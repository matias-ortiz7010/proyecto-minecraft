# Actualización ABM de Mods — Minecraft Stats Hub

Esta actualización agrega alta, baja, modificación y consulta de **Mods** reutilizando el modelo `Mod` existente.
No incluye ni modifica `db.sqlite3`, `models.py`, `settings.py`, migraciones, imágenes ni `static/css/styles.css`.
Conserva ABM Jugadores y ABM Servidores.

## Aplicar en GitHub Codespaces

1. Detener Django con `Ctrl+C` en la terminal.
2. Subir el archivo `Minecraft_Stats_Hub_Actualizacion_ABM_Mods.zip` dentro de `Minecraft_Stats_Hub_Django`.
3. Ejecutar estos comandos **uno por uno**:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
unzip -o Minecraft_Stats_Hub_Actualizacion_ABM_Mods.zip -d .
rm Minecraft_Stats_Hub_Actualizacion_ABM_Mods.zip
python manage.py check
python manage.py test stats
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

La ruta nueva es `/gestion/mods/`.

**Pruebas manuales:** agregá `ModPrueba` (autor `Prueba`, versión `1.21`, descargas `15`, URL opcional en blanco); editá el nombre a `ModEditado`; buscá el mod; y eliminá solamente ese registro de prueba.

Si todo anda bien, para guardar en GitHub: parás Django (`Ctrl+C`) y desde la raíz del repositorio:

```bash
cd /workspaces/proyecto-minecraft
git add Minecraft_Stats_Hub_Django/stats/ Minecraft_Stats_Hub_Django/templates/ Minecraft_Stats_Hub_Django/INSTRUCCIONES_ABM_MODS.md
git status
git commit -m "Agregar ABM de mods"
git push origin main
```

Comprobá que **no se suban `db.sqlite3`, `.env`, `.pyc` ni ZIPs**.

## Seguridad y datos

La actualización mantiene la configuración de acceso anterior. **Los ABM aún no tienen login propio**, así que mantené el puerto 8000 en visibilidad *Private* en Codespaces y no compartas una URL pública hasta agregar autenticación/autorización.
El número de descargas se ingresa manualmente, no es una estadística en tiempo real.
