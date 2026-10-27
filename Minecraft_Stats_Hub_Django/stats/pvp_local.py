"""Resumen PvP de registros locales. No consulta ni modifica la API de Hypixel."""
from django.shortcuts import render
from .models import PvP

ORDENES = {"victorias", "kills", "winrate"}
MIN_PARTIDAS = {0, 5, 10, 25, 50}


def estadisticas_pvp_local(request):
    orden = request.GET.get("orden", "victorias")
    if orden not in ORDENES:
        orden = "victorias"
    try:
        minimo = int(request.GET.get("min", "0"))
    except (ValueError, TypeError):
        minimo = 0
    if minimo not in MIN_PARTIDAS:
        minimo = 0

    filas = []
    for registro in PvP.objects.select_related("jugador").all():
        partidas = registro.victorias + registro.derrotas
        if partidas < minimo:
            continue
        filas.append({
            "jugador": registro.jugador.nombre,
            "victorias": registro.victorias,
            "derrotas": registro.derrotas,
            "partidas": partidas,
            "kills": registro.kills,
            "racha": registro.racha,
            "winrate": registro.winrate,
        })

    if orden == "winrate":
        filas.sort(key=lambda f: (-f["winrate"], -f["partidas"], f["jugador"].lower()))
    else:
        filas.sort(key=lambda f: (-f[orden], -f["victorias"], f["jugador"].lower()))

    totales = {
        "jugadores": len(filas),
        "victorias": sum(f["victorias"] for f in filas),
        "derrotas": sum(f["derrotas"] for f in filas),
        "kills": sum(f["kills"] for f in filas),
    }
    partidas_totales = totales["victorias"] + totales["derrotas"]
    totales["winrate"] = round(totales["victorias"] * 100 / partidas_totales, 1) if partidas_totales else 0
    visibles = filas[:30]
    graficables = filas[:10]
    return render(request, "estadisticas/pvp_local.html", {
        "filas": visibles,
        "orden": orden,
        "minimo": minimo,
        "totales": totales,
        "truncado": len(filas) > len(visibles),
        "grafico": {
            "nombres": [f["jugador"] for f in graficables],
            "victorias": [f["victorias"] for f in graficables],
            "derrotas": [f["derrotas"] for f in graficables],
        },
    })
