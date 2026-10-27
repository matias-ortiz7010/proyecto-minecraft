from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Jugador, Mod, Servidor, ServidorSnapshot, Speedrun



class StaffTestMixin:
    def setUp(self):
        super().setUp()
        staff = get_user_model().objects.create_user(
            username="staff_de_prueba", password="ClaveDePrueba123!", is_staff=True
        )
        self.client.force_login(staff)


class JugadorABMTests(StaffTestMixin, TestCase):
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


class ServidorABMTests(StaffTestMixin, TestCase):
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


class ModABMTests(StaffTestMixin, TestCase):
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


class SpeedrunABMTests(StaffTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.jugador = Jugador.objects.create(nombre="Steve")

    def datos(self, **overrides):
        data = {
            "jugador": self.jugador.pk,
            "categoria": "Any% Glitchless",
            "tiempo": "06:50.123",
            "fecha": "2026-10-26",
            "version": "1.16.1",
            "verificado": "on",
            "fuente_url": "https://example.org/evidencia",
        }
        data.update(overrides)
        return data

    def test_lista_y_busqueda_por_jugador(self):
        Speedrun.objects.create(jugador=self.jugador, categoria="Any%", tiempo_ms=410000)
        response = self.client.get(reverse("stats:speedruns_gestion"), {"q": "steve"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Steve")
        self.assertContains(response, "06:50")

    def test_alta_convierte_tiempo_a_milisegundos(self):
        response = self.client.post(reverse("stats:speedrun_crear"), self.datos())
        self.assertRedirects(response, reverse("stats:speedruns_gestion"))
        record = Speedrun.objects.get()
        self.assertEqual(record.tiempo_ms, 410123)
        self.assertTrue(record.verificado)

    def test_modificacion_tiempo_y_categoria(self):
        record = Speedrun.objects.create(jugador=self.jugador, categoria="Any%", tiempo_ms=410000)
        response = self.client.post(
            reverse("stats:speedrun_editar", args=[record.pk]),
            self.datos(tiempo="05:59.5", categoria="Random Seed"),
        )
        self.assertRedirects(response, reverse("stats:speedruns_gestion"))
        record.refresh_from_db()
        self.assertEqual(record.tiempo_ms, 359500)
        self.assertEqual(record.categoria, "Random Seed")

    def test_baja_exige_post_y_no_borra_jugador(self):
        record = Speedrun.objects.create(jugador=self.jugador, categoria="Any%", tiempo_ms=410000)
        url = reverse("stats:speedrun_eliminar", args=[record.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Speedrun.objects.filter(pk=record.pk).exists())
        self.assertRedirects(self.client.post(url), reverse("stats:speedruns_gestion"))
        self.assertFalse(Speedrun.objects.filter(pk=record.pk).exists())
        self.assertTrue(Jugador.objects.filter(pk=self.jugador.pk).exists())

    def test_formato_tiempo_invalido_no_crea(self):
        for tiempo in ["06:60", "abc", "00:00", "6:50.1234", "-1:35"]:
            with self.subTest(tiempo=tiempo):
                response = self.client.post(reverse("stats:speedrun_crear"), self.datos(tiempo=tiempo))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
        self.assertFalse(Speedrun.objects.exists())

    def test_no_puede_crear_sin_jugador_valido(self):
        response = self.client.post(reverse("stats:speedrun_crear"), self.datos(jugador=999999))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Speedrun.objects.exists())
        self.assertTrue(response.context["form"].errors)

    def test_edicion_muestra_duracion_existente(self):
        record = Speedrun.objects.create(jugador=self.jugador, categoria="Any%", tiempo_ms=410123)
        response = self.client.get(reverse("stats:speedrun_editar", args=[record.pk]))
        self.assertContains(response, "06:50.123")


    def test_alta_fecha_dia_mes_anio(self):
        from datetime import date
        response = self.client.post(
            reverse("stats:speedrun_crear"), self.datos(fecha="26/10/2026")
        )
        self.assertRedirects(response, reverse("stats:speedruns_gestion"))
        self.assertEqual(Speedrun.objects.get().fecha, date(2026, 10, 26))

    def test_alta_fecha_formato_iso_sigue_funcionando(self):
        from datetime import date
        response = self.client.post(
            reverse("stats:speedrun_crear"), self.datos(fecha="2026-10-26")
        )
        self.assertRedirects(response, reverse("stats:speedruns_gestion"))
        self.assertEqual(Speedrun.objects.get().fecha, date(2026, 10, 26))

    def test_fecha_opcional(self):
        response = self.client.post(
            reverse("stats:speedrun_crear"), self.datos(fecha="")
        )
        self.assertRedirects(response, reverse("stats:speedruns_gestion"))
        self.assertIsNone(Speedrun.objects.get().fecha)

    def test_fecha_invalida_rechazada(self):
        response = self.client.post(
            reverse("stats:speedrun_crear"), self.datos(fecha="31/02/2026")
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Speedrun.objects.exists())
        self.assertIn("fecha", response.context["form"].errors)

    def test_formulario_fecha_con_mini_calendario_y_enlace_a_jugadores(self):
        response = self.client.get(reverse("stats:speedrun_crear"))
        self.assertContains(response, 'name="fecha"')
        self.assertContains(response, 'placeholder="DD/MM/AAAA"')
        self.assertContains(response, "speedrun_calendar.js")
        self.assertContains(response, "Registrar jugador nuevo")
        self.assertNotContains(response, 'name="fecha_year"')

    def test_edicion_fecha_presenta_formato_legible(self):
        from datetime import date
        record = Speedrun.objects.create(
            jugador=self.jugador, categoria="Any%", tiempo_ms=410000,
            fecha=date(2026, 10, 26),
        )
        response = self.client.get(reverse("stats:speedrun_editar", args=[record.pk]))
        self.assertContains(response, 'name="fecha"')
        self.assertContains(response, 'value="26/10/2026"')
