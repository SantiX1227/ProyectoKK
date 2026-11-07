from django import forms
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': (
                'foto',
                'fecha_nacimiento',
            ),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': (
                'email',
                'foto',
                'fecha_nacimiento',
            ),
        }),
    )

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
    )

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )



class LoginAdminEmailForm(AdminAuthenticationForm):
    """
    Login del admin por correo: el backend EmailBackend
    autentica con el email, así que el campo debe pedirlo.
    """

    error_messages = {
        **AdminAuthenticationForm.error_messages,
        'invalid_login': (
            'Introduce el correo y la contraseña de una cuenta '
            'con acceso al panel de administración.'
        ),
    }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        campo = self.fields['username']

        campo.label = 'Correo electrónico'

        campo.max_length = 254

        campo.widget = forms.EmailInput(
            attrs={
                'autofocus': True,
                'autocomplete': 'email',
                'maxlength': 254,
            }
        )


admin.site.login_form = LoginAdminEmailForm    