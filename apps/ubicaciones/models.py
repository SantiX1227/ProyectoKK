# Create your models here.
from django.conf import settings
from django.db import models


class Ubicacion(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ubicaciones'
    )

    nombre = models.CharField(
        max_length=100
    )

    tipo = models.CharField(
        max_length=50
    )

    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.nombre} - {self.usuario.username}'