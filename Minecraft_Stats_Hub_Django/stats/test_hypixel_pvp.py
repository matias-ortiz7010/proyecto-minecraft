import json
from unittest.mock import patch
from django.test import SimpleTestCase, override_settings
from django.core.cache import cache
from django.test import Client
from .hypixel_pvp import resumir_stats, consultar_hypixel, HypixelClaveIncorrecta

class TestHypixelStats(SimpleTestCase):
    def test_modos_separados(self):
        result = resumir_stats({'stats': {'Bedwars': {'wins_bedwars': 20, 'losses_bedwars': 10}, 'SkyWars': {'wins': 7}}})
        self.assertEqual(result[0]['campos'][0]['valor'], 20)
        self.assertEqual(result[1]['campos'][0]['valor'], 7)
        self.assertFalse(result[2]['disponible'])

    def test_no_confundir_faltantes_con_cero(self):
        self.assertIsNone(resumir_stats({'stats': {'Duels': {'wins': 3}}})[2]['campos'][1]['valor'])

    @patch.dict('os.environ', {}, clear=True)
    def test_mensaje_sin_clave(self):
        respuesta = Client().get('/estadisticas/pvp/hypixel/')
        self.assertRedirects(
            respuesta,
            "/estadisticas/pvp/wynncraft/",
            fetch_redirect_response=False,
)
