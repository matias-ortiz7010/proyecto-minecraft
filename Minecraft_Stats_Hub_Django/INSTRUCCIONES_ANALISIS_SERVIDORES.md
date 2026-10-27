# Minecraft Stats Hub – Estadísticas de servidores

## Qué incluye

- Vista pública `/estadisticas/servidores/` con filtros por servidor y períodos de 6, 24, 72 y 168 horas.
- Máximo, mínimo y promedio calculados solo a partir de snapshots online.
- Gráfico Chart.js con puntos reales guardados en SQLite (no se inventan datos).
- Tabla de las últimas 12 mediciones; si faltan datos, se explica cómo obtenerlos.
- Enlace «Estadísticas» en el menú de las pantallas de gestión y «Ver historial y gráficos» en ABM Servidores.
- Seis pruebas automáticas (`stats.test_analitica_servidores`).

## Instalación en Codespaces

Hacé Commit y Push del avance anterior. Detené Django (`Ctrl+C`), subí el ZIP a `Minecraft_Stats_Hub_Django/`, y ejecutá:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
unzip -o Minecraft_Stats_Hub_Analisis_Servidores.zip -d .
python manage.py check
python manage.py test stats
python manage.py runserver 0.0.0.0:8000
```

Abrí el puerto 8000 y entrá a `/estadisticas/servidores/`.

**No hace falta migrar ni ejecutar seed_demo**. El ZIP no incluye `db.sqlite3`, `settings.py` ni `templates/index.html` (que estaba modificado localmente en tu último `git status`).

El gráfico utiliza Chart.js desde un CDN. Si el navegador no tiene acceso, sigue disponible la tabla de mediciones.

## Recolectar datos

En otra terminal, con Django encendido:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
python manage.py actualizar_servidores --continuo
```

El comando consulta los servidores cada 5 minutos mientras Codespaces esté activo. Si solo se ha tomado una muestra, el gráfico tendrá un punto: no significa un error. Los valores guardados en la base de datos del Codespace no viajan al repositorio cuando hacés push.

## Guardar en GitHub

En una tercera terminal, desde `/workspaces/proyecto-minecraft`:

```bash
git add Minecraft_Stats_Hub_Django/stats/analitica_servidores.py Minecraft_Stats_Hub_Django/stats/test_analitica_servidores.py Minecraft_Stats_Hub_Django/stats/urls.py Minecraft_Stats_Hub_Django/templates/estadisticas/servidores.html Minecraft_Stats_Hub_Django/templates/gestion/base_gestion.html Minecraft_Stats_Hub_Django/templates/gestion/servidores/lista.html Minecraft_Stats_Hub_Django/static/css/estadisticas_servidores.css Minecraft_Stats_Hub_Django/static/js/estadisticas_servidores.js Minecraft_Stats_Hub_Django/INSTRUCCIONES_ANALISIS_SERVIDORES.md
git status
git commit -m "Agregar estadísticas históricas de servidores"
git push origin main
```

No incluyas ZIPs, `db.sqlite3` ni credenciales.
