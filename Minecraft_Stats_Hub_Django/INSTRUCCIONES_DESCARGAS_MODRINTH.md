# Minecraft Stats Hub – Descarga directa de mods desde Modrinth

Esta actualización agrega a **Mods reales → Ver versiones** el botón **Descargar archivo** de cada versión. Abre el archivo original alojado en el CDN oficial de Modrinth. No instala ni ejecuta mods, no guarda JAR/ZIP en Django y no modifica SQLite.

## Antes de instalar

Se requiere que ya esté funcionando la actualización **Mods Reales Modrinth**. En Codspaces, usá la terminal libre para la instalación. Primero hacé `git status` para ver si existen cambios tuyos sin guardar y, si los hay, realizá un commit o una copia de seguridad de los archivos que vas a sobrescribir.

## Instalar

1. Descargá `Minecraft_Stats_Hub_Descargas_Mods_Modrinth.zip`.
2. Arrastralo dentro de `Minecraft_Stats_Hub_Django` en Codespaces.
3. En la terminal libre ejecutá:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
unzip -o Minecraft_Stats_Hub_Descargas_Mods_Modrinth.zip -d .
python manage.py check
python manage.py test stats
```

4. Recargá `/estadisticas/mods/` y entrá en **Ver versiones** de un mod. Cada versión con archivo válido tendrá **Descargar archivo** y **Ver versión en Modrinth**.
5. Si aparece el diseño anterior, usá `Ctrl + F5`. Django con `runserver` normalmente recarga automáticamente los archivos Python; reinicialo si no lo hace.

## Seguridad y límites

- Se enlazan únicamente archivos `.jar` o `.zip` del dominio exacto `https://cdn.modrinth.com` bajo `/data/`.
- La URL viene de la versión consultada, no de parámetros del usuario.
- No se descarga nada al servidor ni se guarda en SQLite.
- Si falta un archivo compatible o confiable, se muestra **Consultar en Modrinth** en vez del botón de descarga directa.
- Los mods pueden requerir dependencias o configuraciones específicas; revisá Minecraft/loader y la página del autor.
- Los archivos son de terceros y no los auditamos.

## Archivos que modifica

- `stats/modrinth_externos.py`
- `templates/estadisticas/mod_detalle.html`
- `static/css/modrinth_externos.css`

Agrega `stats/test_modrinth_descargas.py` y estas instrucciones. No toca `urls.py`, el ABM, `settings.py`, `db.sqlite3`, el login ni la página de inicio.

## Guardar en GitHub (después de comprobar)

```bash
cd /workspaces/proyecto-minecraft
git add Minecraft_Stats_Hub_Django/stats/modrinth_externos.py Minecraft_Stats_Hub_Django/stats/test_modrinth_descargas.py Minecraft_Stats_Hub_Django/templates/estadisticas/mod_detalle.html Minecraft_Stats_Hub_Django/static/css/modrinth_externos.css Minecraft_Stats_Hub_Django/INSTRUCCIONES_DESCARGAS_MODRINTH.md
git status
git commit -m "Agregar descarga oficial de mods Modrinth"
git push origin main
```

No subas `db.sqlite3`, `.env` ni los ZIP de actualización.
