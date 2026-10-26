# Minecraft Stats Hub — versión Django

Esta versión convierte el prototipo HTML/CSS/JS en una aplicación Django sin cambiar la identidad visual principal.

## Qué hace Django acá

- Sirve la página y los assets.
- Guarda jugadores, PvP, speedruns, mods y servidores en una base de datos.
- Expone endpoints JSON para que JavaScript consulte datos sin recargar toda la página.
- Incluye `/admin/` para cargar y editar datos.
- Incluye un modelo `ServidorSnapshot` preparado para guardar historial y hacer análisis más adelante.

> Importante: todavía NO se conectaron APIs externas de Minecraft, speedrun, mods o servidores. Los datos demo son solo de prueba y no deben interpretarse como rankings oficiales.

## 1. Instalar Python y dependencias

Desde la carpeta del proyecto:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Después:

```bash
pip install -r requirements.txt
```

## 2. Crear la base de datos

```bash
python manage.py makemigrations stats
python manage.py migrate
```

## 3. Cargar los datos demo

```bash
python manage.py seed_demo
```

## 4. Crear un usuario administrador

```bash
python manage.py createsuperuser
```

## 5. Ejecutar la web

```bash
python manage.py runserver
```

Abrí en el navegador:

- Sitio: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

## APIs ya preparadas

- `GET /api/jugadores/buscar/?q=Dream`
- `GET /api/resumen/`
- `GET /api/servidores/`
- `GET /api/speedruns/`
- `GET /api/mods/`

## Estructura importante

```text
Minecraft_Stats_Hub_Django/
├── manage.py
├── minecraft_stats_hub/     # configuración principal de Django
├── stats/                    # modelos, vistas, URLs y admin
├── templates/index.html      # tu HTML convertido a template Django
├── static/css/styles.css
├── static/js/app.js
├── static/assets/            # logo, banner y futuras imágenes
└── legacy/schema.sql         # esquema SQL anterior, conservado como referencia
```

## Qué sigue

La siguiente etapa es conectar fuentes reales. Conviene hacerlo de una en una, por ejemplo:

1. Estado y jugadores de servidores.
2. Datos de jugadores/perfiles.
3. Speedruns verificadas.
4. Mods y descargas.
5. Guardar snapshots históricos y crear gráficos/análisis.

Para datos realmente instantáneos se puede agregar Django Channels/WebSockets después. Para la mayoría de estadísticas basta con consultas periódicas a una API y guardar resultados en la base de datos.

### Atajo en Windows

También podés hacer doble clic en `INICIAR_WINDOWS.bat`. El archivo crea el entorno virtual, instala Django, prepara la base y ejecuta el servidor. La primera vez, si querés los ejemplos, abrí otra terminal en la carpeta y ejecutá `python manage.py seed_demo` con el entorno activado.

## ABM de jugadores

Esta versión incorpora un ABM propio (no depende solamente de Django Admin):

- **Consulta/Listado:** `/gestion/jugadores/`
- **Alta:** `/gestion/jugadores/nuevo/`
- **Modificación:** botón **Editar** del listado.
- **Baja:** botón **Eliminar** con pantalla de confirmación.

El ABM trabaja directamente contra el modelo `Jugador` de Django. Si eliminás un jugador, Django también elimina sus datos relacionados con `Speedrun` y `PvP` por las relaciones `CASCADE` definidas en los modelos.

### En GitHub Codespaces

Desde la carpeta que contiene `manage.py`:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Después abrí el puerto 8000 y entrá a **ABM** desde la barra superior de Minecraft Stats Hub.

Para ejecutar las pruebas automáticas del ABM:

```bash
python manage.py test stats
```
