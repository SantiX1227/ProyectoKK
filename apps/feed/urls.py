from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.feed_cagadas,
        name='feed_cagadas'
    ),

    path(
        'cagada/<int:id>/',
        views.detalle_cagada_publica,
        name='detalle_cagada_publica'
    ),

]