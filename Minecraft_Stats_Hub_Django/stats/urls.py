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

    # ABM de servidores
    path("gestion/servidores/", views.servidores_gestion, name="servidores_gestion"),
    path("gestion/servidores/nuevo/", views.servidor_crear, name="servidor_crear"),
    path("gestion/servidores/<int:pk>/editar/", views.servidor_editar, name="servidor_editar"),
    path("gestion/servidores/<int:pk>/eliminar/", views.servidor_eliminar, name="servidor_eliminar"),

    # ABM de mods
    path("gestion/mods/", views.mods_gestion, name="mods_gestion"),
    path("gestion/mods/nuevo/", views.mod_crear, name="mod_crear"),
    path("gestion/mods/<int:pk>/editar/", views.mod_editar, name="mod_editar"),
    path("gestion/mods/<int:pk>/eliminar/", views.mod_eliminar, name="mod_eliminar"),

    # API JSON usada por la página pública
    path("api/jugadores/buscar/", views.api_buscar_jugador, name="api_buscar_jugador"),
    path("api/resumen/", views.api_resumen, name="api_resumen"),
    path("api/servidores/", views.api_servidores, name="api_servidores"),
    path("api/speedruns/", views.api_speedruns, name="api_speedruns"),
    path("api/mods/", views.api_mods, name="api_mods"),
]
