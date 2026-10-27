# Minecraft Stats Hub — análisis PvP local

Este módulo permite consultar en una página pública los **registros PvP ya guardados en SQLite**, ordenados por victorias, kills o porcentaje de victorias. Incluye filtros, indicadores y gráfico. **No son datos de Hypixel** ni estadísticas oficiales; la API de Hypixel sigue pendiente de la clave autorizada.

## Instalación

1. Antes de actualizar, guardar con Git cualquier cambio propio que quieras conservar.
2. Colocar el ZIP dentro de `Minecraft_Stats_Hub_Django`.
3. Desde la carpeta con `manage.py` ejecutar:

   ```bash
   unzip -o Minecraft_Stats_Hub_Analisis_PvP_Local.zip -d .
   python INSTALAR_PVP_LOCAL.py
   python manage.py check
   python manage.py test stats
   ```

4. Abrir `/estadisticas/pvp/local/`.
5. Comprobar que desde **Estadísticas** o **PvP** aparezca el nuevo enlace. Si no, recargar con Ctrl+F5.

**No ejecutar migraciones**: no se modifica ningún modelo. No se reemplazan `settings.py`, `db.sqlite3`, el resto de ABM, ni las pantallas externas. Este módulo no requiere ni almacena la clave de Hypixel.

## Funcionamiento

- Si faltan datos, muestra un estado vacío (no inventa rankings).
- El orden de % de victorias depende de las partidas registradas; se puede exigir un mínimo de partidas para evitar comparar jugadores con muestras muy pequeñas.
- Usa Chart.js para el gráfico; si su CDN no responde, la tabla y los indicadores siguen disponibles.
- El instalador es idempotente (no duplica enlaces si se ejecuta dos veces).
- `git status` antes de guardar permite verificar que no se suban ZIPs ni la base de datos.

## Reversión

Para revertir el cambio, quitar la importación y la ruta `estadisticas_pvp_local` de `stats/urls.py`, retirar los bloques HTML delimitados con `MSH_PVP_LOCAL_HUB` y `MSH_PVP_LOCAL_LINK` y eliminar `stats/pvp_local.py`, `stats/test_pvp_local.py`, `templates/estadisticas/pvp_local.html`, `static/css/pvp_local.css` y `static/js/pvp_local.js`.
