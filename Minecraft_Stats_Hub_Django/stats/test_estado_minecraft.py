import io
import json
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from stats.models import Servidor, ServidorSnapshot
from stats.services.estado_minecraft import EstadoMinecraftError, consultar_estado


class EstadoMinecraftTests(TestCase):
    def setUp(self):
        self.servidor = Servidor.objects.create(
            nombre="ServidorPrueba", ip="mc.example.com", jugadores=99, online=False)

    def fake_api(self, data):
        return io.BytesIO(json.dumps(data).encode("utf-8"))

    @patch("stats.services.estado_minecraft.urlopen")
    def test_actualiza_online_y_guarda_historial(self, opener):
        opener.return_value = self.fake_api({"online": True, "players": {"online": 12}, "version": "1.21"})
        call_command("actualizar_servidores", verbosity=0)
        self.servidor.refresh_from_db()
        self.assertTrue(self.servidor.online)
        self.assertEqual(self.servidor.jugadores, 12)
        self.assertEqual(ServidorSnapshot.objects.filter(servidor=self.servidor).count(), 1)
        self.assertEqual(ServidorSnapshot.objects.get(servidor=self.servidor).jugadores, 12)
        self.assertIn("User-agent", dict(opener.call_args.args[0].header_items()))

    @patch("stats.services.estado_minecraft.urlopen")
    def test_actualiza_offline(self, opener):
        opener.side_effect = [self.fake_api({"online": False}), self.fake_api({"online": False})]
        call_command("actualizar_servidores", verbosity=0)
        self.servidor.refresh_from_db()
        self.assertFalse(self.servidor.online)
        self.assertEqual(self.servidor.jugadores, 0)

    @patch("stats.services.estado_minecraft.urlopen", side_effect=OSError("network error"))
    def test_error_no_borra_datos(self, opener):
        call_command("actualizar_servidores", verbosity=0)
        self.servidor.refresh_from_db()
        self.assertEqual(self.servidor.jugadores, 99)
        self.assertEqual(ServidorSnapshot.objects.count(), 0)

    def test_direccion_invalida_rechazada(self):
        with self.assertRaises(EstadoMinecraftError):
            consultar_estado("http://localhost/path")
