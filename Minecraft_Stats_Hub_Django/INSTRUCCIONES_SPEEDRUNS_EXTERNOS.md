# Minecraft Stats Hub — datos externos de Speedruns (consulta, no importación)

Esta actualización crea una **página de consulta de speedruns publicados en speedrun.com**:

- `/estadisticas/speedruns/` (pública, de solo lectura)
- Selector de categoría y variables (versión/semilla/reglas, según la API)
- Jugadores, tiempos, fecha y enlaces a los registros públicos
- Enlace desde la sección Speedrun de la página principal

**No importa registros a SQLite**, no crea jugadores ni modifica el ABM existente, no requiere migraciones y no cambia el login. La API externa puede fallar o limitar consultas; si eso ocurre, se muestra un aviso y un enlace a la fuente. Los datos se almacenan temporalmente en la caché de Django (3 minutos, categorías 30 minutos) para reducir solicitudes.

Se consultan las rutas documentadas de la API v1:
- `GET https://www.speedrun.com/api/v1/games/mc/categories`
- `GET https://www.speedrun.com/api/v1/categories/<id>/variables`
- `GET https://www.speedrun.com/api/v1/leaderboards/mc/category/<id>?top=15&embed=players&timing=ingame`

Fuentes:
- https://github.com/speedruncomorg/api/blob/master/version1/leaderboards.md
- https://github.com/speedruncomorg/api/blob/master/version1/games.md
- https://www.speedrun.com/mc

## Instalar en Codespaces

1. Recomendado: comprobá antes con `git status` que no haya ediciones sin guardar; hacé commit si corresponde.
2. Detené **solamente Django** (`Ctrl + C` en la primera terminal). Dejá libre la tercera terminal para instalar.
3. Copiá `Minecraft_Stats_Hub_Speedruns_Reales_Solo_Lectura.zip` a `Minecraft_Stats_Hub_Django`.
4. En la tercera terminal:

   ```bash
   cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
   unzip -o Minecraft_Stats_Hub_Speedruns_Reales_Solo_Lectura.zip -d .
   python manage.py check
   python manage.py test stats
   ```

5. En la primera terminal:

   ```bash
   cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
   python manage.py runserver 0.0.0.0:8000
   ```

6. Abrí `https://TU-CODESPACE-8000.app.github.dev/estadisticas/speedruns/`

## Guardar los cambios en GitHub

Desde `/workspaces/proyecto-minecraft`:

```bash
git add Minecraft_Stats_Hub_Django/stats/urls.py \
  Minecraft_Stats_Hub_Django/stats/speedruns_externos.py \
  Minecraft_Stats_Hub_Django/stats/test_speedruns_externos.py \
  Minecraft_Stats_Hub_Django/templates/index.html \
  Minecraft_Stats_Hub_Django/templates/estadisticas/speedruns_externos.html \
  Minecraft_Stats_Hub_Django/static/css/speedruns_externos.css \
  Minecraft_Stats_Hub_Django/INSTRUCCIONES_SPEEDRUNS_EXTERNOS.md

git status
git commit -m "Agregar consulta externa de speedruns"
git push origin main
```

No subas ZIPs antiguos, ni `db.sqlite3` ni credenciales. Es normal que `git status` muestre ZIPs como archivos sin seguimiento.

## Importante

- Las marcas entre categorías/subcategorías distintas **no** son directamente comparables.
- Las clasificaciones mostradas pertenecen a speedrun.com, no a la base de datos del proyecto.
- Si la API restringe el acceso en Codespaces o cambia su esquema, el sitio principal seguirá funcionando; esta pantalla mostrará un error explícito.
- Si el `index.html` de tu Codespace tiene modificaciones nuevas desde la última versión que compartiste, hacé una copia antes de descomprimir el ZIP.
