import re

from django import forms

from .models import Jugador, Mod, Servidor, Speedrun


class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = ["nombre", "uuid", "pais", "skin_url"]
        labels = {
            "nombre": "Nombre",
            "uuid": "UUID",
            "pais": "País",
            "skin_url": "URL de skin",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej: Dream", "autofocus": True}),
            "uuid": forms.TextInput(attrs={"placeholder": "UUID opcional"}),
            "pais": forms.TextInput(attrs={"placeholder": "Ej: Argentina"}),
            "skin_url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def clean_nombre(self):
        return self.cleaned_data["nombre"].strip()

    def clean_uuid(self):
        value = self.cleaned_data.get("uuid")
        return value.strip() if value else value

    def clean_pais(self):
        value = self.cleaned_data.get("pais", "")
        return value.strip()


class ServidorForm(forms.ModelForm):
    class Meta:
        model = Servidor
        fields = ["nombre", "ip", "pais", "jugadores", "online"]
        labels = {
            "nombre": "Nombre del servidor",
            "ip": "Dirección del servidor (IP o dominio)",
            "pais": "País",
            "jugadores": "Jugadores conectados (dato manual)",
            "online": "En línea (dato manual)",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej: Mi Servidor"}),
            "ip": forms.TextInput(attrs={"placeholder": "Ej: play.ejemplo.net"}),
            "pais": forms.TextInput(attrs={"placeholder": "Ej: Argentina"}),
            "jugadores": forms.NumberInput(attrs={"min": 0}),
        }

    def clean_nombre(self):
        return self.cleaned_data["nombre"].strip()

    def clean_ip(self):
        return self.cleaned_data["ip"].strip()

    def clean_pais(self):
        return self.cleaned_data.get("pais", "").strip()


class ModForm(forms.ModelForm):
    class Meta:
        model = Mod
        fields = ["nombre", "autor", "version", "descargas", "url"]
        labels = {
            "nombre": "Nombre del mod",
            "autor": "Autor o equipo",
            "version": "Versión compatible",
            "descargas": "Descargas registradas (dato manual)",
            "url": "URL oficial del mod (opcional)",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej: Sodium"}),
            "autor": forms.TextInput(attrs={"placeholder": "Ej: CaffeineMC"}),
            "version": forms.TextInput(attrs={"placeholder": "Ej: 1.21.1"}),
            "descargas": forms.NumberInput(attrs={"min": 0}),
            "url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def clean_nombre(self):
        return self.cleaned_data["nombre"].strip()

    def clean_autor(self):
        return self.cleaned_data.get("autor", "").strip()

    def clean_version(self):
        return self.cleaned_data.get("version", "").strip()


class SpeedrunForm(forms.ModelForm):
    # El campo visible es mm:ss[.mmm]; el modelo guarda milisegundos enteros.
    tiempo = forms.CharField(
        label="Tiempo (mm:ss o mm:ss.mmm)",
        help_text="Ejemplos: 06:50 o 06:50.123. Los segundos van de 00 a 59.",
        widget=forms.TextInput(attrs={"placeholder": "Ej: 06:50.123", "inputmode": "text"}),
    )

    # Campo editable de texto: el mini calendario escribe DD/MM/AAAA aquí.
    # Django valida los días/meses reales (incluidos años bisiestos).
    # Sin JavaScript también se puede escribir la fecha manualmente.
    fecha = forms.DateField(
        label="Fecha del récord (opcional)",
        required=False,
        input_formats=["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"],
        help_text="Elegí una fecha en el calendario o escribí DD/MM/AAAA. Podés dejarla vacía.",
        widget=forms.TextInput(attrs={
            "placeholder": "DD/MM/AAAA",
            "inputmode": "numeric",
            "autocomplete": "off",
        }),
        error_messages={"invalid": "Ingresá una fecha válida en formato DD/MM/AAAA."},
    )

    class Meta:
        model = Speedrun
        fields = ["jugador", "categoria", "fecha", "version", "verificado", "fuente_url"]
        labels = {
            "jugador": "Jugador existente",
            "categoria": "Categoría",
            "fecha": "Fecha del récord (opcional)",
            "version": "Versión de Minecraft",
            "verificado": "Marcado como verificado (manual)",
            "fuente_url": "Enlace a la fuente o evidencia",
        }
        widgets = {
            "categoria": forms.TextInput(attrs={"placeholder": "Ej: Any% Glitchless - Random Seed"}),
            "version": forms.TextInput(attrs={"placeholder": "Ej: 1.16.1"}),
            "fuente_url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["tiempo"].initial = self.instance.tiempo_formateado
            if self.instance.fecha:
                self.initial["fecha"] = self.instance.fecha.strftime("%d/%m/%Y")
        self.fields["jugador"].queryset = Jugador.objects.order_by("nombre")
        self.order_fields(["jugador", "categoria", "tiempo", "fecha", "version", "verificado", "fuente_url"])

    def clean_categoria(self):
        return self.cleaned_data["categoria"].strip()

    def clean_version(self):
        return self.cleaned_data.get("version", "").strip()

    def clean_tiempo(self):
        raw = self.cleaned_data["tiempo"].strip()
        match = re.fullmatch(r"(\d{1,5}):([0-5]\d)(?:\.(\d{1,3}))?", raw)
        if not match:
            raise forms.ValidationError("Usá minutos:segundos o minutos:segundos.milisegundos (ej: 06:50.123).")
        minutes, seconds = int(match[1]), int(match[2])
        millis = int((match[3] or "").ljust(3, "0")) if match[3] else 0
        total_ms = (minutes * 60 + seconds) * 1000 + millis
        if total_ms == 0:
            raise forms.ValidationError("El tiempo debe ser mayor que cero.")
        return total_ms

    def save(self, commit=True):
        record = super().save(commit=False)
        record.tiempo_ms = self.cleaned_data["tiempo"]
        if commit:
            record.save()
            self.save_m2m()
        return record
