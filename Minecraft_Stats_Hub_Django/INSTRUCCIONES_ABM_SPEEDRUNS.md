# Actualización ABM de Speedruns — Minecraft Stats Hub

## Requisitos

- Partí del proyecto que ya tiene los ABM de Jugadores, Servidores y Mods.
- Esta actualización no incluye `db.sqlite3`, `models.py` ni `settings.py`: no cambia la base de datos, tu configuración de Codespaces ni tus imágenes.
- Los speedruns se asocian a jugadores existentes. El tiempo se ingresa como `mm:ss` o `mm:ss.mmm` y se guarda como milisegundos enteros (`tiempo_ms`).

## Instalación en Codespaces

1. Antes de actualizar, guardá en GitHub los cambios del ABM de Mods y comprobá con `git status`.
2. Detené Django con `Ctrl + C`.
3. Subí el ZIP dentro de `Minecraft_Stats_Hub_Django/`.
4. Dentro de esa carpeta, ejecutá:

```bash
unzip -l Minecraft_Stats_Hub_Actualizacion_ABM_Speedruns.zip
unzip -o Minecraft_Stats_Hub_Actualizacion_ABM_Speedruns.zip -d .
rm Minecraft_Stats_Hub_Actualizacion_ABM_Speedruns.zip
python manage.py check
python manage.py test stats
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

5. Entrá a `/gestion/speedruns/`. Probá agregar una speedrun con jugador existente, tiempo `06:50.123`, editar, buscar y eliminar.

## Datos y límites

- Estos datos son manuales; "verificado" es una marca local, NO una verificación oficial.
- Para comparar récords, hay que considerar categoría y reglas, versión y origen de los datos.
- Los enlaces de fuente se guardan, pero no se descargan ni verifican automáticamente.
- La instalación no necesita nuevas migraciones: el modelo `Speedrun` ya existía.
- **Seguridad:** mantené privado el puerto 8000 de Codespaces. Actualmente los ABM no están protegidos con login; hay que agregar autenticación y permisos antes de publicar la página.

## Para guardar los cambios en GitHub

Desde la raíz del repositorio:

```bash
git add Minecraft_Stats_Hub_Django/stats/ Minecraft_Stats_Hub_Django/templates/ Minecraft_Stats_Hub_Django/INSTRUCCIONES_ABM_SPEEDRUNS.md
git status
git commit -m "Agregar ABM de speedruns"
git push origin main
```

No incluyas `db.sqlite3`, `.env`, ni `__pycache__` en Git.
