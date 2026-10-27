"""Sin red: asegura filtros, mensajes de error y que no haya escrituras en BD."""
import json
from unittest.mock import patch
from django.test import SimpleTestCase
from django.urls import reverse
from .modrinth_externos import (_filtrar, _normalizar_hit, ModrinthNoDisponible,
                                _limitar_version, _icono)

HIT={"project_type":"mod","slug":"sodium","title":"Sodium", "author":"CaffeineMC",
     "description":"Renderizado optimizado", "downloads":123456,"versions":["1.20.1","1.21.1"],
     "icon_url":"https://cdn.modrinth.com/data/icon.png"}

class ModrinthTest(SimpleTestCase):
    def test_pagina_publica_y_datos(self):
        with patch('stats.modrinth_externos.solicitar_json', return_value={"hits":[HIT],"total_hits":1}) as api:
            response=self.client.get(reverse('stats:mods_externos'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'Sodium')
        self.assertContains(response,'123.456')
        args=api.call_args.args
        self.assertEqual(args[0],'/search')
        self.assertIn(['project_type:mod'], json.loads(args[1]['facets']))

    def test_filtros_validos(self):
        with patch('stats.modrinth_externos.solicitar_json', return_value={'hits':[HIT],'total_hits':1}) as api:
            self.client.get(reverse('stats:mods_externos'),{'version':'1.21.1','loader':'fabric','orden':'downloads','q':'sodium'})
        facets=json.loads(api.call_args.args[1]['facets'])
        self.assertIn(['versions:1.21.1'],facets)
        self.assertIn(['categories:fabric'],facets)
        self.assertEqual(api.call_args.args[1]['query'],'sodium')

    def test_inyeccion_de_filtros_rechazada(self):
        with patch('stats.modrinth_externos.solicitar_json', return_value={'hits':[],'total_hits':0}) as api:
            self.client.get(reverse('stats:mods_externos'),{'loader':'foo:bar','version':'1.21.1"], ["project_type:modpack'})
        self.assertEqual(json.loads(api.call_args.args[1]['facets']),[['project_type:mod']])

    def test_error_api_legible(self):
        with patch('stats.modrinth_externos.solicitar_json',side_effect=ModrinthNoDisponible('API temporalmente no disponible')):
            r=self.client.get(reverse('stats:mods_externos'))
        self.assertEqual(r.status_code,200)
        self.assertContains(r,'API temporalmente no disponible')

    def test_detalle_y_versiones(self):
        mod={'project_type':'mod','title':'Sodium','description':'Rapidez','downloads':50}
        versiones=[{'version_number':'0.6.0','name':'Sodium 0.6','date_published':'2026-01-01T00:00:00Z','game_versions':['1.21.1'],'loaders':['fabric'],'downloads':20}]
        with patch('stats.modrinth_externos.solicitar_json',side_effect=[mod,versiones]) as api:
            r=self.client.get(reverse('stats:mod_externo_detalle',kwargs={'slug':'sodium'}),{'loader':'fabric','version':'1.21.1'})
        self.assertEqual(r.status_code,200)
        self.assertContains(r,'0.6.0')
        self.assertEqual(json.loads(api.call_args_list[1].args[1]['loaders']),['fabric'])

    def test_no_reutiliza_proyecto_no_mod(self):
        with patch('stats.modrinth_externos.solicitar_json',return_value={'project_type':'modpack'}):
            r=self.client.get(reverse('stats:mod_externo_detalle',kwargs={'slug':'pack'}))
        self.assertEqual(r.status_code,404)

    def test_urls_externas_son_controladas(self):
        self.assertEqual(_icono('javascript:alert(1)'), '')
        self.assertEqual(_normalizar_hit({'slug':'../hi','project_type':'mod'}),None)
        self.assertEqual(_limitar_version('1.21.1\",[\"bad'), '')
