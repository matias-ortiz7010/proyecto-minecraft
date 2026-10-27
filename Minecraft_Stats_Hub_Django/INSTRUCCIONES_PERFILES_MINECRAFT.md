# Minecraft Stats Hub — Perfiles reales de Minecraft Java

Agrega una nueva sección pública de **solo lectura** en `/estadisticas/jugadores/`, usando las APIs públicas de Minecraft. Esta actualización NO modifica `db.sqlite3`, migraciones, modelos de Django, el ABM de Jugadores ni sus datos. Tampoco altera el buscador local ya existente.

## Lo que muestra

- Nombre oficial actual y UUID desde `https://api.minecraftservices.com/minecraft/profile/lookup/name/<nombre>`.
- Textura opcional desde `https://sessionserver.mojang.com/session/minecraft/profile/<uuid>`.
- Avatar y render del personaje por `https://crafatar.com` (servicio externo, con caché).
- No muestra datos PvP globales: Minecraft Java no ofrece esas estadísticas para todo servidor.
- Si la API no responde, se informa de un problema temporal **sin afirmar que la cuenta no existe**.

## Antes de instalar

Esta actualización parte del proyecto después de instalar **Navegación de Estadísticas** y **Mods Reales Modrinth**. Usa `git status` para comprobar si hay cambios personales antes de sobrescribir `stats/urls.py`, `templates/index.html` o `static/css/home_dashboard.css`. Si los hay, guardalos con commit o una copia; no borres nada.

## Instalación en la Terminal 3 de Codespaces

1. Arrastrá `Minecraft_Stats_Hub_Perfiles_Reales_Jugadores.zip` a `Minecraft_Stats_Hub_Django`.
2. Ejecutá:

```bash
cd /workspaces/proyecto-minecraft/Minecraft_Stats_Hub_Django
unzip -o Minecraft_Stats_Hub_Perfiles_Reales_Jugadores.zip -d .
python manage.py check
python manage.py test stats
```

3. En el navegador visitá `/estadisticas/jugadores/`, buscá `jeb_`, `Dream` o una cuenta Java que conozcas. También hay un enlace en Estadísticas y Buscar jugador del inicio.
4. Si tenés Django ejecutándose en la Terminal 1, normalmente recarga los archivos Python automáticamente; reiniciá si fuese necesario. Usá `Ctrl+F5` si el navegador tiene CSS anterior.

No hace falta `migrate`, crear superusuario ni volver a ejecutar `seed_demo`. **Esta página no agrega jugadores al ABM**.

## Guardar en GitHub después de probar

```bash
cd /workspaces/proyecto-minecraft
git add Minecraft_Stats_Hub_Django/stats/urls.py Minecraft_Stats_Hub_Django/stats/perfiles_minecraft.py Minecraft_Stats_Hub_Django/stats/test_perfiles_minecraft.py Minecraft_Stats_Hub_Django/templates/index.html Minecraft_Stats_Hub_Django/templates/estadisticas/perfiles_minecraft.html Minecraft_Stats_Hub_Django/static/css/home_dashboard.css Minecraft_Stats_Hub_Django/static/css/perfiles_minecraft.css Minecraft_Stats_Hub_Django/INSTRUCCIONES_PERFILES_MINECRAFT.md
git status
git commit -m "Agregar consulta de perfiles reales de Minecraft Java"
git push origin main
```

**No uses `git add .`** porque en el Codespace hay ZIPs viejos que no queremos incluir. No subas `db.sqlite3`, `.env` ni credenciales.

## Fuentes técnicas

- https://minecraft.wiki/w/Mojang_API
- https://crafatar.com/

La respuesta se guarda por 10 minutos en la caché de Django para reducir solicitudes. Crafatar tiene caché propia, y ambas APIs pueden fallar o limitar consultas. El render y la textura, si están disponibles, corresponden a fuentes externas: no se descargan ni almacenan en Django.
