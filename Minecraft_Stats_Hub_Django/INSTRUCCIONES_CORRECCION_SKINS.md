# Corrección de skins de jugadores Minecraft

Esta actualización **sustituye la visualización de Crafatar**. Antes podía aparecer la skin de Alex/Steve para jugadores cuya skin no se conseguía cargar.

Ahora Django obtiene el nombre/UUID como antes, consulta la textura publicada por Mojang y sirve el PNG desde su propia ruta (proxy restringido al dominio de texturas de Mojang). Un pequeño script JavaScript dibuja en el navegador la **vista frontal 2D de la textura original** (cara, cuerpo, brazos, piernas y segunda capa). Evita reemplazar una textura desconocida por Alex.

## Instalación

Desde la carpeta `Minecraft_Stats_Hub_Django` en la **Terminal 3**:

```bash
unzip -o Minecraft_Stats_Hub_Correccion_Skins_Jugadores.zip -d .
python manage.py check
python manage.py test stats
```

Si la Terminal 1 ya ejecuta Django, se recarga automáticamente al cambiar el Python; si no, iniciá: `python manage.py runserver 0.0.0.0:8000`.

Luego abrí `/estadisticas/jugadores/?nombre=Dream` y recargá con **Ctrl+F5**. Probá también `jeb_` y otro nombre.

## Cambios

- `stats/perfiles_minecraft.py`: nueva consulta y proxy de PNGs de `textures.minecraft.net` restringido a hash hex válido.
- `templates/estadisticas/perfiles_minecraft.html`: lienzos HTML5 para cara y cuerpo, sin imágenes predeterminadas ajenas.
- `static/js/skin_minecraft.js`: representación 2D de la textura oficial (no es un render 3D).
- `static/css/perfiles_minecraft.css`: ajustes visuales.
- `stats/test_perfiles_minecraft.py`: pruebas actualizadas.

No modifica `stats/urls.py`, `settings.py`, `templates/index.html`, los ABM, las otras APIs ni `db.sqlite3`. **No requiere migraciones.**

## Limitaciones

- Mojang puede devolver una skin predeterminada auténtica si el jugador no tiene personalizada.
- Si Mojang no responde, aparecerá «No se pudo verificar la skin» y no Alex de forma engañosa.
- Algunas skins antiguas de 64x32 se dibujan con brazos/piernas simétricos; las de 64x64 usan las capas frontales de la textura.
- La caché del perfil dura diez minutos para respuestas verificadas y 90 segundos en caso de fallo. Si cambió la skin, repetí la consulta más tarde.
- La API pública consulta cuentas **Minecraft Java Edition**, no Bedrock.
