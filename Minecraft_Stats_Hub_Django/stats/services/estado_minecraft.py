"""Consultas del estado de servidores Minecraft Java con verificación cruzada.

La respuesta negativa de una sola API no se toma como prueba definitiva
porque algunos servidores/proxies pueden fallar temporalmente al responder al ping.
"""
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class EstadoMinecraftError(Exception):
    """Estado no verificable: mantener datos guardados sin sobrescribirlos."""


_RE_DIRECCION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,250}(?::[0-9]{1,5})?$")
_UA = "MinecraftStatsHub/1.0 (educational project; github.com/matias-ortiz7010/proyecto-minecraft)"


def _obtener_json(url):
    req = Request(url, headers={"User-Agent": _UA, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=8) as response:
            contenido = json.load(response)
    except (OSError, URLError, HTTPError, TimeoutError, ValueError) as exc:
        raise EstadoMinecraftError("No se pudo consultar la API") from exc
    if not isinstance(contenido, dict) or type(contenido.get("online")) is not bool:
        raise EstadoMinecraftError("La API devolvió un formato inesperado")
    return contenido


def _interpretar(contenido):
    online = contenido["online"]
    if not online:
        return {"online": False, "jugadores": 0, "version": None}
    players = contenido.get("players")
    jugadores = players.get("online") if isinstance(players, dict) else None
    if type(jugadores) is not int or jugadores < 0:
        raise EstadoMinecraftError("La API no devolvió un contador de jugadores válido")
    version = contenido.get("version")
    if isinstance(version, dict):
        version = version.get("name")
    return {"online": True, "jugadores": jugadores,
            "version": version if isinstance(version, str) else None}


def consultar_estado(direccion):
    direccion = direccion.strip()
    if not _RE_DIRECCION.fullmatch(direccion) or ".." in direccion:
        raise EstadoMinecraftError("Dirección inválida; ingresá host o host:puerto, sin http://")
    if ":" in direccion:
        puerto = int(direccion.rsplit(":", 1)[1])
        if not 1 <= puerto <= 65535:
            raise EstadoMinecraftError("Puerto inválido")

    host = quote(direccion, safe=".:_-")
    primaria = "https://api.mcsrvstat.us/3/" + host
    secundaria = "https://api.mcstatus.io/v2/status/java/" + host

    try:
        estado_a = _interpretar(_obtener_json(primaria))
    except EstadoMinecraftError:
        # Si la primera falla, aceptamos una lectura ONLINE de la alternativa.
        # Una lectura OFFLINE sola no alcanza para anotar una caída.
        estado_b = _interpretar(_obtener_json(secundaria))
        if estado_b["online"]:
            return estado_b
        raise EstadoMinecraftError("La primera API falló y la segunda no confirmó que esté online")

    if estado_a["online"]:
        return estado_a

    # Una respuesta offline aislada podría ser un falso negativo.
    # Requerimos confirmación independiente para guardar OFFLINE/0.
    try:
        estado_b = _interpretar(_obtener_json(secundaria))
    except EstadoMinecraftError as exc:
        raise EstadoMinecraftError(
            "Primera API informó offline, segunda no disponible; no se sobreescriben datos"
        ) from exc
    return estado_b  # Online si B detecta el servidor, Offline solo si las dos coinciden.
