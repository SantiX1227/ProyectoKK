from django.contrib import admin
from .models import Cagada


@admin.register(Cagada)
class CagadaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'usuario',
        'hora_inicio_cagada',
        'hora_final_cagada',
        'duracion',
        'calificacion',
        'categorizacion',
        'color',
        'visible_para_otros',
    )

    list_filter = (
        'visible_para_otros',
        'categorizacion',
        'calificacion',
    )

    search_fields = (
        'usuario__username',
        'observaciones',
        'color',
    )