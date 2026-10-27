from django import forms
from django.contrib.auth.forms import AuthenticationForm


class StaffLoginForm(AuthenticationForm):
    """Solo permite entrar al panel con cuentas que tengan is_staff=True."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                "Esta cuenta no tiene permisos para administrar Minecraft Stats Hub.",
                code="sin_permisos",
            )
