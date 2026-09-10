from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_cagada, name='registrar_cagada'),
    path('historial/', views.historial_cagadas, name='historial_cagadas'),
]