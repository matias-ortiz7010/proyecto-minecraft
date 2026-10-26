# Actualización ABM Servidores — Minecraft Stats Hub

Esta actualización agrega la gestión de **Servidores** y conserva el ABM de Jugadores.

## Instalación en GitHub Codespaces

1. Parar `runserver` con Ctrl+C.
2. Desde la carpeta `Minecraft_Stats_Hub_Django`, subir este ZIP (sin extraer).
3. Descomprimirlo encima del código existente:

   ```bash
   unzip -o Minecraft_Stats_Hub_Actualizacion_ABM_Servidores.zip -d .
   ```

4. Comprobar e iniciar Django:

   ```bash
   python manage.py check
   python manage.py test stats
   python manage.py migrate
   python manage.py runserver 0.0.0.0:8000
   ```

5. Abrir `/gestion/servidores/` desde la URL del puerto 8000.

## Qué incluye

- Alta, baja, modificación, consulta y búsqueda de servidores.
- Validación de IP/dominio único (ya definida en el modelo existente).
- Confirmación de baja por POST con token CSRF.
- Avisos de éxito, acceso desde el menú, pruebas automáticas.

## Qué NO cambia

- **No incluye** `settings.py` (conserva tu arreglo de CSRF para Codespaces).
- **No incluye** `db.sqlite3` (no borra jugadores ni servidores).
- **No modifica** `models.py` (no requiere nuevas migraciones).
- Estado y jugadores conectados son **manuales**, no es un monitoreo en vivo todavía.

## Precauciones

- Hacé un commit previo o guarda una copia antes de sobrescribir archivos.
- Usá puertos privados en Codespaces: estos formularios todavía no exigen login.
- Los archivos `.pyc`, `__pycache__` y `db.sqlite3` deben seguir excluidos del repositorio.
- La base SQLite vive en el Codespace, por lo que no se restaura con `git clone`.
- Si los archivos de tu Codespace fueron editados después de la última versión ABM, revisá las diferencias antes de reemplazarlos.
