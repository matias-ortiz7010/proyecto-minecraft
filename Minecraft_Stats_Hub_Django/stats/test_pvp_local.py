from django.test import TestCase
from django.urls import reverse
from .models import Jugador, PvP


class AnalisisPvPLocalTests(TestCase):
    def setUp(self):
        a = Jugador.objects.create(nombre="AlphaTest")
        b = Jugador.objects.create(nombre="BetaTest")
        PvP.objects.create(jugador=a, victorias=8, derrotas=2, kills=10, racha=2)
        PvP.objects.create(jugador=b, victorias=4, derrotas=0, kills=40, racha=4)
        self.url = reverse("stats:estadisticas_pvp_local")

    def test_vista_publica_y_resumen(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AlphaTest")
        self.assertEqual(response.context["totales"]["jugadores"], 2)
        self.assertEqual(response.context["totales"]["victorias"], 12)
        self.assertEqual(response.context["totales"]["winrate"], 85.7)

    def test_ordenar_por_kills(self):
        response = self.client.get(self.url, {"orden": "kills"})
        self.assertEqual(response.context["filas"][0]["jugador"], "BetaTest")

    def test_minimo_de_partidas(self):
        response = self.client.get(self.url, {"min": "5"})
        self.assertEqual([x["jugador"] for x in response.context["filas"]], ["AlphaTest"])

    def test_orden_por_winrate(self):
        response = self.client.get(self.url, {"orden": "winrate"})
        self.assertEqual(response.context["filas"][0]["jugador"], "BetaTest")

    def test_parametros_invalidos_son_ignorados(self):
        response = self.client.get(self.url, {"orden": "--oops--", "min": "cadena"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["orden"], "victorias")
        self.assertEqual(response.context["minimo"], 0)

    def test_consulta_no_modifica_los_datos(self):
        self.client.get(self.url)
        self.assertEqual(PvP.objects.count(), 2)
        self.assertEqual(PvP.objects.get(jugador__nombre="AlphaTest").victorias, 8)
