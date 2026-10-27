"""Consulta pública PvP de Wynncraft v3 (solo lectura).

No usa API key ni guarda datos en SQLite. Sólo consulta al buscar.
Fuente oficial: https://docs.wynncraft.com/modules/player/get-player
"""
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET

API_BASE = "https://api.wynncraft.com/v3/player/"
NOMBRE_VALIDO = re.compile(r"^[A-Za-z0-9_]{1,16}$")
TIMEOUT = 9
MAX_RESPONSE_BYTES = 1024 * 1024


class WynncraftError(Exception):
    """Error mostrable a la persona usuaria, sin exponer detalles internos."""


def extraer_pvp(payload):
    """Transforma sólo los datos públicos reales de la API v3.

    None significa que la estadística no se publicó. 0 es un dato válido.
    """
    if not isinstance(payload, dict):
        raise WynncraftError("La API devolvió un formato inesperado.")
    global_data = payload.get("globalData")
    pvp = global_data.get("pvp") if isinstance(global_data, dict) else None
    if not isinstance(pvp, dict):
        return {
            "jugador": payload.get("username") or "Jugador",
            "uuid": payload.get("uuid") or "",
            "kills": None,
            "muertes": None,
            "ratio": "—",
            "disponible": False,
            "online": payload.get("online") is True,
        }

    def numero(valor):
        return valor if type(valor) is int and valor >= 0 else None

    kills = numero(pvp.get("kills"))
    muertes = numero(pvp.get("deaths"))
    if kills is None or muertes is None:
        ratio = "—"
        disponible = False
    elif muertes == 0:
        ratio = "∞" if kills > 0 else "—"
        disponible = True
    else:
        ratio = f"{kills / muertes:.2f}".replace(".", ",")
        disponible = True

    return {
        "jugador": payload.get("username") or "Jugador",
        "uuid": payload.get("uuid") or "",
        "kills": kills,
        "muertes": muertes,
        "ratio": ratio,
        "disponible": disponible,
        "online": payload.get("online") is True,
    }


def consultar_jugador(nombre):
    """Consultas bajo demanda con caché breve para respetar límites de Wynncraft."""
    if not NOMBRE_VALIDO.fullmatch(nombre):
        raise WynncraftError("Escribí un nombre válido de Minecraft Java (1 a 16 letras, números o _).")
    llave = "msh:wynncraft:pvp:v1:" + nombre.lower()
    existente = cache.get(llave)
    if existente is not None:
        return existente
    url = API_BASE + quote(nombre, safe="")
    req = Request(url, headers={
        "User-Agent": "MinecraftStatsHub/1.0 (proyecto educativo)",
        "Accept": "application/json",
    })
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise WynncraftError("La respuesta de Wynncraft fue demasiado grande.")
        data = json.loads(raw.decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            raise WynncraftError("No se encontró ese jugador en Wynncraft. Probá con alguien que haya jugado allí.") from exc
        if exc.code == 300:
            raise WynncraftError("Ese nombre corresponde a varios perfiles. Probá consultar con un UUID específico desde Wynncraft.") from exc
        if exc.code == 403:
            raise WynncraftError("Wynncraft no permite consultar ese perfil o algunos datos son privados.") from exc
        if exc.code == 429:
            raise WynncraftError("Wynncraft limitó temporalmente las consultas. Probá nuevamente más tarde.") from exc
        raise WynncraftError("Wynncraft no está disponible en este momento.") from exc
    except (URLError, TimeoutError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WynncraftError("No se pudo conectar con la API de Wynncraft. Probá más tarde.") from exc
    resultado = extraer_pvp(data)
    cache.set(llave, resultado, 120)
    return resultado


@require_GET
def wynncraft_pvp(request):
    nombre = request.GET.get("nombre", "").strip()
    contexto = {"nombre": nombre[:40], "resultado": None, "mensaje": ""}
    if nombre:
        try:
            contexto["resultado"] = consultar_jugador(nombre)
        except WynncraftError as exc:
            contexto["mensaje"] = str(exc)
    return render(request, "estadisticas/wynncraft_pvp.html", contexto)


@require_GET
def redireccion_pvp_hypixel(request):
    """El enlace anterior sigue funcionando, pero ya no solicita la API de Hypixel."""
    url = reverse("stats:wynncraft_pvp")
    nombre = request.GET.get("nombre", "").strip()
    if nombre and NOMBRE_VALIDO.fullmatch(nombre):
        url += "?" + urlencode({"nombre": nombre})
    return HttpResponseRedirect(url)
