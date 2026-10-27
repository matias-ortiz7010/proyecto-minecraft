"""Perfiles públicos de Minecraft Java y visualización fiel de su textura.

No guarda jugadores ni toca los ABM. La textura proviene únicamente de Mojang.
"""
import base64
import binascii
import json
import re
import struct
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from django.core.cache import cache
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET

NOMBRE_RE = re.compile(r'^[A-Za-z0-9_]{1,16}$')
UUID_RE = re.compile(r'^[0-9a-fA-F]{32}$')
TEXTURA_RE = re.compile(r'^/texture/([0-9a-fA-F]{32,128})$')
TIMEOUT = 7
MAX_PNG = 1024 * 1024  # Las skins normales pesan muchísimo menos.


class JugadorNoEncontrado(Exception):
    """La API confirma que ese nombre no tiene un perfil público."""


class PerfilNoDisponible(Exception):
    """La consulta externa falló temporalmente."""


def solicitar_json(url):
    """Se llama sólo con URLs de API conocidas construidas por el servidor."""
    req = Request(url, headers={
        'User-Agent': 'MinecraftStatsHub/1.1 (perfiles-publicos-educativos)',
        'Accept': 'application/json',
    })
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            if response.status == 204:
                raise JugadorNoEncontrado()
            contenido = response.read(131073)
        if len(contenido) > 131072:
            raise PerfilNoDisponible('La API devolvió demasiados datos.')
        return json.loads(contenido.decode('utf-8'))
    except HTTPError as error:
        if error.code in (404, 204):
            raise JugadorNoEncontrado() from error
        raise PerfilNoDisponible('La API de Minecraft no respondió correctamente.') from error
    except (URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PerfilNoDisponible('No se pudo conectar con la API de Minecraft.') from error


def _url_textura(url):
    """Rechaza URLs ajenas a la CDN de texturas de Mojang."""
    if not isinstance(url, str):
        return ''
    parsed = urlparse(url)
    if (parsed.scheme not in ('https', 'http')
            or parsed.netloc.lower() != 'textures.minecraft.net'
            or not TEXTURA_RE.fullmatch(parsed.path)
            or parsed.query or parsed.fragment or parsed.username or parsed.password):
        return ''
    return 'https://textures.minecraft.net' + parsed.path


def obtener_texturas(uuid):
    """Distingue entre una skin real, una skin predeterminada y una consulta fallida."""
    try:
        session = solicitar_json('https://sessionserver.mojang.com/session/minecraft/profile/' + uuid)
        if not isinstance(session, dict):
            raise PerfilNoDisponible('Respuesta inesperada.')
        properties = session.get('properties', [])
        if not isinstance(properties, list):
            raise PerfilNoDisponible('Respuesta inesperada.')
        for item in properties:
            if not isinstance(item, dict) or item.get('name') != 'textures':
                continue
            encoded = item.get('value', '')
            if not isinstance(encoded, str) or len(encoded) > 131072:
                raise PerfilNoDisponible('Contenido de texturas incorrecto.')
            decoded = json.loads(base64.b64decode(encoded, validate=True).decode('utf-8'))
            if not isinstance(decoded, dict):
                raise PerfilNoDisponible('Contenido de texturas incorrecto.')
            textures = decoded.get('textures', {})
            if not isinstance(textures, dict):
                raise PerfilNoDisponible('Contenido de texturas incorrecto.')
            skin = textures.get('SKIN') or {}
            cape = textures.get('CAPE') or {}
            skin_url = _url_textura(skin.get('url')) if isinstance(skin, dict) else ''
            cape_url = _url_textura(cape.get('url')) if isinstance(cape, dict) else ''
            metadata = (skin.get('metadata') or {}) if isinstance(skin, dict) else {}
            if not isinstance(metadata, dict):
                metadata = {}
            return {
                'skin_url': skin_url,
                'skin_hash': skin_url.rsplit('/', 1)[-1] if skin_url else '',
                'cape_url': cape_url,
                'modelo': 'Slim (brazos finos)' if metadata.get('model') == 'slim' else 'Clásico (brazos anchos)' if skin_url else 'Predeterminado',
                'estado_skin': 'personalizada' if skin_url else 'predeterminada',
            }
        return {'estado_skin': 'predeterminada', 'modelo': 'Predeterminado'}
    except (JugadorNoEncontrado, PerfilNoDisponible, ValueError, KeyError, TypeError,
            UnicodeDecodeError, json.JSONDecodeError, binascii.Error):
        # No afirmar "no tiene skin": también puede ser un error de Mojang.
        return {'estado_skin': 'no_verificada', 'modelo': 'No se pudo comprobar'}


def consultar_perfil(nombre):
    nombre = (nombre or '').strip()
    if not NOMBRE_RE.fullmatch(nombre):
        raise ValueError('El nombre debe tener entre 1 y 16 caracteres: letras, números o guion bajo.')
    key = 'msh:java-perfil:v2:' + nombre.lower()  # v2 evita reutilizar el caché de Crafatar.
    existente = cache.get(key)
    if existente is not None:
        return existente
    data = solicitar_json('https://api.minecraftservices.com/minecraft/profile/lookup/name/' + quote(nombre, safe=''))
    if not isinstance(data, dict):
        raise PerfilNoDisponible('La respuesta del servicio no es válida.')
    uuid = data.get('id', '')
    oficial = data.get('name', '')
    if not isinstance(uuid, str) or not UUID_RE.fullmatch(uuid):
        raise PerfilNoDisponible('La API devolvió un UUID incorrecto.')
    if not isinstance(oficial, str) or not NOMBRE_RE.fullmatch(oficial):
        raise PerfilNoDisponible('La API devolvió un nombre incorrecto.')
    uuid = uuid.lower()
    perfil = {
        'nombre': oficial,
        'uuid': uuid,
        'uuid_formato': f'{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}',
        'skin_url': '', 'skin_hash': '', 'cape_url': '',
        'modelo': 'No se pudo comprobar', 'estado_skin': 'no_verificada',
    }
    perfil.update(obtener_texturas(uuid))
    # Una falla de texturas se vuelve a intentar antes.
    cache.set(key, perfil, timeout=90 if perfil['estado_skin'] == 'no_verificada' else 600)
    return perfil


def obtener_png_skin(hash_textura):
    """Descarga SOLO PNGs de Mojang para que Canvas los lea sin depender de CORS.

    No se acepta una URL remota proporcionada por el usuario.
    """
    if not TEXTURA_RE.fullmatch('/texture/' + hash_textura):
        raise ValueError('Identificador de textura incorrecto.')
    hash_textura = hash_textura.lower()
    key = 'msh:skin-png:v1:' + hash_textura
    previo = cache.get(key)
    if previo is not None:
        return previo
    req = Request('https://textures.minecraft.net/texture/' + hash_textura,
                  headers={'User-Agent': 'MinecraftStatsHub/1.1', 'Accept': 'image/png'})
    try:
        with urlopen(req, timeout=TIMEOUT) as res:
            data = res.read(MAX_PNG + 1)
    except (URLError, HTTPError, TimeoutError, OSError) as error:
        raise PerfilNoDisponible('La textura no está disponible.') from error
    if len(data) > MAX_PNG or len(data) < 24 or not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise PerfilNoDisponible('La textura descargada no es un PNG válido.')
    width, height = struct.unpack('>II', data[16:24])
    if width != 64 or height not in (32, 64):
        raise PerfilNoDisponible('El tamaño de la textura no es compatible.')
    cache.set(key, data, timeout=600)
    return data


@require_GET
def perfiles_minecraft(request):
    # Endpoint de imagen, sólo como proxy fijo hacia la CDN oficial de Mojang.
    if 'skin' in request.GET:
        hash_textura = request.GET.get('skin', '')
        if not TEXTURA_RE.fullmatch('/texture/' + hash_textura):
            return HttpResponseBadRequest('Identificador de textura no válido.')
        try:
            contenido = obtener_png_skin(hash_textura)
        except (PerfilNoDisponible, ValueError):
            return HttpResponse(status=503)
        respuesta = HttpResponse(contenido, content_type='image/png')
        respuesta['Cache-Control'] = 'public, max-age=600'
        respuesta['X-Content-Type-Options'] = 'nosniff'
        return respuesta

    nombre = request.GET.get('nombre', '').strip()
    perfil = None
    mensaje = ''
    if nombre:
        try:
            perfil = consultar_perfil(nombre)
        except JugadorNoEncontrado:
            mensaje = 'No se encontró una cuenta Java Edition con ese nombre.'
        except ValueError as error:
            mensaje = str(error)
        except PerfilNoDisponible:
            mensaje = 'El servicio de perfiles no está disponible. Probá de nuevo más tarde.'
    return render(request, 'estadisticas/perfiles_minecraft.html', {
        'nombre_buscado': nombre[:40], 'perfil': perfil, 'mensaje': mensaje,
    })
