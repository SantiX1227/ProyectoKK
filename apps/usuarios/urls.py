from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('registro/', views.registrarse, name='registro'),
    path( 'recuperar/', auth_views.PasswordResetView.as_view( template_name='usuarios/password_reset.html' ), name='password_reset' ),
    path( 'recuperar/enviado/', auth_views.PasswordResetDoneView.as_view( template_name='usuarios/password_reset_done.html' ), name='password_reset_done' ),
    path( 'recuperar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view( template_name='usuarios/password_reset_confirm.html' ), name='password_reset_confirm' ),
    path( 'recuperar/completo/', auth_views.PasswordResetCompleteView.as_view( template_name='usuarios/password_reset_complete.html' ), name='password_reset_complete' ),
]