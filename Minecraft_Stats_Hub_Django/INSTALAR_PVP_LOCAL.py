# Añade acceso a análisis PvP local; correr desde carpeta con manage.py.
from pathlib import Path
import re

raiz = Path.cwd()
urls = raiz / "stats/urls.py"
index = raiz / "templates/index.html"
if not (raiz / "manage.py").is_file() or not urls.is_file():
    raise SystemExit("ERROR: Iniciá este instalador dentro de Minecraft_Stats_Hub_Django (junto a manage.py).")

contenido = urls.read_text(encoding="utf-8")
if "urlpatterns = [" not in contenido:
    raise SystemExit("ERROR: No se encontró urlpatterns en stats/urls.py. No se modificó ningún archivo.")
actualizado = contenido
if "from .pvp_local import estadisticas_pvp_local" not in actualizado:
    actualizado = actualizado.replace("urlpatterns = [", "from .pvp_local import estadisticas_pvp_local\n\nurlpatterns = [", 1)
if 'name="estadisticas_pvp_local"' not in actualizado:
    actualizado = actualizado.replace("urlpatterns = [", 'urlpatterns = [\n    path("estadisticas/pvp/local/", estadisticas_pvp_local, name="estadisticas_pvp_local"),', 1)
if contenido != actualizado:
    urls.write_text(actualizado, encoding="utf-8")
    print("OK: URL agregada en stats/urls.py")
else:
    print("OK: URL ya estaba configurada")

if index.is_file():
    actual = index.read_text(encoding="utf-8")
    editado = actual
    card = '''        <!-- MSH_PVP_LOCAL_HUB -->
        <a class="home-stats-link" href="{% url 'stats:estadisticas_pvp_local' %}">
          <span class="home-stats-icon" aria-hidden="true">⚔️</span>
          <strong>PvP registrado</strong>
          <small>Ranking y gráficos de tus datos de Django</small>
          <span class="home-stats-cta">Analizar PvP ↗</span>
        </a>
'''
    if "MSH_PVP_LOCAL_HUB" not in editado and '<div class="home-stats-links">' in editado:
        editado = editado.replace('<div class="home-stats-links">', '<div class="home-stats-links">\n' + card, 1)
    action = '''      <!-- MSH_PVP_LOCAL_LINK -->
      <p class="data-note"><a class="inline-link" href="{% url 'stats:estadisticas_pvp_local' %}">⚔️ Ver ranking y gráficos PvP registrados →</a></p>
'''
    if "MSH_PVP_LOCAL_LINK" not in editado:
        match = re.search(r'<section\b[^>]*id=["\']pvp["\'][^>]*>[\s\S]*?</section>', editado)
        if match:
            section = match.group(0)
            editado = editado[:match.start()] + section.replace("</section>", action + "    </section>", 1) + editado[match.end():]
        else:
            print("AVISO: No se encontró #pvp; la nueva página sigue accesible desde su URL")
    if editado != actual:
        index.write_text(editado, encoding="utf-8")
        print("OK: Enlaces añadidos en templates/index.html")
    else:
        print("OK: Enlaces existentes o plantilla distinta; no se sobrescribió")
else:
    print("AVISO: templates/index.html no encontrado; la URL funciona igual")
print("Listo: /estadisticas/pvp/local/. Ejecutá python manage.py check y python manage.py test stats.")
