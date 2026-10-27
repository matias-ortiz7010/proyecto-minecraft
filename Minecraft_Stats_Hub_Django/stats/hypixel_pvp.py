"""Consulta puntual de PvP en Hypixel, solo lectura.

No guarda estadísticas externas en SQLite ni modifica los ABM. No hacer polling.
La clave debe ser entregada a la app en Codespaces Secrets como HYPIXEL_API_KEY.
"""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.core.cache import cache
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .perfiles_minecraft import (NOMBRE_RE, consultar_perfil, JugadorNoEncontrado,
                                  PerfilNoDisponible)

API_BASE = 'https://api.hypixel.net/v2/player'
TIMEOUT = 8
MAX_BYTES = 1024 * 1024
MODOS = (
    ('Bed Wars', 'Bedwars', {'victorias': 'wins_bedwars', 'derrotas': 'losses_bedwars', 'kills': 'kills_bedwars', 'final_kills': 'final_kills_bedwars'}),
    ('SkyWars', 'SkyWars', {'victorias': 'wins', 'derrotas': 'losses', 'kills': 'kills'}),
    ('Duels', 'Duels', {'victorias': 'wins', 'derrotas': 'losses', 'kills': 'kills'}),
)

class HypixelNoDisponible(Exception):
    pass

class HypixelClaveIncorrecta(Exception):
    pass

class HypixelSinCupo(Exception):
    pass


def _valor_no_negativo(data, campo):
    v = data.get(campo)
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
        return None
    return int(v)


def resumir_stats(data):
    """Extrae estadísticas generales por modo sin mezclar modalidades."""
    stats = (data or {}).get('stats') or {}
    if not isinstance(stats, dict):
        stats = {}
    res = []
    for nombre, clave, campos in MODOS:
        valores = stats.get(clave)
        if not isinstance(valores, dict) or not valores:
            res.append({'nombre': nombre, 'disponible': False, 'campos': []})
            continue
        filas = [{'nombre': etiqueta.replace('_', ' ').capitalize(), 'valor': _valor_no_negativo(valores, campo)} for etiqueta, campo in campos.items()]
        res.append({'nombre': nombre, 'disponible': True, 'campos': filas})
    return res


def consultar_hypixel(uuid, clave):
    cache_key = 'msh:hypixel-pvp:v1:' + uuid.lower()
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    url = API_BASE + '?' + urlencode({'uuid': uuid})
    req = Request(url, headers={'API-Key': clave, 'User-Agent': 'MinecraftStatsHub/1.0 (academic-site)', 'Accept': 'application/json'})
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            payload = response.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise HypixelNoDisponible('La respuesta fue demasiado grande.')
        data = json.loads(payload.decode('utf-8'))
    except HTTPError as e:
        if e.code in (401, 403):
            raise HypixelClaveIncorrecta() from e
        if e.code == 429:
            raise HypixelSinCupo() from e
        raise HypixelNoDisponible() from e
    except (URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise HypixelNoDisponible() from e
    if not isinstance(data, dict) or data.get('success') is not True:
        raise HypixelNoDisponible()
    player = data.get('player')
    resultado = {'encontrado': isinstance(player, dict), 'modos': resumir_stats(player) if isinstance(player, dict) else []}
    cache.set(cache_key, resultado, timeout=600 if resultado['encontrado'] else 120)
    return resultado


@require_GET
def estadisticas_pvp_hypixel(request):
    nombre = request.GET.get('nombre', '').strip()
    contexto = {'nombre': nombre[:40], 'datos': None, 'perfil': None, 'mensaje': ''}
    api_key = os.environ.get('HYPIXEL_API_KEY', '').strip()
    if not api_key:
        contexto['mensaje'] = 'Las estadísticas de Hypixel requieren configurar HYPIXEL_API_KEY en los secretos de Codespaces. La búsqueda de perfiles públicos sigue disponible.'
    elif nombre:
        if not NOMBRE_RE.fullmatch(nombre):
            contexto['mensaje'] = 'Ingresá un nombre válido de Minecraft Java (1 a 16 letras, números o _).'
        else:
            try:
                perfil = consultar_perfil(nombre)
                contexto['perfil'] = perfil
                resultado = consultar_hypixel(perfil['uuid'], api_key)
                if resultado['encontrado']:
                    contexto['datos'] = resultado['modos']
                else:
                    contexto['mensaje'] = 'Hypixel no devolvió datos públicos para este jugador.'
            except JugadorNoEncontrado:
                contexto['mensaje'] = 'No existe una cuenta Minecraft Java con ese nombre.'
            except PerfilNoDisponible:
                contexto['mensaje'] = 'No se pudo verificar el jugador con Minecraft. Probá más tarde.'
            except HypixelClaveIncorrecta:
                contexto['mensaje'] = 'Hypixel rechazó la clave de API. Revisala en los secretos de Codespaces.'
            except HypixelSinCupo:
                contexto['mensaje'] = 'Se alcanzó temporalmente el límite de solicitudes de Hypixel.'
            except HypixelNoDisponible:
                contexto['mensaje'] = 'No se pudieron consultar las estadísticas de Hypixel. Probá más tarde.'
    return render(request, 'estadisticas/hypixel_pvp.html', contexto)
