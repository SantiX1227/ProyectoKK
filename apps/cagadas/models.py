from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Cagada(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cagadas'
    )
    ubicacion = models.ForeignKey(
        'ubicaciones.Ubicacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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


    CATEGORIAS = [
        (1, 'Normal'),
        (2, 'Rápida'),
        (3, 'Larga'),
        (4, 'Difícil'),
        (5, 'Tranquila'),
        (6, 'Explosiva'),
        (7, 'Interrumpida'),
        (8, 'Urgente'),
        (9, 'Satisfactoria'),
        (10, 'Problemática'),
    ]
    
    categorizacion = models.PositiveSmallIntegerField(
        choices=CATEGORIAS,
        default=1
    )

    color = models.CharField(
        max_length=7
    )

    visible_para_otros = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f'Cagada de {self.usuario.username} - {self.hora_inicio_cagada}'