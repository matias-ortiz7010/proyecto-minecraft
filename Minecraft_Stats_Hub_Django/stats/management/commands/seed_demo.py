from datetime import date
from django.core.management.base import BaseCommand

from stats.models import Jugador, Mod, PvP, Servidor, ServidorSnapshot, Speedrun


class Command(BaseCommand):
    help = "Carga datos de demostración para probar Minecraft Stats Hub."

    def handle(self, *args, **options):
        lowk3y, _ = Jugador.objects.update_or_create(
            nombre="lowk3y_",
            defaults={"uuid": "demo-lowk3y-uuid", "pais": ""},
        )
        dream, _ = Jugador.objects.update_or_create(
            nombre="Dream",
            defaults={"uuid": "ec70bcaf-demo-uuid", "pais": ""},
        )
        feinberg, _ = Jugador.objects.update_or_create(nombre="Feinberg", defaults={"uuid": None})
        couriway, _ = Jugador.objects.update_or_create(nombre="Couriway", defaults={"uuid": None})

        PvP.objects.update_or_create(
            jugador=lowk3y,
            defaults={"victorias": 680, "derrotas": 120, "kills": 1850, "racha": 27},
        )
        PvP.objects.update_or_create(
            jugador=dream,
            defaults={"victorias": 540, "derrotas": 160, "kills": 1320, "racha": 19},
        )

        speedruns = [
            (lowk3y, "Any% Random Seed", 410000, date(2025, 1, 1), "1.16.1"),
            (feinberg, "Any% Random Seed", 423000, date(2025, 2, 1), "1.16.1"),
            (couriway, "Any% Random Seed", 430000, date(2025, 3, 1), "1.16.1"),
        ]
        for jugador, categoria, tiempo_ms, fecha, version in speedruns:
            Speedrun.objects.update_or_create(
                jugador=jugador,
                categoria=categoria,
                defaults={
                    "tiempo_ms": tiempo_ms,
                    "fecha": fecha,
                    "version": version,
                    "verificado": False,
                },
            )

        for nombre, autor, version, descargas in [
            ("Sodium", "CaffeineMC", "demo", 1000000),
            ("OptiFine", "sp614x", "demo", 900000),
            ("Iris", "IrisShaders", "demo", 800000),
            ("Create", "simibubi", "demo", 700000),
        ]:
            Mod.objects.update_or_create(
                nombre=nombre,
                defaults={"autor": autor, "version": version, "descargas": descargas},
            )

        hypixel, _ = Servidor.objects.update_or_create(
            ip="mc.hypixel.net",
            defaults={"nombre": "Hypixel", "pais": "", "jugadores": 42000, "online": True},
        )
        ServidorSnapshot.objects.create(servidor=hypixel, jugadores=hypixel.jugadores, online=hypixel.online)

        self.stdout.write(self.style.SUCCESS("Datos demo cargados correctamente."))
