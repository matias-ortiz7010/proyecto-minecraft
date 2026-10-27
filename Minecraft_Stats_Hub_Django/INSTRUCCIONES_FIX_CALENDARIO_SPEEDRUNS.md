# Reparación del campo de fecha: calendario (Speedruns)

**Problema:** el selector anterior mostraba el año al revés, con opciones 1, 2, 3... y era incómodo elegir la fecha.

**Solución:** botón **Calendario** con mini calendario de lunes a domingo, botones de mes anterior/siguiente y selectores de mes y **año real** (2009, 2010, 2011..., 2026...). Al hacer clic en un día, se escribe automáticamente `DD/MM/AAAA` en el campo de fecha. También podés escribirlo manualmente. Al editar un speedrun, la fecha anterior aparece precargada. Botones **Hoy**, **Limpiar** (fecha opcional) y **Cerrar**. Django valida la fecha al guardar.

## Instalación en GitHub Codespaces

**Antes de instalar:** si tenés otros cambios sin guardar, hacé commit/push para tener una copia del código anterior. NO elimines la base de datos.

1. Detené Django con `Ctrl + C`.
2. Subí `Minecraft_Stats_Hub_Fix_Calendario_Speedruns.zip` dentro de `Minecraft_Stats_Hub_Django`.
3. En la terminal:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
unzip -o Minecraft_Stats_Hub_Fix_Calendario_Speedruns.zip -d .
python manage.py check
python manage.py test stats
python manage.py runserver 0.0.0.0:8000
```

4. Volvé a `/gestion/speedruns/4/editar/` (o editá otro speedrun), recargá con `Ctrl+F5` y tocá **Calendario**.
5. Elegí, por ejemplo, 26 de octubre de 2026, guardá y comprobá que se muestre `26/10/2026`. Probá también crear un registro y limpiar la fecha.
6. Cuando ande, **guardá el avance en GitHub**:

```bash
cd /workspaces/proyecto-minecraft
git status
git add Minecraft_Stats_Hub_Django/stats/forms.py Minecraft_Stats_Hub_Django/stats/tests.py Minecraft_Stats_Hub_Django/stats/test_fecha_speedrun.py Minecraft_Stats_Hub_Django/templates/gestion/speedruns/form.html Minecraft_Stats_Hub_Django/static/css/speedrun_calendar.css Minecraft_Stats_Hub_Django/static/js/speedrun_calendar.js Minecraft_Stats_Hub_Django/INSTRUCCIONES_FIX_CALENDARIO_SPEEDRUNS.md
git commit -m "Corregir fecha de speedruns con mini calendario"
git push origin main
```

Este ZIP **no contiene** ni altera `db.sqlite3`, `settings.py`, `models.py`, las imágenes, ni los otros ABM. No necesita migraciones.
El campo de fecha sigue siendo opcional; el calendario es interfaz y la validación se hace en Django.
