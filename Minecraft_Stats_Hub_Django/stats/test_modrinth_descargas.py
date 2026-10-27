"""Pruebas de enlaces directos Modrinth sin llamadas externas."""
from unittest.mock import patch
from django.test import SimpleTestCase
from django.urls import reverse
from .modrinth_externos import _archivo_principal, _url_descarga_modrinth

GOOD = "https://cdn.modrinth.com/data/AABBCCDD/versions/1234/sodium.jar"


class ModrinthDownloadsTest(SimpleTestCase):
    def test_url_cdn_oficial(self):
        self.assertEqual(_url_descarga_modrinth(GOOD), GOOD)
        for url in (
            "http://cdn.modrinth.com/data/id/versions/1234/mod.jar",
            "https://cdn.modrinth.com.evil.example/data/id/versions/1234/mod.jar",
            "https://evil.example/data/id/versions/1234/mod.jar",
            "javascript:alert(1)",
            "https://cdn.modrinth.com@evil.example/data/id/versions/1234/mod.jar",
            "https://cdn.modrinth.com/data/id/versions/1234/file.exe",
            "https://cdn.modrinth.com:8443/data/id/versions/1234/mod.jar",
        ):
            with self.subTest(url=url):
                self.assertEqual(_url_descarga_modrinth(url), "")

    def test_elige_principal_no_archivo_de_fuentes(self):
        v = {"files": [
            {"url": "https://cdn.modrinth.com/data/id/versions/a/sources.jar", "filename": "example-sources.jar"},
            {"url": GOOD, "filename": "sodium.jar", "primary": True,
             "hashes": {"sha512": "a" * 128}},
        ]}
        chosen = _archivo_principal(v)
        self.assertEqual(chosen["url"], GOOD)
        self.assertEqual(chosen["nombre"], "sodium.jar")
        self.assertEqual(chosen["sha512"], "a" * 128)

    def test_no_enlaza_cdn_ajeno(self):
        self.assertIsNone(_archivo_principal({"files": [
            {"url": "https://other.example/mod.jar", "filename": "mod.jar", "primary": True}
        ]}))

    def test_detalle_muestra_descarga_sin_guardar_datos(self):
        info = {"project_type": "mod", "title": "Sodium", "description": "Optimizador", "downloads": 100}
        releases = [{
            "id": "AABBCCDD", "version_number": "0.6.5", "name": "Sodium 0.6.5", 
            "date_published": "2026-01-01T00:00:00Z", "game_versions": ["1.21.1"],
            "loaders": ["fabric"], "downloads": 45,
            "files": [{"filename": "sodium.jar", "url": GOOD, "primary": True}],
        }]
        with patch('stats.modrinth_externos.solicitar_json', side_effect=[info, releases]):
            r = self.client.get(reverse('stats:mod_externo_detalle', kwargs={'slug': 'sodium'}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Descargar archivo")
        self.assertContains(r, GOOD)
        self.assertContains(r, "Ver versión en Modrinth")

    def test_mod_sin_archivo_valido_tiene_fallback(self):
        info = {"project_type": "mod", "title": "Sodium", "description": "", "downloads": 1}
        releases = [{"id": "AABBCCDD", "version_number": "0.6.5", "files": [
            {"filename": "evil.jar", "url": "https://evil.example/evil.jar"}
        ]}]
        with patch('stats.modrinth_externos.solicitar_json', side_effect=[info, releases]):
            r = self.client.get(reverse('stats:mod_externo_detalle', kwargs={'slug': 'sodium'}))
        self.assertContains(r, "Archivo directo no disponible")
        self.assertNotContains(r, "evil.example")
