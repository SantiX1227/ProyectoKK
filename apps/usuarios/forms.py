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