"""Pruebas del tablero público y sus cálculos de historial."""
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Servidor, ServidorSnapshot


class AnaliticaServidoresTests(TestCase):
    def setUp(self):
        self.url = reverse("stats:estadisticas_servidores")
        self.servidor = Servidor.objects.create(nombre="Test Analytics", ip="analytics.example.com")

    def crear_muestra(self, jugadores, online, horas_atras=0):
        muestra = ServidorSnapshot.objects.create(
            servidor=self.servidor, jugadores=jugadores, online=online
        )
        if horas_atras:
            ServidorSnapshot.objects.filter(pk=muestra.pk).update(
                registrado_en=timezone.now() - timedelta(hours=horas_atras)
            )
        return muestra

    def test_dashboard_publico_sin_login(self):
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Estadísticas de servidores")
        self.assertContains(respuesta, "Todavía no hay mediciones")

    def test_calculos_solo_muestras_online(self):
        self.crear_muestra(20, True, 2)
        self.crear_muestra(40, True, 1)
        self.crear_muestra(0, False)
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.context["minimo"], 20)
        self.assertEqual(respuesta.context["maximo"], 40)
        self.assertEqual(respuesta.context["promedio"], 30)
        self.assertEqual(respuesta.context["muestras_online"], 2)
        self.assertEqual(respuesta.context["muestras"], 3)
        self.assertEqual(respuesta.context["puntos"][-1]["jugadores"], None)

    def test_filtrado_por_periodo(self):
        self.crear_muestra(40, True, 30)
        self.crear_muestra(10, True, 1)
        respuesta = self.client.get(self.url, {"horas": 6})
        self.assertEqual(respuesta.context["muestras"], 1)
        self.assertEqual(respuesta.context["promedio"], 10)
        respuesta = self.client.get(self.url, {"horas": "cualquier cosa"})
        self.assertEqual(respuesta.context["horas"], 24)

    def test_filtrado_por_servidor(self):
        otro = Servidor.objects.create(nombre="Segundo", ip="segundo.example.com")
        ServidorSnapshot.objects.create(servidor=otro, jugadores=200, online=True)
        self.crear_muestra(5, True)
        respuesta = self.client.get(self.url, {"servidor": otro.pk})
        self.assertEqual(respuesta.context["servidor"].pk, otro.pk)
        self.assertEqual(respuesta.context["maximo"], 200)

    def test_no_modifica_tablas(self):
        self.crear_muestra(10, True)
        antes = ServidorSnapshot.objects.count()
        self.client.get(self.url)
        self.assertEqual(ServidorSnapshot.objects.count(), antes)

    def test_sin_servidores(self):
        Servidor.objects.all().delete()
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Todavía no hay servidores")
