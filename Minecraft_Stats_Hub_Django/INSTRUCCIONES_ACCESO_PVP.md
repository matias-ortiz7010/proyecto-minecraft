# Minecraft Stats Hub – Tarjeta PvP Hypixel en Estadísticas

Esta corrección **no reemplaza archivos existentes**: `INSTALAR_TARJETA_PVP.py` edita tu propio `templates/index.html` y añade una regla a `static/css/home_dashboard.css`. Se puede ejecutar dos veces sin duplicar los botones. **No toca SQLite, modelos ni el login.**

## Instalación en GitHub Codespaces

1. Subí el ZIP a la carpeta que contiene `manage.py` (Minecraft_Stats_Hub_Django).
2. En la Terminal 3:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
unzip -o Minecraft_Stats_Hub_Acceso_PvP_Estadisticas.zip -d .
python INSTALAR_TARJETA_PVP.py
python manage.py check
python manage.py test stats
```

3. Volvé al sitio, recargá con `Ctrl + F5` y tocá Estadísticas: debe aparecer **PvP Hypixel**. La sección PvP de la portada también tendrá un botón.

## Por qué puede aparecer «HYPIXEL_API_KEY»

Este aviso no es un fallo del diseño. La ruta `/estadisticas/pvp/hypixel/` está instalada, pero la API oficial exige una clave autorizada. Solicitá una desde https://developer.hypixel.net/create/ (puede requerir aprobación). No compartas la clave.

En GitHub, abrí **Settings → Codespaces → Codespaces secrets → New secret**, asigná nombre `HYPIXEL_API_KEY`, colocá la clave en el campo seguro **Value** y elegí acceso al repositorio `proyecto-minecraft`. Detené y reiniciá el Codespace para que la variable esté disponible y volvé a encender Django y el actualizador de servidores. Según el tipo de aplicación, Hypixel puede exigir aprobación antes de habilitar consultas.

Para verificar que el secreto existe, sin mostrarlo, podés ejecutar:

```bash
python -c 'import os; print("Configurada" if os.getenv("HYPIXEL_API_KEY") else "No configurada")'
```

## Antes del commit

Desde `/workspaces/proyecto-minecraft`, ejecutá `git diff -- Minecraft_Stats_Hub_Django/templates/index.html Minecraft_Stats_Hub_Django/static/css/home_dashboard.css`. Revisá y subí solo los archivos modificados de código. Evitá subir ZIP, `.env`, claves, `db.sqlite3` o la carpeta `__pycache__`.
