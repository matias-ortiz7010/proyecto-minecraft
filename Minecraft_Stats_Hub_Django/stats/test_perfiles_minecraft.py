"""Pruebas del visor de skins. No hacen peticiones externas ni alteran el ABM."""
import base64
import io
import json
import struct
from unittest.mock import patch
from django.core.cache import cache
from django.test import SimpleTestCase
from django.urls import reverse

from .perfiles_minecraft import (
    consultar_perfil, obtener_texturas, obtener_png_skin,
    _url_textura, PerfilNoDisponible, JugadorNoEncontrado,
)

UUID = '853c80ef3c3749fdaa49938b674adae6'
HASH = 'a' * 64
TEXTURA = 'https://textures.minecraft.net/texture/' + HASH


def respuesta_png(w=64, h=64):
    return b'\x89PNG\r\n\x1a\n' + b'\x00\x00\x00\x0dIHDR' + struct.pack('>II', w, h) + b'\x08\x06\x00\x00\x00' + b'0' * 10


class FakeResponse(io.BytesIO):
    status = 200


class PerfilesMinecraftTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_formulario(self):
        r = self.client.get(reverse('stats:perfiles_minecraft'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Perfiles reales de Minecraft')

    def test_muestra_png_oficial_y_no_imagen_generica(self):
        perfil = {
            'nombre': 'jeb_', 'uuid': UUID,
            'uuid_formato': '853c80ef-3c37-49fd-aa49-938b674adae6',
            'skin_url': TEXTURA, 'skin_hash': HASH,
            'cape_url': '', 'modelo': 'Slim (brazos finos)', 'estado_skin': 'personalizada',
        }
        with patch('stats.perfiles_minecraft.consultar_perfil', return_value=perfil):
            r = self.client.get(reverse('stats:perfiles_minecraft'), {'nombre': 'jeb_'})
        self.assertContains(r, '853c80ef-3c37-49fd-aa49-938b674adae6')
        self.assertContains(r, '?skin=' + HASH)
        self.assertNotContains(r, 'crafatar.com')
        self.assertContains(r, 'skin_minecraft.js')

    def test_no_mostrar_alex_si_mojang_no_responde(self):
        perfil = {
            'nombre': 'jeb_', 'uuid': UUID, 'uuid_formato': UUID,
            'skin_url': '', 'skin_hash': '', 'cape_url': '',
            'modelo': 'No se pudo comprobar', 'estado_skin': 'no_verificada',
        }
        with patch('stats.perfiles_minecraft.consultar_perfil', return_value=perfil):
            r = self.client.get(reverse('stats:perfiles_minecraft'), {'nombre': 'jeb_'})
        self.assertContains(r, 'No se pudo verificar la skin')
        self.assertNotContains(r, '?skin=' + HASH)

    def test_ruta_no_acepta_hacks_en_hash(self):
        ruta = reverse('stats:perfiles_minecraft')
        with patch('stats.perfiles_minecraft.obtener_png_skin') as descargar:
            r = self.client.get(ruta, {'skin': 'https://example.org/private'})
        self.assertEqual(r.status_code, 400)
        descargar.assert_not_called()

    def test_proxy_entrega_png(self):
        ruta = reverse('stats:perfiles_minecraft')
        contenido = respuesta_png()
        with patch('stats.perfiles_minecraft.obtener_png_skin', return_value=contenido):
            r = self.client.get(ruta, {'skin': HASH})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'image/png')
        self.assertEqual(r.content, contenido)

    def test_proxy_solo_descarga_de_mojang(self):
        png = respuesta_png()
        with patch('stats.perfiles_minecraft.urlopen', return_value=FakeResponse(png)) as fetch:
            self.assertEqual(obtener_png_skin(HASH), png)
        self.assertEqual(fetch.call_args.args[0].full_url, TEXTURA)

    def test_proxy_no_acepta_tamanos_incompatibles(self):
        with patch('stats.perfiles_minecraft.urlopen', return_value=FakeResponse(respuesta_png(1024, 1024))):
            with self.assertRaises(PerfilNoDisponible):
                obtener_png_skin('b' * 64)

    def test_urls_ajenas_rechazadas(self):
        self.assertEqual(_url_textura('javascript:alert(1)'), '')
        self.assertEqual(_url_textura('https://textures.minecraft.net.evil.test/texture/' + HASH), '')
        self.assertEqual(_url_textura('http://textures.minecraft.net/texture/' + HASH), TEXTURA)

    def test_sesion_mojang_devuelve_skin_personalizada(self):
        raw = {'textures': {'SKIN': {'url': TEXTURA, 'metadata': {'model': 'slim'}}}}
        encoded = base64.b64encode(json.dumps(raw).encode()).decode()
        with patch('stats.perfiles_minecraft.solicitar_json', return_value={
            'properties': [{'name': 'textures', 'value': encoded}]
        }):
            skin = obtener_texturas(UUID)
        self.assertEqual(skin['skin_url'], TEXTURA)
        self.assertEqual(skin['skin_hash'], HASH)
        self.assertEqual(skin['estado_skin'], 'personalizada')
        self.assertEqual(skin['modelo'], 'Slim (brazos finos)')

    def test_fallo_no_se_confunde_con_default(self):
        with patch('stats.perfiles_minecraft.solicitar_json', side_effect=PerfilNoDisponible('429')):
            skin = obtener_texturas(UUID)
        self.assertEqual(skin['estado_skin'], 'no_verificada')

    def test_consulta_no_altera_sqlite(self):
        with patch('stats.perfiles_minecraft.solicitar_json', return_value={'id': UUID, 'name': 'jeb_'}), \
                patch('stats.perfiles_minecraft.obtener_texturas', return_value={
                    'skin_url': TEXTURA, 'skin_hash': HASH,
                    'modelo': 'Clásico (brazos anchos)', 'estado_skin': 'personalizada'
                }):
            perfil = consultar_perfil('jeb_')
        self.assertEqual(perfil['nombre'], 'jeb_')
        self.assertEqual(perfil['skin_hash'], HASH)
        self.assertEqual(perfil['estado_skin'], 'personalizada')

    def test_nombre_invalido(self):
        with patch('stats.perfiles_minecraft.solicitar_json') as api:
            with self.assertRaises(ValueError):
                consultar_perfil('https://bad.example')
        api.assert_not_called()

    def test_mensaje_no_encontrado(self):
        with patch('stats.perfiles_minecraft.consultar_perfil', side_effect=JugadorNoEncontrado):
            r = self.client.get(reverse('stats:perfiles_minecraft'), {'nombre': 'unknown'})
        self.assertContains(r, 'No se encontró una cuenta Java Edition')
