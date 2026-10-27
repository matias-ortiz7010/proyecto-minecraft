# Minecraft Stats Hub — PvP real de Wynncraft (sin clave API)

Esta actualización reemplaza el acceso de **PvP Hypixel** por **PvP Wynncraft**.

**Fuente oficial**: https://docs.wynncraft.com/modules/player/get-player  
**API**: `https://api.wynncraft.com/v3/player/<nombre>`  
**Datos disponibles**: `globalData.pvp.kills` y `globalData.pvp.deaths`, cuando el jugador permite su publicación.

- Consulta a Wynncraft sólo cuando el visitante busca un jugador.
- No utiliza clave API, no guarda estadísticas externas en SQLite, y no cambia los cuatro ABM.
- Conserva el análisis **PvP registrado** (local).
- Si el perfil es privado o falta el bloque PvP, muestra «no disponible», nunca cero inventado.
- Aplica caché de 120 segundos para no generar consultas innecesarias.
- Mantiene la antigua ruta `/estadisticas/pvp/hypixel/`, que **redirige** a `/estadisticas/pvp/wynncraft/` para que los marcadores antiguos sigan funcionando.
- No hace falta ejecutar migraciones ni `seed_demo`.

## Instalar desde GitHub Codespaces

1. Descargá `Minecraft_Stats_Hub_PvP_Wynncraft.zip` y subilo a la carpeta `Minecraft_Stats_Hub_Django` (junto a `manage.py`).
2. En la **Terminal 3**:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
ls -l Minecraft_Stats_Hub_PvP_Wynncraft.zip
unzip -o Minecraft_Stats_Hub_PvP_Wynncraft.zip -d .
python INSTALAR_PVP_WYNNCRAFT.py
python manage.py check
python manage.py test stats
```

Si el nombre cambió por una segunda descarga (por ejemplo `... (1).zip`), ajustá el nombre de `unzip` según lo que muestre `ls`.

3. Si Django está encendido, recargá el navegador con `Ctrl + F5`; si no, encendelo en la Terminal 1:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
python manage.py runserver 0.0.0.0:8000
```

4. Abrí `/estadisticas/pvp/wynncraft/` y probá con un usuario que juegue Wynncraft, como `Salted`.

## Atención

Los resultados son **del servidor Wynncraft**, no de Hypixel, ni un ranking PvP global de Minecraft. Algunos perfiles pueden ser privados y otros no haber jugado Wynncraft. La API está sujeta a límites y puede estar momentáneamente inaccesible.

## Guardar en GitHub después de verificar

```bash
cd /workspaces/proyecto-minecraft
git status
```

Prepará sólo los archivos de esta actualización (`stats/wynncraft_pvp.py`, `stats/test_wynncraft_pvp.py`, `stats/urls.py`, `templates/index.html`, `templates/estadisticas/wynncraft_pvp.html`, `templates/estadisticas/pvp_local.html`, `static/css/wynncraft_pvp.css`, `INSTALAR_PVP_WYNNCRAFT.py`, `INSTRUCCIONES_PVP_WYNNCRAFT.md`), siempre que estén modificados. **No subas ZIPs ni la carpeta `.wynncraft_backup/`**. Revisá `git diff --cached` antes de hacer Commit y Push.

## Restauración

El instalador guarda copias de los archivos que modifique en `.wynncraft_backup/`. También podés usar `git diff` para revisar exactamente qué se modificó. No borres tu base de datos ni reemplaces todo el proyecto.
