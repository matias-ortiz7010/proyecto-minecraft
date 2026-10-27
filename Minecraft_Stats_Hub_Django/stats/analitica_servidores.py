"""Vistas de lectura de historial real de servidores, sin modificar registros."""
from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from .models import Servidor, ServidorSnapshot


PERIODOS_VALIDOS = (6, 24, 72, 168)


def estadisticas_servidores(request):
    """Muestra muestras existentes; nunca consulta APIs ni genera datos falsos."""
    periodo_raw = request.GET.get("horas", "24")
    try:
        horas = int(periodo_raw)
    except (TypeError, ValueError):
        horas = 24
    if horas not in PERIODOS_VALIDOS:
        horas = 24

    servidores = list(Servidor.objects.order_by("nombre", "pk"))
    elegido = request.GET.get("servidor", "")
    servidor = next((s for s in servidores if str(s.pk) == elegido), None)
    if servidor is None:
        servidor = servidores[0] if servidores else None

    registros = []
    if servidor is not None:
        # Cortamos a las últimas 4.000 muestras para prevenir páginas enormes.
        registros = list(ServidorSnapshot.objects.filter(
            servidor=servidor, registrado_en__gte=timezone.now() - timedelta(hours=horas)
        ).order_by("-registrado_en", "-pk")[:4000])
    registros.reverse()

    mediciones_online = [r.jugadores for r in registros if r.online]
    puntos = [
        {
            "fecha": registro.registrado_en.isoformat(),
            "jugadores": registro.jugadores if registro.online else None,
            "online": registro.online,
        }
        for registro in registros
    ]
    datos = {
        "servidores": servidores,
        "servidor": servidor,
        "horas": horas,
        "periodos": PERIODOS_VALIDOS,
        "puntos": puntos,
        "muestras": len(registros),
        "muestras_online": len(mediciones_online),
        "maximo": max(mediciones_online) if mediciones_online else None,
        "minimo": min(mediciones_online) if mediciones_online else None,
        "promedio": round(sum(mediciones_online) / len(mediciones_online)) if mediciones_online else None,
        "ultima_muestra": registros[-1] if registros else None,
        "recientes": list(reversed(registros[-12:])),
    }
    return render(request, "estadisticas/servidores.html", datos)
