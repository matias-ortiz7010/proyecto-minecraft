ACTUALIZACIÓN DEL INICIO DE MINECRAFT STATS HUB
===============================================

Incluye solamente:
  templates/index.html
  static/css/home_dashboard.css

No reemplaza db.sqlite3, las imágenes, el backend, las APIs, ni los cuatro ABM.

REQUISITO: la ruta Django `stats:estadisticas_servidores` debe existir.
Es parte de la actualización de Análisis de Servidores que instalaste.

INSTALACIÓN EN CODESPACES
-------------------------
1. Dejar guardados en GitHub los avances previos, si hay cambios sin confirmar.
2. Detener Django con Ctrl+C en su terminal.
3. Colocar este ZIP dentro de la carpeta Minecraft_Stats_Hub_Django.
4. En esa carpeta ejecutar:
   unzip -o Minecraft_Stats_Hub_Mejora_Inicio.zip -d .
5. Comprobar:
   python manage.py check
   python manage.py test stats
6. Arrancar Django si estaba detenido:
   python manage.py runserver 0.0.0.0:8000
7. Abrir el puerto 8000 y refrescar con Ctrl+F5.

NOTAS
-----
- Los datos se siguen obteniendo de las mismas variables de Django y las APIs ya existentes.
- No se inventan rankings oficiales ni estados en tiempo real.
- La etiqueta de actualización muestra cuándo el navegador consultó Django, NO cuándo la API externa verificó el servidor.
- Los datos de base de datos SQLite no se sincronizan con GitHub; conservá el Codespace.
- El JavaScript `static/js/app.js` anterior sigue funcionando porque conservamos los IDs requeridos.
- Si Django muestra NoReverseMatch para `stats:estadisticas_servidores`, falta instalar o recuperar el módulo de análisis.
- Si al descomprimir pregunta por reemplazos, el ZIP modifica exclusivamente la plantilla de inicio y agrega su CSS.
