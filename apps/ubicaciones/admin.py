from django.contrib import admin
from .models import Ubicacion


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'usuario',
        'nombre',
        'tipo',
        'latitud',
        'longitud',
        'fecha_creacion',
    )

    list_filter = (
        'tipo',
        'fecha_creacion',
    )

    search_fields = (
        'usuario__username',
        'nombre',
        'tipo',
    )