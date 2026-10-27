"""python manage.py actualizar_servidores [--continuo]

Refresca Servidor y registra muestras históricas sin cambiar el esquema SQL.
"""
import time
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from stats.models import Servidor, ServidorSnapshot
from stats.services.estado_minecraft import EstadoMinecraftError, consultar_estado


class Command(BaseCommand):
    help = "Consulta estados reales de servidores y registra el historial."

    def add_arguments(self, parser):
        parser.add_argument("--continuo", action="store_true", help="Repetir mientras esté abierto Codespaces")
        parser.add_argument("--intervalo", type=int, default=300,
                            help="Segundos entre consultas en modo continuo (mínimo 300)")

    def handle(self, *args, **options):
        intervalo = options["intervalo"]
        if options["continuo"] and intervalo < 300:
            raise CommandError("La API almacena respuestas unos 5 minutos. Usá --intervalo 300 o mayor.")
        if not options["continuo"]:
            self.actualizar_todos()
            return
        self.stdout.write("Actualizador activo cada %s segundos. Detener con Ctrl+C." % intervalo)
        try:
            while True:
                self.actualizar_todos()
                time.sleep(intervalo)
        except KeyboardInterrupt:
            self.stdout.write("Actualizador detenido.")

    def actualizar_todos(self):
        servidores = list(Servidor.objects.order_by("pk"))
        if not servidores:
            self.stdout.write("No hay servidores. Creá alguno desde el ABM.")
            return
        ok = 0
        for servidor in servidores:
            try:
                estado = consultar_estado(servidor.ip)
            except EstadoMinecraftError as exc:
                self.stderr.write(self.style.WARNING(
                    "%s (%s): %s. Se conserva el último valor guardado." % (servidor.nombre, servidor.ip, exc)))
                continue
            with transaction.atomic():
                Servidor.objects.filter(pk=servidor.pk).update(
                    online=estado["online"], jugadores=estado["jugadores"],
                    actualizado_en=timezone.now())
                ServidorSnapshot.objects.create(
                    servidor_id=servidor.pk, online=estado["online"],
                    jugadores=estado["jugadores"])
            ok += 1
            self.stdout.write(self.style.SUCCESS(
                "%s: %s · %s jugadores%s" % (
                    servidor.nombre, "Online" if estado["online"] else "Offline",
                    estado["jugadores"],
                    " · Minecraft " + estado["version"] if estado["version"] else "")))
        self.stdout.write("Servidores actualizados: %s/%s" % (ok, len(servidores)))
