from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import Usuario


class FechaNacimientoMixin:
    """
    Limita la fecha de nacimiento a hoy como máximo:
    en el calendario (atributo max) y en el servidor.
    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if 'fecha_nacimiento' in self.fields:

            self.fields['fecha_nacimiento'].widget.attrs['max'] = (
                timezone.localdate().isoformat()
            )

    def clean_fecha_nacimiento(self):

        fecha = self.cleaned_data.get(
            'fecha_nacimiento'
        )

        if fecha and fecha > timezone.localdate():
            raise forms.ValidationError(
                'La fecha de nacimiento no puede ser posterior a hoy.'
            )

        return fecha


class RegistroUsuarioForm(FechaNacimientoMixin, UserCreationForm):

    email = forms.EmailField(
        required=True
    )

    class Meta:
        model = Usuario

        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'fecha_nacimiento',
            'foto',
            'password1',
            'password2',
        )

        widgets = {
            'fecha_nacimiento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date'
                }
            ),
        }

class PerfilUsuarioForm(FechaNacimientoMixin, forms.ModelForm):

    class Meta:
        model = Usuario

        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'fecha_nacimiento',
            'foto',
        )

        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'foto': 'Foto de perfil',
        }

        widgets = {
            'fecha_nacimiento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date'
                }
            ),
        }