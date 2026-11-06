from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Cagada
from apps.ubicaciones.models import Ubicacion


# Límites para validar las horas que envía el cronómetro
DURACION_MAXIMA = timedelta(hours=2)

# Margen por si el reloj del dispositivo va un poco adelantado
TOLERANCIA_RELOJ = timedelta(minutes=2)

# Tiempo máximo entre terminar la cagada y registrarla
ANTIGUEDAD_MAXIMA = timedelta(hours=1)


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

        ahora = timezone.now()

        if hora_final > ahora + TOLERANCIA_RELOJ:
            raise forms.ValidationError(
                'La hora final no puede estar en el futuro.'
            )

        if hora_final - hora_inicio > DURACION_MAXIMA:
            raise forms.ValidationError(
                'La duración no puede superar las 2 horas.'
            )

        if ahora - hora_final > ANTIGUEDAD_MAXIMA:
            raise forms.ValidationError(
                'Esta cagada terminó hace demasiado tiempo. '
                'Reinicia el cronómetro y vuelve a registrarla.'
            )

        return cleaned_data

        
class EditarCagadaForm(forms.ModelForm):

    class Meta:
        model = Cagada

        fields = (
            'ubicacion',
            'calificacion',
            'categorizacion',
            'color',
            'observaciones',
            'visible_para_otros',
        )

        labels = {
            'ubicacion': 'Ubicación',
            'calificacion': 'Calificación',
            'categorizacion': 'Categorización',
            'color': 'Color',
            'observaciones': 'Observaciones',
            'visible_para_otros': (
                'Visible para otros usuarios'
            ),
        }

        widgets = {
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

        usuario = kwargs.pop(
            'usuario',
            None
        )

        super().__init__(
            *args,
            **kwargs
        )

        if usuario is not None:

            self.fields['ubicacion'].queryset = (
                Ubicacion.objects.filter(
                    usuario=usuario
                )
            )