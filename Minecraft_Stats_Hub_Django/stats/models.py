from django.db import models


class Jugador(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    uuid = models.CharField(max_length=36, unique=True, null=True, blank=True)
    skin_url = models.URLField(blank=True)
    pais = models.CharField(max_length=50, blank=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Speedrun(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name="speedruns")
    categoria = models.CharField(max_length=100)
    tiempo_ms = models.PositiveBigIntegerField(help_text="Tiempo total en milisegundos")
    fecha = models.DateField(null=True, blank=True)
    version = models.CharField(max_length=30, blank=True)
    verificado = models.BooleanField(default=False)
    fuente_url = models.URLField(blank=True)

    class Meta:
        ordering = ["tiempo_ms", "fecha"]

    def __str__(self):
        return f"{self.jugador} - {self.categoria} - {self.tiempo_formateado}"

    @property
    def tiempo_formateado(self):
        total_seconds = self.tiempo_ms // 1000
        minutes, seconds = divmod(total_seconds, 60)
        millis = self.tiempo_ms % 1000
        if millis:
            return f"{minutes:02d}:{seconds:02d}.{millis:03d}"
        return f"{minutes:02d}:{seconds:02d}"


class PvP(models.Model):
    jugador = models.OneToOneField(Jugador, on_delete=models.CASCADE, related_name="pvp")
    victorias = models.PositiveIntegerField(default=0)
    derrotas = models.PositiveIntegerField(default=0)
    kills = models.PositiveIntegerField(default=0)
    racha = models.PositiveIntegerField(default=0)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estadística PvP"
        verbose_name_plural = "Estadísticas PvP"

    @property
    def winrate(self):
        total = self.victorias + self.derrotas
        return round((self.victorias / total) * 100, 2) if total else 0

    def __str__(self):
        return f"PvP de {self.jugador}"


class Mod(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    autor = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=30, blank=True)
    descargas = models.PositiveBigIntegerField(default=0)
    url = models.URLField(blank=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-descargas", "nombre"]

    def __str__(self):
        return self.nombre


class Servidor(models.Model):
    nombre = models.CharField(max_length=100)
    ip = models.CharField(max_length=255, unique=True)
    pais = models.CharField(max_length=50, blank=True)
    jugadores = models.PositiveIntegerField(default=0)
    online = models.BooleanField(default=False)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-jugadores", "nombre"]

    def __str__(self):
        return self.nombre


class ServidorSnapshot(models.Model):
    servidor = models.ForeignKey(Servidor, on_delete=models.CASCADE, related_name="historial")
    jugadores = models.PositiveIntegerField(default=0)
    online = models.BooleanField(default=False)
    registrado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-registrado_en"]
        indexes = [models.Index(fields=["servidor", "registrado_en"])]

    def __str__(self):
        return f"{self.servidor} - {self.jugadores} - {self.registrado_en:%Y-%m-%d %H:%M}"
