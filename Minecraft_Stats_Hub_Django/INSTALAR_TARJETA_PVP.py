'''Inserta PvP Hypixel en el centro de estadísticas sin reemplazar plantillas existentes.
Ejecutar desde el directorio donde está manage.py.
'''
from pathlib import Path
import re

index = Path('templates/index.html')
css = Path('static/css/home_dashboard.css')
if not Path('manage.py').exists() or not index.exists():
    raise SystemExit('ERROR: Entrá a Minecraft_Stats_Hub_Django (la carpeta que contiene manage.py).')

source = index.read_text(encoding='utf-8')
# Importante: el menú global puede contener el enlace aunque falte la tarjeta.
pattern = re.compile(r'(<div\s+class=["\']home-stats-links["\']\s*>)(.*?)(\n\s*</div>)', re.S)
match = pattern.search(source)
if not match:
    raise SystemExit('ERROR: No encontré las tarjetas del centro de estadísticas. No modifiqué archivos.')

updated = source
if "'stats:hypixel_pvp'" not in match.group(2) and '"stats:hypixel_pvp"' not in match.group(2):
    card = '''\n        <a class="home-stats-link" href="{% url 'stats:hypixel_pvp' %}">
          <span class="home-stats-icon" aria-hidden="true">⚔️</span>
          <strong>PvP Hypixel</strong>
          <small>Consultá Bed Wars, SkyWars y Duels por jugador (requiere API key)</small>
          <span class="home-stats-cta">Ver estadísticas PvP ↗</span>
        </a>'''
    updated = updated[:match.end(2)] + card + updated[match.end(2):]
    print('OK: tarjeta PvP Hypixel agregada a Estadísticas.')
else:
    print('OK: la tarjeta PvP Hypixel ya estaba incluida.')

pvp = re.search(r'(<section\b[^>]*\bid=["\']pvp["\'][^>]*>)(.*?)(</section>)', updated, re.S)
if pvp:
    if 'stats:hypixel_pvp' not in pvp.group(2):
        link = '''      <div class="home-source-action">
        <a class="home-primary-link" href="{% url 'stats:hypixel_pvp' %}">⚔️ Consultar PvP real en Hypixel ↗</a>
        <span>Datos externos · No modifica el ABM · Requiere clave de API</span>
      </div>
'''
        updated = updated[:pvp.start(3)] + link + pvp.group(3) + updated[pvp.end(3):]
        print('OK: botón agregado en la sección PvP.')
    else:
        print('OK: botón PvP de sección ya presente.')
else:
    print('AVISO: no encontré la sección #pvp; el acceso de Estadísticas sí se agregó.')

if updated != source:
    index.write_text(updated, encoding='utf-8')

if css.exists():
    original_css = css.read_text(encoding='utf-8')
    marker = '/* MSH PVPH NAV CARD V1 */'
    if marker not in original_css:
        addition = '''\n/* MSH PVPH NAV CARD V1 */
/* Con cinco accesos, distribuimos las tarjetas en 3 + 2 en pantallas anchas. */
@media (min-width: 1050px) {
  .home-stats-hub .home-stats-links { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
'''
        css.write_text(original_css.rstrip() + '\n' + addition, encoding='utf-8')
        print('OK: distribución de las tarjetas ajustada.')
    else:
        print('OK: los estilos ya estaban ajustados.')
else:
    print('AVISO: no encontré home_dashboard.css; los enlaces seguirán funcionando.')

print('Terminado: ejecutá python manage.py check y recargá con Ctrl + F5.')
