from django import forms

from .models import Ubicacion


class UbicacionForm(forms.ModelForm):

    class Meta:
        model = Ubicacion

        fields = (
            'nombre',
            'tipo',
            'latitud',
            'longitud',
        )

        labels = {
            'nombre': 'Nombre',
            'tipo': 'Tipo',
            'latitud': 'Latitud',
            'longitud': 'Longitud',
        }

        widgets = {
            'latitud': forms.NumberInput(
                attrs={
                    'step': 'any'
                }
            ),

            'longitud': forms.NumberInput(
                attrs={
                    'step': 'any'
                }
            ),
        }