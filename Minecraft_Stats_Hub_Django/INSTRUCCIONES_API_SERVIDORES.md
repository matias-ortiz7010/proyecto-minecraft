# API real de servidores (mcsrvstat.us v3)

## Instalación
1. Primero confirmá que tu último commit/push esté guardado.
2. Desde `Minecraft_Stats_Hub_Django/`, con Django detenido, descomprimí el ZIP con `unzip -o <archivo>.zip -d .`.
3. Verificá que se agregó `stats/management/commands/actualizar_servidores.py`.
4. Ejecutá `python manage.py check` y `python manage.py test stats`.
5. En la terminal 1: `python manage.py runserver 0.0.0.0:8000`.
6. En una SEGUNDA terminal, ubicada en `Minecraft_Stats_Hub_Django/`:
   - Prueba única: `python manage.py actualizar_servidores`
   - Monitoreo continuo: `python manage.py actualizar_servidores --continuo`.
7. Abrí tu web. La tabla del inicio se consulta a Django cada 30 segundos.

## Datos
- Fuente: https://api.mcsrvstat.us/ (versión 3, Java Edition).
- El proveedor almacena resultados unos cinco minutos. Esto **no es** un contador segundo a segundo.
- Se consulta la IP/dominio registrado en el ABM, no se inventan servidores.
- Cuando una consulta se realiza correctamente, se actualizan `Servidor.online`, `Servidor.jugadores` y se crea un `ServidorSnapshot` para análisis futuros.
- Ante error de red o respuesta inválida, **NO** se marca offline ni se borran números: permanecen datos previos.
- Si agregás un servidor nuevo, empezará a consultarse en el siguiente ciclo.
- La versión se muestra en la terminal; no se almacena porque aún no hay campo de versión en el modelo.
- Si Codespaces se detiene, se pausa el actualizador. No es un servicio de hosting continuo.
- Datos Java Edition solamente; el soporte Bedrock se podrá agregar después.
- La base `db.sqlite3` no está dentro de este ZIP y no se cambia el esquema: **no requiere migraciones**.

## Solución de problemas
- No aparece ningún servidor: agregá una dirección Java válida desde el ABM; no incluya `https://`.
- API no responde: verificar salida de la terminal del actualizador; se conservan los últimos datos.
- Hay valores viejos: iniciar `actualizar_servidores --continuo` en segunda terminal, comprobar que Codespaces está activo.
- Cambios de GitHub: no agregar `db.sqlite3`, `.env` o ZIP de instalación al commit.
