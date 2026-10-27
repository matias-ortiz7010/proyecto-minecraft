"""Consulta pública y de solo lectura a Modrinth API v2.

No importa información a SQLite, ni usa modelos Django ni toca los ABM.
Filtros validados, límite de respuesta, caché corta y URL de origen fija.
"""
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote, urlsplit
from urllib.request import Request, urlopen

from django.core.cache import cache
from django.http import Http404
from django.shortcuts import render

BASE = "https://api.modrinth.com/v2"
USER_AGENT = "matias-ortiz7010/minecraft-stats-hub/1.0 (proyecto educativo)"
CACHE_TTL = 300
MAX_RESPONSE_BYTES = 2_000_000
LOADERS = {"fabric", "forge", "neoforge", "quilt"}
ORDENES = {"relevance", "downloads", "newest", "updated"}
VERSION_RE = re.compile(r"^[0-9]{1,2}\.[0-9]{1,2}(?:\.[0-9]{1,2})?$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")


class ModrinthNoDisponible(Exception):
    """Error transitorio de la fuente externa o datos inválidos."""


def solicitar_json(ruta, parametros=None, ttl=CACHE_TTL):
    """Accede solo al dominio fijo de Modrinth; nunca a URLs del usuario."""
    if not ruta.startswith("/") or ".." in ruta or "?" in ruta:
        raise ValueError("Ruta de Modrinth no válida")
    url = BASE + ruta
    if parametros:
        url += "?" + urlencode(parametros)
    cache_key = "msh:modrinth:v2:" + url
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    request = Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    try:
        with urlopen(request, timeout=12) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise ModrinthNoDisponible("La respuesta de Modrinth es demasiado grande.")
        data = json.loads(body.decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, UnicodeError, ValueError) as exc:
        raise ModrinthNoDisponible("No se pudo consultar Modrinth. Intentá de nuevo más tarde.") from exc
    cache.set(cache_key, data, ttl)
    return data


def _numero(value):
    try:
        return f"{max(0, int(value)):,}".replace(",", ".")
    except (TypeError, ValueError, OverflowError):
        return "—"


def _limitar_version(value):
    value = str(value or "").strip()[:20]
    return value if VERSION_RE.fullmatch(value) else ""


def _filtrar(request):
    consulta = request.GET.get("q", "").strip()[:65]
    version = _limitar_version(request.GET.get("version"))
    loader = request.GET.get("loader", "").lower()
    if loader not in LOADERS:
        loader = ""
    orden = request.GET.get("orden", "downloads")
    if orden not in ORDENES:
        orden = "downloads"
    try:
        pagina = max(1, min(10, int(request.GET.get("pagina", "1"))))
    except (ValueError, TypeError):
        pagina = 1
    return consulta, version, loader, orden, pagina


def _icono(url):
    # Solo imágenes alojadas en el CDN conocido de Modrinth.
    return url if isinstance(url, str) and url.startswith("https://cdn.modrinth.com/") else ""


def _normalizar_hit(hit):
    if not isinstance(hit, dict) or hit.get("project_type") != "mod":
        return None
    slug = str(hit.get("slug") or "").lower()
    if not SLUG_RE.fullmatch(slug):
        return None
    return {
        "slug": slug,
        "nombre": str(hit.get("title") or slug)[:140],
        "descripcion": str(hit.get("description") or "")[:350],
        "autor": str(hit.get("author") or "No indicado")[:100],
        "descargas": _numero(hit.get("downloads")),
        "versiones_mc": ", ".join(str(v) for v in (hit.get("versions") or [])[-5:]) or "No informadas",
        "icono": _icono(hit.get("icon_url")),
        "url": "https://modrinth.com/mod/" + quote(slug),
    }


def _query_string(filtros, pagina):
    data = dict(filtros)
    data["pagina"] = pagina
    return urlencode({k: v for k, v in data.items() if v not in ("", None)})


def mods_externos(request):
    consulta, version, loader, orden, pagina = _filtrar(request)
    base_filtros = {"q": consulta, "version": version, "loader": loader, "orden": orden}
    contexto = {
        "consulta": consulta, "version": version, "loader": loader,
        "orden": orden, "pagina": pagina, "mods": [], "total": 0,
        "error": "", "siguiente": "", "anterior": "",
    }
    facetas = [["project_type:mod"]]
    if version:
        facetas.append(["versions:" + version])
    if loader:
        facetas.append(["categories:" + loader])
    try:
        resultado = solicitar_json("/search", {
            "query": consulta, "facets": json.dumps(facetas, separators=(",", ":")),
            "index": orden, "limit": 12, "offset": (pagina - 1) * 12,
        })
        if not isinstance(resultado, dict) or not isinstance(resultado.get("hits"), list):
            raise ModrinthNoDisponible("La API devolvió datos inesperados.")
        mods = [x for h in resultado["hits"] if (x := _normalizar_hit(h))]
        try:
            total = max(0, int(resultado.get("total_hits", len(mods))))
        except (ValueError, TypeError):
            total = len(mods)
        contexto.update({"mods": mods, "total": total})
        if pagina > 1:
            contexto["anterior"] = _query_string(base_filtros, pagina - 1)
        if pagina * 12 < total and pagina < 10:
            contexto["siguiente"] = _query_string(base_filtros, pagina + 1)
    except ModrinthNoDisponible as error:
        contexto["error"] = str(error)
    return render(request, "estadisticas/mods_externos.html", contexto)


def _url_descarga_modrinth(url):
    """Acepta únicamente archivos del CDN oficial de Modrinth.

    Nunca se solicita el archivo desde Django: el navegador contacta al CDN.
    """
    if not isinstance(url, str) or len(url) > 2048:
        return ""
    try:
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or parsed.netloc != "cdn.modrinth.com"
                or parsed.username or parsed.password or parsed.port is not None
                or not parsed.path.startswith("/data/")
                or not parsed.path.lower().endswith((".jar", ".zip"))):
            return ""
    except ValueError:
        return ""
    return url


def _archivo_principal(version):
    """Prioriza el archivo principal publicado por Modrinth; excluye fuentes y dev jars."""
    files = version.get("files") or []
    if not isinstance(files, list):
        return None
    validos = []
    for f in files[:30]:
        if not isinstance(f, dict):
            continue
        if f.get("file_type") not in (None, "", "unknown"):
            continue
        nombre = str(f.get("filename") or "")[:200]
        lower_name = nombre.lower()
        if not lower_name.endswith((".jar", ".zip")):
            continue
        if any(term in lower_name for term in ("-sources.jar", "-javadoc.jar", "-dev.jar")):
            continue
        descarga = _url_descarga_modrinth(f.get("url"))
        if descarga:
            validos.append({
                "url": descarga,
                "nombre": nombre,
                "primary": f.get("primary") is True,
                "sha512": str((f.get("hashes") or {}).get("sha512") or "")[:128],
            })
    return next((f for f in validos if f["primary"]), validos[0] if validos else None)


def mod_externo_detalle(request, slug):
    if not SLUG_RE.fullmatch(slug):
        raise Http404("Mod no encontrado")
    version = _limitar_version(request.GET.get("version"))
    loader = request.GET.get("loader", "").lower()
    if loader not in LOADERS:
        loader = ""
    contexto = {"slug": slug, "version": version, "loader": loader,
                "mod": None, "versiones": [], "error": ""}
    try:
        datos = solicitar_json("/project/" + quote(slug))
        if not isinstance(datos, dict) or datos.get("project_type") != "mod":
            raise Http404("Proyecto no encontrado como mod")
        params = {"include_changelog": "false"}
        if version:
            params["game_versions"] = json.dumps([version])
        if loader:
            params["loaders"] = json.dumps([loader])
        versiones = solicitar_json("/project/" + quote(slug) + "/version", params)
        if not isinstance(versiones, list):
            raise ModrinthNoDisponible("No se pudieron interpretar las versiones.")
        versiones = sorted((v for v in versiones if isinstance(v, dict)),
                           key=lambda v: str(v.get("date_published", "")), reverse=True)
        contexto["mod"] = {
            "nombre": str(datos.get("title") or slug)[:140],
            "descripcion": str(datos.get("description") or "")[:400],
            "descargas": _numero(datos.get("downloads")),
            "icono": _icono(datos.get("icon_url")),
            "url": "https://modrinth.com/mod/" + quote(slug),
        }
        contexto["versiones"] = [{
            "numero": str(v.get("version_number") or "—")[:100],
            "nombre": str(v.get("name") or "")[:100],
            "fecha": str(v.get("date_published") or "")[:10],
            "mc": ", ".join(str(x) for x in (v.get("game_versions") or [])[:5]),
            "loaders": ", ".join(str(x) for x in (v.get("loaders") or [])[:5]),
            "tipo": str(v.get("version_type") or "—")[:20],
            "descargas": _numero(v.get("downloads")),
            "archivo": _archivo_principal(v),
            "pagina_version": ("https://modrinth.com/mod/" + quote(slug) + "/version/" + v["id"])
                              if isinstance(v.get("id"), str) and re.fullmatch(r"[A-Za-z0-9]{5,20}", v["id"])
                              else "https://modrinth.com/mod/" + quote(slug),
        } for v in versiones[:20]]
    except ModrinthNoDisponible as error:
        contexto["error"] = str(error)
    return render(request, "estadisticas/mod_detalle.html", contexto)
