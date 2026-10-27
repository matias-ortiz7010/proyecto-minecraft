"""Pruebas de contraste entre dos APIs para impedir falsas caídas."""
import io
import json
from unittest.mock import patch

from django.test import SimpleTestCase
from stats.services.estado_minecraft import EstadoMinecraftError, consultar_estado


def respuesta(datos):
    return io.BytesIO(json.dumps(datos).encode("utf-8"))


class FallbackMinecraftTests(SimpleTestCase):
    @patch("stats.services.estado_minecraft.urlopen")
    def test_primera_online_no_consulta_segunda(self, urlopen):
        urlopen.return_value = respuesta({"online": True, "players": {"online": 10}, "version": "1.21"})
        resultado = consultar_estado("mc.hypixel.net")
        self.assertEqual(resultado["jugadores"], 10)
        self.assertEqual(urlopen.call_count, 1)

    @patch("stats.services.estado_minecraft.urlopen")
    def test_primera_false_segunda_true(self, urlopen):
        urlopen.side_effect = [
            respuesta({"online": False}),
            respuesta({"online": True, "players": {"online": 33000}, "version": {"name": "1.21"}}),
        ]
        resultado = consultar_estado("mc.hypixel.net")
        self.assertTrue(resultado["online"])
        self.assertEqual(resultado["jugadores"], 33000)
        self.assertEqual(resultado["version"], "1.21")
        self.assertEqual(urlopen.call_count, 2)

    @patch("stats.services.estado_minecraft.urlopen")
    def test_ambas_offline_confirma_caida(self, urlopen):
        urlopen.side_effect = [respuesta({"online": False}), respuesta({"online": False})]
        self.assertEqual(consultar_estado("mc.example.com"), {"online": False, "jugadores": 0, "version": None})

    @patch("stats.services.estado_minecraft.urlopen")
    def test_primera_offline_segunda_error_no_sobreescribir(self, urlopen):
        urlopen.side_effect = [respuesta({"online": False}), OSError("timeout")]
        with self.assertRaises(EstadoMinecraftError):
            consultar_estado("mc.example.com")

    @patch("stats.services.estado_minecraft.urlopen")
    def test_primera_error_segunda_online(self, urlopen):
        urlopen.side_effect = [OSError("timeout"), respuesta({"online": True, "players": {"online": 5}})]
        self.assertEqual(consultar_estado("mc.example.com")["jugadores"], 5)
