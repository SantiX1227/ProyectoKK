from django import forms

from apps.cagadas.models import Cagada


class FeedFilterForm(forms.Form):

    usuario = forms.CharField(
        required=False,
        label='Usuario'
    )

    calificacion = forms.ChoiceField(
        required=False,
        label='Calificación',
        choices=[]
    )

    categoria = forms.ChoiceField(
        required=False,
        label='Categoría',
        choices=[]
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        calificaciones = (
            Cagada.objects
            .values_list(
                'calificacion',
                flat=True
            )
            .distinct()
            .order_by(
                '-calificacion'
            )
        )

        self.fields['calificacion'].choices = [
            ('', 'Todas')
        ] + [
            (
                str(calificacion),
                str(calificacion)
            )
            for calificacion in calificaciones
        ]

        categorias = (
            Cagada.CATEGORIAS
        )

        self.fields['categoria'].choices = [
            ('', 'Todas')
        ] + list(categorias)