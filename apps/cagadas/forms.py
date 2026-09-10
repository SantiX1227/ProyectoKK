from django import forms
from .models import Cagada
from apps.ubicaciones.models import Ubicacion

class CagadaForm(forms.ModelForm):

    class Meta:
        model = Cagada

        fields = (
            'ubicacion',
            'hora_inicio_cagada',
            'hora_final_cagada',
            'calificacion',
            'categorizacion',
            'color',
            'observaciones',
            'visible_para_otros',
        )

        labels = {
            'ubicacion': 'Ubicación',
            'hora_inicio_cagada': 'Hora de inicio',
            'hora_final_cagada': 'Hora final',
            'calificacion': 'Calificación',
            'categorizacion': 'Categorización',
            'color': 'Color',
            'observaciones': 'Observaciones',
            'visible_para_otros': 'Visible para otros usuarios',
        }

        widgets = {
            'hora_inicio_cagada': forms.HiddenInput(),

            'hora_final_cagada': forms.HiddenInput(),

            'color': forms.TextInput(
                attrs={
                    'type': 'color'
                }
            ),

            'observaciones': forms.Textarea(
                attrs={
                    'rows': 4
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        usuario = kwargs.pop('usuario', None)

        super().__init__(*args, **kwargs)

        if usuario is not None:

            self.fields['ubicacion'].queryset = (
                Ubicacion.objects.filter(
                    usuario=usuario
                )
            )

    def clean(self):

        cleaned_data = super().clean()

        hora_inicio = cleaned_data.get(
            'hora_inicio_cagada'
        )

        hora_final = cleaned_data.get(
            'hora_final_cagada'
        )

        if not hora_inicio:
            raise forms.ValidationError(
                'Debes iniciar la cagada antes de registrarla.'
            )

        if not hora_final:
            raise forms.ValidationError(
                'Debes terminar la cagada antes de registrarla.'
            )

        if hora_final <= hora_inicio:
            raise forms.ValidationError(
                'La hora final debe ser posterior a la hora de inicio.'
            )

        return cleaned_data