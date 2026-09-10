from django.urls import path

from . import views


urlpatterns = [
    path(
        'ubicaciones/',
        views.listar_ubicaciones,
        name='listar_ubicaciones'
    ),
    path(
        'crear-ubicacion/',
        views.crear_ubicacion,
        name='crear_ubicacion'
    ),
    path(
        'editar-ubicacion/<int:id>/',
        views.editar_ubicacion,
        name='editar_ubicacion'
    ),
    path(
        'eliminar-ubicacion/<int:id>/',
        views.eliminar_ubicacion,
        name='eliminar_ubicacion'
    ),
]