"""Pruebas de la consulta externa: no hacen peticiones HTTP a speedrun.com."""
from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse

from .speedruns_externos import FuenteNoDisponible, formato_tiempo, procesar_tabla


CATEGORIAS = [
    {'id': 'abc123', 'nombre': 'Any% Glitchless'},
    {'id': 'def456', 'nombre': 'All Advancements'},
]
VARIABLES = [
    {'id': 'semilla1', 'nombre': 'Seed Type', 'opciones': [
        {'id': 'rsg', 'nombre': 'Random Seed'},
        {'id': 'ssg', 'nombre': 'Set Seed'},
    ], 'seleccionado': ''},
]
TABLA = {
    'weblink': 'https://www.speedrun.com/mc',
    'players': {'data': [{'id': 'user1', 'names': {'international': 'Tester'}}]},
    'runs': [{'place': 1, 'run': {
        'players': [{'rel': 'user', 'id': 'user1'}],
        'times': {'primary_t': 410.359},
        'status': {'status': 'verified'},
        'values': {'semilla1': 'rsg'},
        'weblink': 'https://www.speedrun.com/run/test123',
        'date': '2026-10-01',
    }}],
}


class FuenteSpeedrunTest(SimpleTestCase):
    def test_formato_tiempo(self):
        self.assertEqual(formato_tiempo('410.359'), '06:50.359')
        self.assertEqual(formato_tiempo(4000.123), '1:06:40.123')
        self.assertEqual(formato_tiempo(None), '—')

    def test_procesa_tabla_y_jugadores(self):
        filas = procesar_tabla(TABLA, VARIABLES)
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]['jugador'], 'Tester')
        self.assertEqual(filas[0]['tiempo'], '06:50.359')
        self.assertEqual(filas[0]['detalles'], 'Random Seed')

    @patch('stats.speedruns_externos.solicitar_json', return_value=TABLA)
    @patch('stats.speedruns_externos.variables_categoria', return_value=VARIABLES)
    @patch('stats.speedruns_externos.categorias_mc', return_value=CATEGORIAS)
    def test_pagina_es_publica(self, cats, vars, datos):
        r = self.client.get(reverse('stats:speedruns_externos'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Tester')
        self.assertContains(r, '06:50.359')
        datos.assert_called_once()

    @patch('stats.speedruns_externos.solicitar_json', return_value=TABLA)
    @patch('stats.speedruns_externos.variables_categoria', return_value=VARIABLES)
    @patch('stats.speedruns_externos.categorias_mc', return_value=CATEGORIAS)
    def test_filtro_invalido_se_ignora(self, cats, vars, datos):
        self.client.get(reverse('stats:speedruns_externos'), {
            'categoria': 'abc123', 'var_semilla1': 'arbitrario',
        })
        self.assertNotIn('var-semilla1', datos.call_args.args[1])

    @patch('stats.speedruns_externos.categorias_mc', side_effect=FuenteNoDisponible('API temporalmente caída'))
    def test_falla_api_sin_romper_el_sitio(self, cats):
        r = self.client.get(reverse('stats:speedruns_externos'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'API temporalmente caída')
