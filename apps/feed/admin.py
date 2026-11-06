from django.contrib import admin
from .models import Reaccion


@admin.register(Reaccion)
class ReaccionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'usuario',
        'cagada',
        'tipo',
        'fecha',
    )

    list_filter = (
        'tipo',
        'fecha',
    )

    search_fields = (
        'usuario__username',
        'cagada__usuario__username',
    )

    list_select_related = (
        'usuario',
        'cagada__usuario',
    )

    raw_id_fields = (
        'usuario',
        'cagada',
    )