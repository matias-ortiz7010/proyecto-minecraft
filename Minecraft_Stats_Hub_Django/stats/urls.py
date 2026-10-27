from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .auth_forms import StaffLoginForm
from . import views
from .analitica_servidores import estadisticas_servidores
from .speedruns_externos import speedruns_externos

app_name = "stats"

urlpatterns = [
    path("gestion/ingresar/", LoginView.as_view(
        template_name="gestion/login.html",
        authentication_form=StaffLoginForm,
        next_page="stats:jugadores_gestion",
        redirect_authenticated_user=False,
    ), name="gestion_login"),
    path("gestion/salir/", LogoutView.as_view(next_page="stats:index"), name="gestion_logout"),
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

    # ABM de speedruns
    path("gestion/speedruns/", views.speedruns_gestion, name="speedruns_gestion"),
    path("gestion/speedruns/nuevo/", views.speedrun_crear, name="speedrun_crear"),
    path("gestion/speedruns/<int:pk>/editar/", views.speedrun_editar, name="speedrun_editar"),
    path("gestion/speedruns/<int:pk>/eliminar/", views.speedrun_eliminar, name="speedrun_eliminar"),

    # Analítica pública de datos históricos de servidores
    path("estadisticas/servidores/", estadisticas_servidores, name="estadisticas_servidores"),

    # Clasificaciones externas (solo lectura, sin tocar los registros del ABM)
    path("estadisticas/speedruns/", speedruns_externos, name="speedruns_externos"),

    # API JSON usada por la página pública
    path("api/jugadores/buscar/", views.api_buscar_jugador, name="api_buscar_jugador"),
    path("api/resumen/", views.api_resumen, name="api_resumen"),
    path("api/servidores/", views.api_servidores, name="api_servidores"),
    path("api/speedruns/", views.api_speedruns, name="api_speedruns"),
    path("api/mods/", views.api_mods, name="api_mods"),
]
