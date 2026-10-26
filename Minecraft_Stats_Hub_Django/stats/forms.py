from django import forms

from .models import Jugador, Mod, Servidor


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
