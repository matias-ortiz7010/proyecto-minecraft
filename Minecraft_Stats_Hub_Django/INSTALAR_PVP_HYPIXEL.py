"""Instalador idempotente de ruta y enlace. Correr desde donde está manage.py."""
from pathlib import Path

urls = Path('stats/urls.py')
if not urls.exists() or not Path('manage.py').exists():
    raise SystemExit('ERROR: Ejecutá este script desde Minecraft_Stats_Hub_Django.')
original = urls.read_text(encoding='utf-8')
modificado = original
if 'estadisticas_pvp_hypixel' not in modificado:
    linea = 'from .hypixel_pvp import estadisticas_pvp_hypixel\n'
    pos = modificado.find('urlpatterns = [')
    if pos < 0:
        raise SystemExit('ERROR: No se encontró urlpatterns en stats/urls.py')
    modificado = modificado[:pos] + linea + '\n' + modificado[pos:]
if 'name="hypixel_pvp"' not in modificado:
    marcador = 'urlpatterns = ['
    modificado = modificado.replace(marcador, marcador + '\n    path("estadisticas/pvp/hypixel/", estadisticas_pvp_hypixel, name="hypixel_pvp"),', 1)
if modificado != original:
    urls.write_text(modificado, encoding='utf-8')
    print('Se agregó la ruta /estadisticas/pvp/hypixel/')
else:
    print('La ruta ya estaba configurada.')
index = Path('templates/index.html')
if index.exists():
    original = index.read_text(encoding='utf-8')
    if "'stats:hypixel_pvp'" not in original:
        marcador = '</nav>'
        enlace = '''      <a href="{% url 'stats:hypixel_pvp' %}">PvP Hypixel</a>\n'''
        if marcador in original:
            index.write_text(original.replace(marcador, enlace + marcador, 1), encoding='utf-8')
            print('Se agregó un enlace al menú principal.')
        else:
            print('No se encontró </nav>; agregá el enlace manualmente.')
print('Listo. Ejecutá python manage.py check.')
