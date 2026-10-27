"""Consulta pública de clasificaciones de speedrun.com, sin cambiar el ABM ni SQLite.

Se recuperan datos de la API v1 de speedrun.com. Los parámetros externos siempre
se construyen usando identificadores validados de categorías/variables devueltos
por la API, no desde URLs arbitrarias ingresadas por visitantes.
"""
import json
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from django.core.cache import cache
from django.shortcuts import render

BASE_API = 'https://www.speedrun.com/api/v1'
BASE_WEB = 'https://www.speedrun.com/mc'
AGENTE = 'MinecraftStatsHub/1.1 (proyecto educativo; consulta publica)'
MAX_BYTES = 3_000_000
IDENTIFICADOR = re.compile(r'^[a-zA-Z0-9_-]{1,32}$')


class FuenteNoDisponible(Exception):
    """La API remota no puede usarse en este momento."""


def solicitar_json(ruta, parametros=None, ttl=180):
    """Caché breve; URL fija en speedrun.com; solicitudes de solo lectura."""
    parametros = parametros or {}
    url = BASE_API + ruta
    if parametros:
        url += '?' + urlencode(parametros)
    llave = 'src:v1:' + url
    cacheado = cache.get(llave)
    if cacheado is not None:
        return cacheado
    req = Request(url, headers={'User-Agent': AGENTE, 'Accept': 'application/json'})
    try:
        with urlopen(req, timeout=9) as respuesta:
            contenido = respuesta.read(MAX_BYTES + 1)
        if len(contenido) > MAX_BYTES:
            raise FuenteNoDisponible('La respuesta de la API fue demasiado grande.')
        resultado = json.loads(contenido.decode('utf-8'))
        if not isinstance(resultado, dict) or 'data' not in resultado:
            raise FuenteNoDisponible('La API devolvió una respuesta inesperada.')
    except (HTTPError, URLError, TimeoutError, UnicodeDecodeError, ValueError, OSError) as exc:
        raise FuenteNoDisponible('No se pudo consultar speedrun.com. Probá de nuevo más tarde.') from exc
    cache.set(llave, resultado['data'], ttl)
    return resultado['data']


def categorias_mc():
    data = solicitar_json('/games/mc/categories', ttl=1800)
    if not isinstance(data, list):
        raise FuenteNoDisponible('No se pudieron interpretar las categorías de speedrun.com.')
    categorias = []
    for c in data:
        if not isinstance(c, dict) or c.get('type') != 'per-game':
            continue
        if IDENTIFICADOR.fullmatch(str(c.get('id', ''))):
            categorias.append({'id': c['id'], 'nombre': str(c.get('name', 'Categoría'))[:100]})
    if not categorias:
        raise FuenteNoDisponible('No hay categorías completas disponibles en la API.')
    return categorias


def variables_categoria(categoria):
    data = solicitar_json('/categories/' + categoria + '/variables', ttl=1800)
    if not isinstance(data, list):
        return []
    variables = []
    for v in data:
        if not isinstance(v, dict) or not IDENTIFICADOR.fullmatch(str(v.get('id', ''))):
            continue
        datos_valores = v.get('values', {})
        if not isinstance(datos_valores, dict):
            continue
        opciones = []
        for vid, item in (datos_valores.get('values') or {}).items():
            if not IDENTIFICADOR.fullmatch(str(vid)):
                continue
            etiqueta = item.get('label', vid) if isinstance(item, dict) else str(item)
            opciones.append({'id': vid, 'nombre': str(etiqueta)[:90]})
        if opciones:
            variables.append({
                'id': v['id'], 'nombre': str(v.get('name', 'Filtro'))[:90],
                'opciones': opciones,
                'seleccionado': '',
            })
    return variables


def formato_tiempo(segundos):
    try:
        x = Decimal(str(segundos))
        if not x.is_finite() or x < 0:
            return '—'
        milis = int((x * 1000).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError, TypeError):
        return '—'
    horas, rem = divmod(milis, 3_600_000)
    minutos, rem = divmod(rem, 60_000)
    secs, resto = divmod(rem, 1000)
    if horas:
        return f'{horas}:{minutos:02d}:{secs:02d}.{resto:03d}'
    return f'{minutos:02d}:{secs:02d}.{resto:03d}'


def _nombre_jugadores(run, directorio):
    nombres = []
    for item in run.get('players', []):
        if not isinstance(item, dict):
            continue
        if item.get('rel') == 'guest':
            nombre = item.get('name', 'Invitado')
        else:
            nombre = directorio.get(item.get('id'), item.get('id', 'Usuario sin nombre'))
        nombres.append(str(nombre)[:70])
    return ' / '.join(nombres) if nombres else 'Sin nombre público'


def _url_fuente(url):
    if not isinstance(url, str):
        return ''
    parsed = urlsplit(url)
    if parsed.scheme == 'https' and parsed.hostname in ('www.speedrun.com', 'speedrun.com'):
        return url
    return ''


def procesar_tabla(tabla, variables):
    """El JSON público no se guarda en la BD; presenta jugadores, tiempo y reglas."""
    if not isinstance(tabla, dict):
        raise FuenteNoDisponible('Formato de clasificación inesperado.')
    jugadores_embebidos = tabla.get('players', {})
    if isinstance(jugadores_embebidos, dict):
        jugadores_embebidos = jugadores_embebidos.get('data', [])
    if not isinstance(jugadores_embebidos, list):
        jugadores_embebidos = []
    directorio = {}
    for u in jugadores_embebidos:
        if not isinstance(u, dict) or not u.get('id'):
            continue
        nombres = u.get('names') or {}
        nombre = nombres.get('international') if isinstance(nombres, dict) else None
        directorio[u['id']] = str(nombre or u.get('name') or u['id'])[:70]
    etiquetas = {}
    for v in variables:
        etiquetas[v['id']] = {o['id']: o['nombre'] for o in v['opciones']}
    registros = []
    for fila in tabla.get('runs', [])[:30]:
        if not isinstance(fila, dict):
            continue
        run = fila.get('run') or {}
        if not isinstance(run, dict):
            continue
        # No hacer pasar una run rechazada/en espera por récord verificado.
        estado = (run.get('status') or {}).get('status')
        if estado and estado != 'verified':
            continue
        valor_t = (run.get('times') or {}).get('primary_t')
        notas = []
        for key, value in (run.get('values') or {}).items():
            label = etiquetas.get(key, {}).get(value)
            if label:
                notas.append(label)
        posicion = fila.get('place')
        registros.append({
            'puesto': posicion if isinstance(posicion, int) else '—',
            'jugador': _nombre_jugadores(run, directorio),
            'tiempo': formato_tiempo(valor_t),
            'fecha': str(run.get('date') or '—')[:20],
            'detalles': ', '.join(notas[:4]) or 'Sin detalles',
            'url': _url_fuente(run.get('weblink')),
        })
    return registros


def speedruns_externos(request):
    """Solo GET; no requiere login; no escribe jugadores ni speedruns locales."""
    contexto = {
        'categorias': [], 'categoria_id': '', 'categoria_nombre': '',
        'variables': [], 'registros': [], 'error': '', 'filtrado': False,
        'url_origen': BASE_WEB,
    }
    try:
        categorias = categorias_mc()
        elegida = request.GET.get('categoria', '')
        ids = {c['id'] for c in categorias}
        if elegida not in ids:
            preferida = next((c for c in categorias if c['nombre'].casefold() == 'any% glitchless'), None)
            elegida = (preferida or categorias[0])['id']
        nombre = next(c['nombre'] for c in categorias if c['id'] == elegida)
        variables = variables_categoria(elegida)
        filtros = {}
        for variable in variables:
            val = request.GET.get('var_' + variable['id'], '')
            if any(o['id'] == val for o in variable['opciones']):
                filtros['var-' + variable['id']] = val
                variable['seleccionado'] = val
        params = {'top': 15, 'embed': 'players', 'timing': 'ingame'}
        params.update(filtros)
        datos = solicitar_json('/leaderboards/mc/category/' + elegida, params, ttl=180)
        contexto.update({
            'categorias': categorias, 'categoria_id': elegida,
            'categoria_nombre': nombre, 'variables': variables,
            'registros': procesar_tabla(datos, variables),
            'filtrado': bool(filtros),
            'url_origen': _url_fuente(datos.get('weblink', '')) or BASE_WEB,
        })
    except FuenteNoDisponible as error:
        contexto['error'] = str(error)
    return render(request, 'estadisticas/speedruns_externos.html', contexto)
