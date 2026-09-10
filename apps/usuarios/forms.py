from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


class RegistroUsuarioForm(UserCreationForm):

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

class PerfilUsuarioForm(forms.ModelForm):

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
                attrs={
                    'type': 'date'
                }
            ),
        }