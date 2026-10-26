# Actualización: ABM de Jugadores

Esta versión agrega un sistema ABM propio para jugadores.

## Rutas

- Listado/consulta: `/gestion/jugadores/`
- Alta: `/gestion/jugadores/nuevo/`
- Modificación: desde **Editar**
- Baja: desde **Eliminar**

## Codespaces

Parado en la carpeta donde está `manage.py`:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

No se modificaron los modelos de base de datos, por lo que esta actualización no necesita una migración nueva. `migrate` sigue siendo seguro para verificar que todo esté al día.

## Importante

Si ya tenías `db.sqlite3` creado en tu Codespace, podés conservarlo: el ABM utilizará esos mismos datos.
