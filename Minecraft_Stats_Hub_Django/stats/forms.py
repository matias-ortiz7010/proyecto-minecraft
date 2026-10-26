from django import forms

from .models import Jugador


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
