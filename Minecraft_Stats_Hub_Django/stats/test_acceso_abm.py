from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Jugador, Mod, Servidor, Speedrun


class AccesoABMTests(TestCase):
    def setUp(self):
        self.jugador = Jugador.objects.create(nombre="SteveAcceso")
        self.mod = Mod.objects.create(nombre="ModAcceso")
        self.servidor = Servidor.objects.create(nombre="ServidorAcceso", ip="server.test")
        self.speedrun = Speedrun.objects.create(
            jugador=self.jugador, categoria="Any%", tiempo_ms=500000
        )
        self.staff = get_user_model().objects.create_user(
            username="staff_acceso", password="ClaveDePrueba123!", is_staff=True
        )
        self.normal = get_user_model().objects.create_user(
            username="visitante_acceso", password="ClaveDePrueba123!", is_staff=False
        )
        self.listados = [
            "stats:jugadores_gestion", "stats:servidores_gestion",
            "stats:mods_gestion", "stats:speedruns_gestion",
        ]
        self.altas = [
            "stats:jugador_crear", "stats:servidor_crear",
            "stats:mod_crear", "stats:speedrun_crear",
        ]
        self.operaciones = [
            ("stats:jugador_editar", self.jugador.pk),
            ("stats:jugador_eliminar", self.jugador.pk),
            ("stats:servidor_editar", self.servidor.pk),
            ("stats:servidor_eliminar", self.servidor.pk),
            ("stats:mod_editar", self.mod.pk),
            ("stats:mod_eliminar", self.mod.pk),
            ("stats:speedrun_editar", self.speedrun.pk),
            ("stats:speedrun_eliminar", self.speedrun.pk),
        ]

    def test_visitante_puede_ver_web_y_apis(self):
        for name in ["stats:index", "stats:api_resumen", "stats:api_mods", "stats:api_servidores", "stats:api_speedruns"]:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_anonimo_redirigido_desde_todos_los_abm(self):
        for name in self.listados + self.altas:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("stats:gestion_login"), response.url)
        for name, pk in self.operaciones:
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=[pk]))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("stats:gestion_login"), response.url)

    def test_anonimo_no_puede_crear_ni_borrar_registros(self):
        response = self.client.post(reverse("stats:jugador_crear"), {
            "nombre": "Intruso", "uuid": "", "pais": "", "skin_url": "",
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Jugador.objects.filter(nombre="Intruso").exists())
        for name, pk in self.operaciones:
            if name.endswith("eliminar"):
                with self.subTest(name=name):
                    self.assertEqual(self.client.post(reverse(name, args=[pk])).status_code, 302)
        self.assertTrue(Jugador.objects.filter(pk=self.jugador.pk).exists())
        self.assertTrue(Servidor.objects.filter(pk=self.servidor.pk).exists())
        self.assertTrue(Mod.objects.filter(pk=self.mod.pk).exists())
        self.assertTrue(Speedrun.objects.filter(pk=self.speedrun.pk).exists())

    def test_cuenta_comun_no_puede_iniciar_sesion_en_panel(self):
        response = self.client.post(reverse("stats:gestion_login"), {
            "username": "visitante_acceso", "password": "ClaveDePrueba123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no tiene permisos")
        self.assertNotIn("_auth_user_id", self.client.session)
        self.client.force_login(self.normal)
        self.assertEqual(self.client.get(reverse("stats:jugadores_gestion")).status_code, 302)

    def test_staff_puede_entrar_y_salir(self):
        url = reverse("stats:gestion_login")
        listado = reverse("stats:jugadores_gestion")
        response = self.client.post(url, {
            "username": "staff_acceso", "password": "ClaveDePrueba123!", "next": listado,
        })
        self.assertRedirects(response, listado)
        self.assertEqual(self.client.get(listado).status_code, 200)
        self.assertRedirects(self.client.post(reverse("stats:gestion_logout")), reverse("stats:index"))
        self.assertEqual(self.client.get(listado).status_code, 302)

    def test_staff_puede_crear_jugador(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse("stats:jugador_crear"), {
            "nombre": "NuevoPorStaff", "uuid": "", "pais": "", "skin_url": "",
        })
        self.assertRedirects(response, reverse("stats:jugadores_gestion"))
        self.assertTrue(Jugador.objects.filter(nombre="NuevoPorStaff").exists())

    def test_login_tiene_token_csrf(self):
        response = self.client.get(reverse("stats:gestion_login"))
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
