# Corrección definitiva de fecha — ABM Speedruns

## Qué cambia
Se cambia la fecha de Speedruns por **tres menús desplegables: Día, Mes y Año**. Esto evita tener que escribir la fecha en el campo `type=date` del navegador. En Edición, los valores previos aparecen seleccionados, y al guardar se conserva en el campo `fecha` de SQLite. Es opcional y permite dejar las tres casillas vacías.

Esta actualización modifica `stats/forms.py`, `stats/tests.py` (actualiza pruebas anteriores del campo de fecha) y `templates/gestion/speedruns/form.html`; suma pruebas en `stats/test_fecha_speedrun.py`. No reemplaza `db.sqlite3`, `settings.py`, imágenes ni otros modelos. **No requiere migraciones.**

## Instalar en GitHub Codespaces
1. Antes de reemplazar código, comprobá/guardá cambios previos con git y detené Django con `Ctrl+C`.
2. Subí el ZIP a `Minecraft_Stats_Hub_Django`.
3. En la terminal:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
unzip -o Minecraft_Stats_Hub_Fix_Fecha_Selectores.zip -d .
python manage.py check
python manage.py test stats
python manage.py runserver 0.0.0.0:8000
```

4. Recargá la página con `Ctrl+F5` para evitar caché y entrá en `/gestion/speedruns/nuevo/` o Editar un speedrun existente. Deben aparecer TRES selectores de fecha. Probá `26` / `Octubre` / `2026`.

Si al actualizar ves todavía el calendario anterior, revisá que el ZIP se haya extraído dentro de la misma carpeta que tiene `manage.py` y que estés usando el puerto correcto. Verificá con:

```bash
python manage.py shell -c "from stats.forms import SpeedrunForm; print(SpeedrunForm()['fecha'])"
```

La salida debe contener `fecha_day`, `fecha_month` y `fecha_year`.

La actualización incluye los tests originales ajustados para la nueva interfaz, y también tests adicionales en `stats/test_fecha_speedrun.py`.
