from django.contrib import admin
from .models import Jugador, Mod, PvP, Servidor, ServidorSnapshot, Speedrun


@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "uuid", "pais", "actualizado_en")
    search_fields = ("nombre", "uuid")


@admin.register(Speedrun)
class SpeedrunAdmin(admin.ModelAdmin):
    list_display = ("jugador", "categoria", "tiempo_formateado", "version", "fecha", "verificado")
    list_filter = ("categoria", "version", "verificado")
    search_fields = ("jugador__nombre",)


@admin.register(PvP)
class PvPAdmin(admin.ModelAdmin):
    list_display = ("jugador", "victorias", "derrotas", "kills", "racha", "winrate")
    search_fields = ("jugador__nombre",)


@admin.register(Mod)
class ModAdmin(admin.ModelAdmin):
    list_display = ("nombre", "autor", "version", "descargas", "actualizado_en")
    search_fields = ("nombre", "autor")


@admin.register(Servidor)
class ServidorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ip", "online", "jugadores", "actualizado_en")
    list_filter = ("online",)
    search_fields = ("nombre", "ip")


@admin.register(ServidorSnapshot)
class ServidorSnapshotAdmin(admin.ModelAdmin):
    list_display = ("servidor", "jugadores", "online", "registrado_en")
    list_filter = ("online", "servidor")
