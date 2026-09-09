from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Cagada(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cagadas'
    )

    hora_inicio_cagada = models.DateTimeField()

    hora_final_cagada = models.DateTimeField()

    duracion = models.DurationField(
        null=True,
        blank=True
    )

    calificacion = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]
    )

    observaciones = models.TextField(
        blank=True
    )

    categorizacion = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    color = models.CharField(
        max_length=7
    )

    visible_para_otros = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f'Cagada de {self.usuario.username} - {self.hora_inicio_cagada}'