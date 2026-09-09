from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    foto = models.ImageField(
        upload_to='usuarios/',
        null=True,
        blank=True
    )

    fecha_nacimiento = models.DateField(
        null=True,
        blank=True
    )