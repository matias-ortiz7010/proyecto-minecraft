# Actualización de navegación — Minecraft Stats Hub

Esta actualización corrige un problema de navegación. La opción **Estadísticas** del menú principal ahora baja a una sección con tres accesos claros: **Servidores**, **Speedruns reales** y **Mods reales**. También se agregaron botones visibles en las secciones Speedrun y Mods y enlaces en la página de estadísticas de servidores.

## Requisitos previos

Haber instalado las actualizaciones de Speedruns externos (speedrun.com) y Mods externos (Modrinth), y haber probado que funcionan cuando se escriben sus URLs directamente. La actualización emplea las rutas Django `stats:estadisticas_servidores`, `stats:speedruns_externos` y `stats:mods_externos`.

## Instalación en Codespaces

1. Subí el ZIP a `Minecraft_Stats_Hub_Django`.
2. En la Terminal 3, parate en esa carpeta y ejecutá `unzip -o Minecraft_Stats_Hub_Navegacion_Estadisticas.zip -d .`.
3. Ejecutá `python manage.py check` y `python manage.py test stats`.
4. Si Django ya está ejecutándose, dejalo activo; si ves los botones anteriores, recargá con Ctrl+F5.
5. Entrá en el inicio y tocá **Estadísticas** del menú. Verás las tres opciones. Probá también los botones en Speedrun, Mods y Estadísticas de Servidores.

## Archivos modificados

- `templates/index.html`
- `templates/estadisticas/servidores.html`
- `static/css/home_dashboard.css`
- `static/css/estadisticas_servidores.css`

No incluye `db.sqlite3`, migraciones, `settings.py`, APIs, ni código de ABM. No hace falta ejecutar `migrate` ni `seed_demo`. El ZIP reemplaza estos cuatro archivos de presentación: si realizaste otras ediciones manuales en ellos, guardalas primero.

## Guardado en GitHub

Desde la raíz del repositorio, agregá **solamente** estos cuatro archivos y las instrucciones, revisá `git status` y luego hacé commit/push. No agregues ZIPs ni `db.sqlite3`.
