from django.urls import path
from . import views

app_name = "stats"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/jugadores/buscar/", views.api_buscar_jugador, name="api_buscar_jugador"),
    path("api/resumen/", views.api_resumen, name="api_resumen"),
    path("api/servidores/", views.api_servidores, name="api_servidores"),
    path("api/speedruns/", views.api_speedruns, name="api_speedruns"),
    path("api/mods/", views.api_mods, name="api_mods"),
]
