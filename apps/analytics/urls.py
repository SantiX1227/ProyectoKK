from django.urls import path
from . import views


urlpatterns = [
    path(
        '',
        views.analytics,
        name='analytics'
    ),
    path(
        'comparacion/<int:usuario_id>/',
        views.analytics_comparacion,
        name='analytics-comparacion'
    ),
]