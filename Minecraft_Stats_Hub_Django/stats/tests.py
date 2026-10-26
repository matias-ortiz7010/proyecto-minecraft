from django.test import TestCase
from django.urls import reverse

from .models import Jugador


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
