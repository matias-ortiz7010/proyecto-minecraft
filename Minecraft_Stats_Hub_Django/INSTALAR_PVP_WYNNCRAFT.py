"""Reemplaza los accesos de Hypixel por Wynncraft sin sobrescribir los ABM.

Ejecutar SOLO desde Minecraft_Stats_Hub_Django (carpeta de manage.py).
Puede correrse más de una vez: no duplica rutas ni tarjetas.
"""
from pathlib import Path
import re
import shutil

raiz = Path.cwd()
urls = raiz / 'stats/urls.py'
index = raiz / 'templates/index.html'
local = raiz / 'templates/estadisticas/pvp_local.html'
css = raiz / 'static/css/home_dashboard.css'
backup = raiz / '.wynncraft_backup'

if not (raiz / 'manage.py').is_file() or not urls.is_file():
    raise SystemExit('ERROR: Entrá primero a la carpeta Minecraft_Stats_Hub_Django, donde está manage.py.')
if not (raiz / 'stats/wynncraft_pvp.py').is_file() or not (raiz / 'templates/estadisticas/wynncraft_pvp.html').is_file():
    raise SystemExit('ERROR: Descomprimí primero Minecraft_Stats_Hub_PvP_Wynncraft.zip en esta carpeta.')

source = urls.read_text(encoding='utf-8')
if 'urlpatterns = [' not in source:
    raise SystemExit('ERROR: No encuentro urlpatterns en stats/urls.py. No hice cambios.')

# Preparamos todas las modificaciones antes de escribir ninguna.
new_urls = source
import_stmt = 'from .wynncraft_pvp import wynncraft_pvp, redireccion_pvp_hypixel'
if import_stmt not in new_urls:
    new_urls = new_urls.replace('urlpatterns = [', import_stmt + '\n\nurlpatterns = [', 1)
if 'name="wynncraft_pvp"' not in new_urls and "name='wynncraft_pvp'" not in new_urls:
    new_urls = new_urls.replace('urlpatterns = [', 'urlpatterns = [\n    path("estadisticas/pvp/wynncraft/", wynncraft_pvp, name="wynncraft_pvp"),', 1)

legacy_pattern = re.compile(r'''(path\(\s*["']estadisticas/pvp/hypixel/["']\s*,\s*)([A-Za-z_]\w*)(\s*,\s*name\s*=\s*["']hypixel_pvp["']\s*\))''')
found = legacy_pattern.search(new_urls)
if found:
    # Cambia solamente la función de vista, manteniendo la URL y el nombre antiguos.
    new_urls = legacy_pattern.sub(lambda m: m.group(1) + 'redireccion_pvp_hypixel' + m.group(3), new_urls, count=1)
elif 'name="hypixel_pvp"' not in new_urls and "name='hypixel_pvp'" not in new_urls:
    new_urls = new_urls.replace('urlpatterns = [', 'urlpatterns = [\n    path("estadisticas/pvp/hypixel/", redireccion_pvp_hypixel, name="hypixel_pvp"),', 1)
else:
    raise SystemExit('ERROR: El formato de la ruta Hypixel es diferente. No modifiqué ningún archivo.')

new_index = None
if index.is_file():
    old_index = index.read_text(encoding='utf-8')
    def reescribir_anchor(match):
        a = match.group(0)
        if "stats:hypixel_pvp" not in a:
            return a
        a = a.replace('stats:hypixel_pvp', 'stats:wynncraft_pvp')
        a = a.replace('PvP Hypixel', 'PvP Wynncraft').replace('PvP real en Hypixel', 'PvP real en Wynncraft')
        a = a.replace('Bed Wars, SkyWars y Duels por jugador (requiere API key)', 'Kills, muertes y ratio K/D públicos de Wynncraft, sin clave')
        a = a.replace('Requiere clave de API', 'No necesita clave de API')
        return a
    new_index = re.sub(r'<a\b[^>]*>[\s\S]*?</a>', reescribir_anchor, old_index)
    # Si se había omitido la tarjeta de Hypixel, agregamos acceso a Wynncraft.
    if 'stats:wynncraft_pvp' not in new_index and '<div class="home-stats-links">' in new_index:
        tarjeta = '''\n        <!-- MSH_PVP_WYNNCRAFT -->
        <a class="home-stats-link" href="{% url 'stats:wynncraft_pvp' %}">
          <span class="home-stats-icon" aria-hidden="true">⚔️</span>
          <strong>PvP Wynncraft</strong>
          <small>Kills, muertes y ratio K/D públicos de Wynncraft · Sin clave API</small>
          <span class="home-stats-cta">Consultar PvP real ↗</span>
        </a>'''
        new_index = new_index.replace('<div class="home-stats-links">', '<div class="home-stats-links">' + tarjeta, 1)
    if "stats:wynncraft_pvp" not in new_index:
        print('AVISO: No localicé la navegación del inicio; la URL de Wynncraft funcionará igualmente.')
else:
    old_index = None
    print('AVISO: No existe templates/index.html; no se modificará el menú.')

new_local = None
if local.is_file():
    old_local = local.read_text(encoding='utf-8')
    new_local = old_local.replace('href="/estadisticas/pvp/hypixel/">PvP Hypixel', 'href="{% url \'stats:wynncraft_pvp\' %}">PvP Wynncraft')

modificaciones = [(urls, source, new_urls)]
if old_index is not None:
    modificaciones.append((index, old_index, new_index))
if new_local is not None:
    modificaciones.append((local, old_local, new_local))

pendientes = [(ruta, anterior, nuevo) for ruta, anterior, nuevo in modificaciones if anterior != nuevo]
if pendientes:
    backup.mkdir(exist_ok=True)
    for ruta, _, _ in pendientes:
        copia = backup / ruta.relative_to(raiz)
        copia.parent.mkdir(parents=True, exist_ok=True)
        if not copia.exists():
            shutil.copy2(ruta, copia)
    for ruta, _, nuevo in pendientes:
        ruta.write_text(nuevo, encoding='utf-8')
        print('OK: actualicé ' + str(ruta.relative_to(raiz)))
else:
    print('OK: rutas y enlaces ya estaban configurados.')
print('Listo: /estadisticas/pvp/wynncraft/')
print('La ruta anterior /estadisticas/pvp/hypixel/ ahora redirige a Wynncraft.')
print('Copias previas de archivos editados: .wynncraft_backup/ (no las subas a Git).')
print('Siguiente: python manage.py check && python manage.py test stats')
