# Consultar estadísticas PvP de Hypixel (solo lectura)

## Qué hace
- Nueva página: `/estadisticas/pvp/hypixel/` con búsqueda por nombre.
- Datos reales por modo: Bed Wars, SkyWars y Duels. `—` indica que un dato no está disponible.
- No toca la base SQLite ni los cuatro ABM. No guarda historial ni hace consultas automáticas.
- Esta aplicación no está afiliada a Hypixel.

## Instalación
1. Guardá primero el código actual con Git. No subas claves privadas ni db.sqlite3.
2. Desde `Minecraft_Stats_Hub_Django`, descomprimí el ZIP.
3. Ejecutá `python INSTALAR_PVP_HYPIXEL.py` para añadir la ruta y el enlace al menú; revisá `git diff`.
4. Ejecutá `python manage.py check` y `python manage.py test stats`.
5. Iniciá Django y abrí `/estadisticas/pvp/hypixel/`.

## Configurar clave de Hypixel
Hypixel requiere una aplicación registrada y clave de API. Leé sus políticas en
https://developer.hypixel.net/policies y solicitá una clave autorizada en
https://developer.hypixel.net/create/.

Guardá la clave en **GitHub → Codespaces → Secrets** con el nombre `HYPIXEL_API_KEY`.
Reiniciá el Codespace o una terminal nueva tras configurar el secreto.
**No compartas la clave en el chat, ni la agregues a settings.py, Git o un ZIP.**

Sin clave, la página se muestra con una explicación y NO intenta consultas privadas.
Hypixel prohíbe el seguimiento continuo de estadísticas PvP; esta integración solo consulta cuando el visitante busca un jugador, con caché de 10 min y límites aplicables de API.

## Cómo guardar en Git
Desde la carpeta del repositorio: `git status`. Revisá y usá `git add` solo sobre los archivos nuevos `stats/hypixel_pvp.py`, `stats/test_hypixel_pvp.py`, `templates/estadisticas/hypixel_pvp.html`, `static/css/hypixel_pvp.css`, `stats/urls.py`, `templates/index.html` y esta documentación.
