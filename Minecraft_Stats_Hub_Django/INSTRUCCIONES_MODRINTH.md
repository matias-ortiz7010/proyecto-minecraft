# Actualización: consulta pública de mods de Modrinth

Proyecto: Minecraft Stats Hub (Django, GitHub Codespaces)

## Qué incluye
- `stats/modrinth_externos.py`: consultas solo lectura a `https://api.modrinth.com/v2`, con User-Agent identificador, filtros validados, límite de descarga de respuesta y caché 5 minutos.
- `stats/urls.py`: mantiene todos los ABM, speedruns externos y estadísticas de servidores; agrega rutas de Modrinth.
- `templates/index.html`: conserva la página de inicio anterior y agrega un enlace bajo la sección Mods.
- `templates/estadisticas/modrinth_base.html`, `mods_externos.html`, `mod_detalle.html`: pantallas públicas de búsqueda y versiones.
- `static/css/modrinth_externos.css`: estilos verde y negro.
- `stats/test_modrinth_externos.py`: pruebas sin conexión real a la API.

## Instalación en Codespaces
1. Si hay modificaciones sin guardar en `templates/index.html` o `stats/urls.py`, guardalas primero con Git, porque esta actualización reemplaza esos dos archivos.
2. En Codespaces, detené solo Django (terminal 1) con Ctrl+C. Podés dejar corriendo el actualizador de servidores (terminal 2).
3. Subí el ZIP dentro de `Minecraft_Stats_Hub_Django`.
4. En la terminal 3:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
unzip -o Minecraft_Stats_Hub_Mods_Reales_Modrinth.zip -d .
python manage.py check
python manage.py test stats
```

5. En terminal 1, iniciá Django si está apagado:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
python manage.py runserver 0.0.0.0:8000
```

6. Abrí `/estadisticas/mods/` o el enlace de la sección Mods en Inicio. Probá buscar Sodium y filtrar por versión de Minecraft y por Fabric.
7. Para ver versiones concretas, abrí `Ver versiones` de un mod. No se necesita ejecutar migraciones ni `seed_demo`.

## Fuente y límites
API documentada: https://docs.modrinth.com/api/operations/searchprojects/ y https://docs.modrinth.com/api/operations/getprojectversions/.
El catálogo externo y tus mods manuales están separados. Las descargas son las publicadas por Modrinth y no constituyen descargas actuales en tiempo real. Cache: 5 minutos.
Si la API falla o rate-limita, se muestra un aviso. Ninguna vista de este módulo escribe en SQLite.

## Guardar en GitHub
En la raíz del repositorio:

```bash
cd /workspaces/proyecto-minecraft
git status
git add Minecraft_Stats_Hub_Django/stats/modrinth_externos.py Minecraft_Stats_Hub_Django/stats/test_modrinth_externos.py Minecraft_Stats_Hub_Django/stats/urls.py Minecraft_Stats_Hub_Django/templates/index.html Minecraft_Stats_Hub_Django/templates/estadisticas/modrinth_base.html Minecraft_Stats_Hub_Django/templates/estadisticas/mods_externos.html Minecraft_Stats_Hub_Django/templates/estadisticas/mod_detalle.html Minecraft_Stats_Hub_Django/static/css/modrinth_externos.css Minecraft_Stats_Hub_Django/INSTRUCCIONES_MODRINTH.md
git status
git commit -m "Agregar consulta de mods reales con Modrinth"
git push origin main
```

**No uses `git add .`**, así evitamos subir ZIPs de actualizaciones. No subas `db.sqlite3` ni secretos.
