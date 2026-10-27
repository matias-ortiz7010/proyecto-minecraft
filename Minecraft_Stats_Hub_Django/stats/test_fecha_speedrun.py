from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Jugador, Speedrun


class FechaSpeedrunCalendarioTests(TestCase):
    def setUp(self):
        staff = get_user_model().objects.create_user(
            username="staff_fecha", password="ClaveDePrueba123!", is_staff=True
        )
        self.client.force_login(staff)
        self.jugador = Jugador.objects.create(nombre="AlexFechaPrueba")

    def datos(self, **overrides):
        values = {
            "jugador": self.jugador.pk,
            "categoria": "Any% Random Seed",
            "tiempo": "06:50.123",
            "fecha": "26/10/2026",
            "version": "1.16.1", "verificado": "", "fuente_url": "",
        }
        values.update(overrides)
        return values

    def test_calendario_en_formulario(self):
        response = self.client.get(reverse("stats:speedrun_crear"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-sr-datepicker')
        self.assertContains(response, 'name="fecha"')
        self.assertContains(response, 'speedrun_calendar.js')
        self.assertNotContains(response, 'name="fecha_year"')

    def test_crear_fecha_seleccionada(self):
        response = self.client.post(reverse("stats:speedrun_crear"), self.datos())
        self.assertRedirects(response, reverse("stats:speedruns_gestion"))
        self.assertEqual(Speedrun.objects.get().fecha, date(2026, 10, 26))

    def test_editar_fecha_existente_y_poder_cambiarla(self):
        record = Speedrun.objects.create(
            jugador=self.jugador, categoria="Any%", tiempo_ms=410000, fecha=date(2025, 1, 1)
        )
        url = reverse("stats:speedrun_editar", args=[record.pk])
        response = self.client.get(url)
        self.assertContains(response, 'value="01/01/2025"')
        response = self.client.post(url, self.datos(fecha="04/06/2026"))
        self.assertRedirects(response, reverse("stats:speedruns_gestion"))
        record.refresh_from_db()
        self.assertEqual(record.fecha, date(2026, 6, 4))

    def test_fecha_vacia_permitida(self):
        response = self.client.post(reverse("stats:speedrun_crear"), self.datos(fecha=""))
        self.assertRedirects(response, reverse("stats:speedruns_gestion"))
        self.assertIsNone(Speedrun.objects.get().fecha)

    def test_fecha_invalida_rechazada(self):
        response = self.client.post(reverse("stats:speedrun_crear"), self.datos(fecha="31/02/2026"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("fecha", response.context["form"].errors)
        self.assertFalse(Speedrun.objects.exists())

    def test_fecha_iso_antigua_sigue_aceptada(self):
        response = self.client.post(reverse("stats:speedrun_crear"), self.datos(fecha="2026-10-26"))
        self.assertRedirects(response, reverse("stats:speedruns_gestion"))
        self.assertEqual(Speedrun.objects.get().fecha, date(2026, 10, 26))

    def test_fecha_bisiesta(self):
        response = self.client.post(reverse("stats:speedrun_crear"), self.datos(fecha="29/02/2024"))
        self.assertRedirects(response, reverse("stats:speedruns_gestion"))
        self.assertEqual(Speedrun.objects.get().fecha, date(2024, 2, 29))
