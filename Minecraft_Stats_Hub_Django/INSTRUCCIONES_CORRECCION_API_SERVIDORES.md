# Corrección: estados falsamente fuera de línea en servidores

Esta actualización cambia el servicio de consulta y agrega pruebas. **No incluye** `db.sqlite3`, `settings.py`, imágenes ni migraciones.

Antes de aplicar, guardá en GitHub el código que ya funciona. Detené los procesos `runserver` y `actualizar_servidores --continuo` con Ctrl+C.

Desde `/workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django`:

```bash
unzip -o Minecraft_Stats_Hub_Correccion_Estado_Servidores.zip -d .
python manage.py check
python manage.py test stats
python manage.py actualizar_servidores
python manage.py runserver 0.0.0.0:8000
```

Si usás actualización continua, iniciá **otra terminal** y ejecutá `python manage.py actualizar_servidores --continuo` para que tome el código nuevo.

## Funcionamiento

1. Si mcsrvstat.us devuelve **online**, se guardan sus datos.
2. Si devuelve **offline**, se comprueba el mismo servidor con mcstatus.io.
3. Si la segunda API confirma **online**, se usan sus datos.
4. Si ambas devuelven **offline**, se registra offline/0. Si la segunda consulta falla, se conservan los valores almacenados.
5. Si la primera API falla, solo se guarda una lectura si la segunda sí confirma online.

Las APIs contienen caché; la respuesta no es instantánea. La pantalla todavía solo muestra online/offline: un estado no verificable conserva el último valor guardado. Esto no equivale a indicar un estado desconocido, lo que requeriría cambios al modelo y a la interfaz.

Estas son APIs para **Minecraft Java Edition**. Si agregás servidores Bedrock, requieren endpoints específicos.

Tras comprobar que funciona, guardá los cambios desde la raíz del repositorio y evitá agregar los ZIP:

```bash
cd /workspaces/proyecto-minecraft
git add Minecraft_Stats_Hub_Django/stats/services/estado_minecraft.py Minecraft_Stats_Hub_Django/stats/test_estado_minecraft_fallback.py Minecraft_Stats_Hub_Django/INSTRUCCIONES_CORRECCION_API_SERVIDORES.md
git commit -m "Verificar estados con dos APIs y evitar falsos offline"
git push origin main
```
