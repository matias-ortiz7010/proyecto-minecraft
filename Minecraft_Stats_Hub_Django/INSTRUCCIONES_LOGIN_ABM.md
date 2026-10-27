# Minecraft Stats Hub — Login seguro para los ABM

Esta actualización **no** incluye `db.sqlite3`, `settings.py`, modelos ni migraciones. Conserva los ABM existentes y el mini calendario de Speedruns.

## ¿Qué cambia?

- Página pública (`/`) y APIs JSON: siguen accesibles sin entrar.
- Los cuatro ABM (`/gestion/jugadores/`, `/gestion/servidores/`, `/gestion/mods/`, `/gestion/speedruns/`) requieren iniciar sesión con un usuario **staff** de Django.
- Las rutas de agregar, editar y eliminar también están protegidas del lado del servidor (no solo ocultamos botones).
- Página de acceso: `/gestion/ingresar/`. Salir con el botón `Salir`, por formulario POST y CSRF.
- No se alteran los modelos, las fechas ni las estadísticas.

## Instalar en GitHub Codespaces

**Antes de actualizar** confirmá que tus cambios actuales están guardados (`git status`, Commit y Push). Con Django detenido:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
unzip -o Minecraft_Stats_Hub_Actualizacion_Login_ABM.zip -d .
rm Minecraft_Stats_Hub_Actualizacion_Login_ABM.zip
python manage.py check
python manage.py test stats
```

Si Django señala migraciones pendientes, ejecutá `python manage.py migrate`. Esta actualización no requiere migraciones propias.

## Crear usuario administrador (una vez)

```bash
python manage.py createsuperuser
```

Elegí un nombre y contraseña robusta. La contraseña **no se sube a GitHub** y se guarda en Django dentro de tu `db.sqlite3` local. No me envíes la contraseña. Si ya creaste un superusuario antes, usá ese y omití el comando.

Arrancar servidor:

```bash
python manage.py runserver 0.0.0.0:8000
```

Entrá al sitio, tocá **Administración** y luego **Ingresar**. Después de autenticarte vas a poder usar los cuatro ABM. Usá el botón **Salir** para terminar la sesión.

## Prueba rápida de seguridad

1. En ventana privada entrá a `/gestion/jugadores/nuevo/`: debe pedir login.
2. Iniciá sesión con el superusuario, entrá al ABM y probá abrir un registro.
3. Tocá Salir y volvé a intentar abrir `/gestion/mods/`: debe pedir login.
4. Verificá que la web principal siga siendo pública.

## Guardar en GitHub

```bash
cd /workspaces/proyecto-minecraft
git status
git add Minecraft_Stats_Hub_Django/stats/ Minecraft_Stats_Hub_Django/templates/ Minecraft_Stats_Hub_Django/static/css/ Minecraft_Stats_Hub_Django/INSTRUCCIONES_LOGIN_ABM.md
git commit -m "Proteger ABM con login de administradores"
git push origin main
```

Antes de hacer Commit, revisá que no aparezca `db.sqlite3` ni `.env` en `git status`. Mantené el puerto 8000 privado durante el desarrollo y no publiques un servidor Django con `DEBUG=True`.
