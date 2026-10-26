from django.urls import path
from . import views

app_name = "stats"

urlpatterns = [
    path("", views.index, name="index"),

    # ABM de jugadores
    path("gestion/jugadores/", views.jugadores_gestion, name="jugadores_gestion"),
    path("gestion/jugadores/nuevo/", views.jugador_crear, name="jugador_crear"),
    path("gestion/jugadores/<int:pk>/editar/", views.jugador_editar, name="jugador_editar"),
    path("gestion/jugadores/<int:pk>/eliminar/", views.jugador_eliminar, name="jugador_eliminar"),

    # API JSON usada por la página pública
    path("api/jugadores/buscar/", views.api_buscar_jugador, name="api_buscar_jugador"),
    path("api/resumen/", views.api_resumen, name="api_resumen"),
    path("api/servidores/", views.api_servidores, name="api_servidores"),
    path("api/speedruns/", views.api_speedruns, name="api_speedruns"),
    path("api/mods/", views.api_mods, name="api_mods"),
]
