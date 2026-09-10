from django.urls import path

from . import views


urlpatterns = [
    path(
        'ubicaciones/',
        views.listar_ubicaciones,
        name='listar_ubicaciones'
    ),
]