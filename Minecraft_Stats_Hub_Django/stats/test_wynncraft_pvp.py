"""Pruebas de la integración pública sin llamadas reales a la red."""
import io
import json
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from django.core.cache import cache
from django.test import SimpleTestCase

from .wynncraft_pvp import WynncraftError, consultar_jugador, extraer_pvp


class WynncraftPvPTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_pvp_publico(self):
        datos = {'username': 'Ejemplo', 'uuid': 'abc', 'globalData': {'pvp': {'kills': 24, 'deaths': 8}}}
        resumen = extraer_pvp(datos)
        self.assertEqual(resumen['kills'], 24)
        self.assertEqual(resumen['muertes'], 8)
        self.assertEqual(resumen['ratio'], '3,00')
        self.assertTrue(resumen['disponible'])

    def test_sin_muertes_no_divide_por_cero(self):
        resumen = extraer_pvp({'globalData': {'pvp': {'kills': 12, 'deaths': 0}}})
        self.assertEqual(resumen['ratio'], '∞')

    def test_pvp_oculto_no_es_cero(self):
        resumen = extraer_pvp({'username': 'Privado', 'globalData': {}})
        self.assertIsNone(resumen['kills'])
        self.assertFalse(resumen['disponible'])

    def test_parcial_no_inventa_datos(self):
        resumen = extraer_pvp({'globalData': {'pvp': {'kills': 5}}})
        self.assertIsNone(resumen['muertes'])
        self.assertFalse(resumen['disponible'])

    def test_nombre_malicioso_rechazado(self):
        with self.assertRaises(WynncraftError):
            consultar_jugador('../../admin')

    def test_consulta_exitosa_con_cache(self):
        muestra = {'username': 'Ejemplo', 'globalData': {'pvp': {'kills': 7, 'deaths': 2}}}
        with patch('stats.wynncraft_pvp.urlopen', return_value=io.BytesIO(json.dumps(muestra).encode())) as llamada:
            x = consultar_jugador('Ejemplo')
            y = consultar_jugador('Ejemplo')
        self.assertEqual(x['kills'], 7)
        self.assertEqual(y['kills'], 7)
        self.assertEqual(llamada.call_count, 1)

    def test_jugador_inexistente(self):
        error = HTTPError('https://api.wynncraft.com/', 404, 'Not Found', None, None)
        with patch('stats.wynncraft_pvp.urlopen', side_effect=error):
            with self.assertRaisesRegex(WynncraftError, 'No se encontró'):
                consultar_jugador('Inexistente')

    def test_api_limite(self):
        error = HTTPError('https://api.wynncraft.com/', 429, 'Too many', None, None)
        with patch('stats.wynncraft_pvp.urlopen', side_effect=error):
            with self.assertRaisesRegex(WynncraftError, 'limitó'):
                consultar_jugador('Alguien')

    def test_fallo_red(self):
        with patch('stats.wynncraft_pvp.urlopen', side_effect=URLError('offline')):
            with self.assertRaisesRegex(WynncraftError, 'No se pudo conectar'):
                consultar_jugador('Alguien')

    def test_template_y_ruta(self):
        resp = self.client.get('/estadisticas/pvp/wynncraft/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'PvP real de Wynncraft')

    def test_ruta_antigua_redirige(self):
        resp = self.client.get('/estadisticas/pvp/hypixel/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/estadisticas/pvp/wynncraft/', resp['Location'])
