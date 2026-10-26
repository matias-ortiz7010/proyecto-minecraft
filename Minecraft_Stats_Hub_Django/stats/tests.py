from django.test import TestCase
from django.urls import reverse

from .models import Jugador, Mod, Servidor, ServidorSnapshot


class JugadorABMTests(TestCase):
    def test_lista_jugadores(self):
        Jugador.objects.create(nombre="Alex", pais="Argentina")
        response = self.client.get(reverse("stats:jugadores_gestion"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alex")

    def test_alta_jugador(self):
        response = self.client.post(
            reverse("stats:jugador_crear"),
            {"nombre": "Steve", "uuid": "", "pais": "Argentina", "skin_url": ""},
        )
        self.assertRedirects(response, reverse("stats:jugadores_gestion"))
        self.assertTrue(Jugador.objects.filter(nombre="Steve").exists())

    def test_modificacion_jugador(self):
        jugador = Jugador.objects.create(nombre="Steve")
        response = self.client.post(
            reverse("stats:jugador_editar", args=[jugador.pk]),
            {"nombre": "Steve2", "uuid": "", "pais": "", "skin_url": ""},
        )
        self.assertRedirects(response, reverse("stats:jugadores_gestion"))
        jugador.refresh_from_db()
        self.assertEqual(jugador.nombre, "Steve2")

    def test_baja_jugador(self):
        jugador = Jugador.objects.create(nombre="Steve")
        response = self.client.post(reverse("stats:jugador_eliminar", args=[jugador.pk]))
        self.assertRedirects(response, reverse("stats:jugadores_gestion"))
        self.assertFalse(Jugador.objects.filter(pk=jugador.pk).exists())


class ServidorABMTests(TestCase):
    def test_lista_y_busqueda_servidores(self):
        Servidor.objects.create(nombre="Servidor de prueba", ip="play.prueba.test", pais="Argentina")
        response = self.client.get(reverse("stats:servidores_gestion"), {"q": "prueba"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Servidor de prueba")

    def test_alta_servidor(self):
        response = self.client.post(reverse("stats:servidor_crear"), {
            "nombre": "Survival", "ip": "play.survival.test", "pais": "Argentina",
            "jugadores": 12, "online": "on",
        })
        self.assertRedirects(response, reverse("stats:servidores_gestion"))
        self.assertTrue(Servidor.objects.filter(ip="play.survival.test", jugadores=12, online=True).exists())

    def test_modificacion_servidor(self):
        servidor = Servidor.objects.create(nombre="Viejo", ip="viejo.test")
        response = self.client.post(reverse("stats:servidor_editar", args=[servidor.pk]), {
            "nombre": "Nuevo", "ip": "nuevo.test", "pais": "Argentina",
            "jugadores": 6, "online": "",
        })
        self.assertRedirects(response, reverse("stats:servidores_gestion"))
        servidor.refresh_from_db()
        self.assertEqual(servidor.nombre, "Nuevo")
        self.assertFalse(servidor.online)

    def test_eliminar_servidor_pide_post_y_elimina_historial(self):
        servidor = Servidor.objects.create(nombre="Demo", ip="demo.test")
        ServidorSnapshot.objects.create(servidor=servidor, jugadores=5)
        pagina = reverse("stats:servidor_eliminar", args=[servidor.pk])
        self.assertEqual(self.client.get(pagina).status_code, 200)
        self.assertTrue(Servidor.objects.filter(pk=servidor.pk).exists())
        self.assertRedirects(self.client.post(pagina), reverse("stats:servidores_gestion"))
        self.assertFalse(Servidor.objects.filter(pk=servidor.pk).exists())
        self.assertFalse(ServidorSnapshot.objects.filter(servidor_id=servidor.pk).exists())

    def test_ip_no_duplicada(self):
        Servidor.objects.create(nombre="Uno", ip="mismo.test")
        response = self.client.post(reverse("stats:servidor_crear"), {
            "nombre": "Dos", "ip": "mismo.test", "pais": "", "jugadores": 0, "online": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servidor.objects.filter(ip="mismo.test").count(), 1)


class ModABMTests(TestCase):
    def test_lista_y_busqueda_por_autor(self):
        Mod.objects.create(nombre="Sodium", autor="CaffeineMC", version="1.21")
        Mod.objects.create(nombre="Iris", autor="Otro")
        response = self.client.get(reverse("stats:mods_gestion"), {"q": "caffeinemc"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sodium")
        self.assertNotContains(response, "Iris")

    def test_alta_mod(self):
        response = self.client.post(reverse("stats:mod_crear"), {
            "nombre": "Create", "autor": "simibubi", "version": "1.20",
            "descargas": 1200, "url": "https://example.com/create",
        })
        self.assertRedirects(response, reverse("stats:mods_gestion"))
        self.assertTrue(Mod.objects.filter(nombre="Create", descargas=1200).exists())

    def test_modificacion_mod(self):
        mod = Mod.objects.create(nombre="ModViejo")
        response = self.client.post(reverse("stats:mod_editar", args=[mod.pk]), {
            "nombre": "ModNuevo", "autor": "Autor", "version": "1.21",
            "descargas": 50, "url": "",
        })
        self.assertRedirects(response, reverse("stats:mods_gestion"))
        mod.refresh_from_db()
        self.assertEqual(mod.nombre, "ModNuevo")
        self.assertEqual(mod.descargas, 50)

    def test_baja_exige_post_y_confirmacion(self):
        mod = Mod.objects.create(nombre="Borrable")
        url = reverse("stats:mod_eliminar", args=[mod.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Mod.objects.filter(pk=mod.pk).exists())
        self.assertRedirects(self.client.post(url), reverse("stats:mods_gestion"))
        self.assertFalse(Mod.objects.filter(pk=mod.pk).exists())

    def test_nombre_duplicado_invalido(self):
        Mod.objects.create(nombre="Sodium")
        response = self.client.post(reverse("stats:mod_crear"), {
            "nombre": "Sodium", "autor": "", "version": "",
            "descargas": 0, "url": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Mod.objects.filter(nombre="Sodium").count(), 1)
        self.assertTrue(response.context["form"].errors)

    def test_descargas_negativas_invalidas(self):
        response = self.client.post(reverse("stats:mod_crear"), {
            "nombre": "Negativo", "autor": "", "version": "",
            "descargas": -5, "url": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Mod.objects.filter(nombre="Negativo").exists())
        self.assertTrue(response.context["form"].errors)

    def test_url_invalida(self):
        response = self.client.post(reverse("stats:mod_crear"), {
            "nombre": "URLMala", "autor": "", "version": "",
            "descargas": 0, "url": "esto no es url",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Mod.objects.filter(nombre="URLMala").exists())
        self.assertTrue(response.context["form"].errors)
