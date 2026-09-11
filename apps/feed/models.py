from django.conf import settings
from django.db import models

from apps.cagadas.models import Cagada


class Reaccion(models.Model):

    TIPOS_REACCION = [
        ('UY_PA', '💀 Uy pa'),
        ('DURISIMO', '🔥 Durísimo hermano'),
        ('GG', '🤝 GG'),
        ('MIERDA', '💩 Una mierda'),
        ('MEDIQUESE', '🤒 Medíquese'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reacciones'
    )

    cagada = models.ForeignKey(
        Cagada,
        on_delete=models.CASCADE,
        related_name='reacciones'
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_REACCION
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'cagada'],
                name='una_reaccion_por_usuario_cagada'
            )
        ]

    def __str__(self):
        return f'{self.usuario.username} - {self.get_tipo_display()}'