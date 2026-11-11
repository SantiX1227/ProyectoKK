from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import RegistroUsuarioForm, PerfilUsuarioForm

def iniciar_sesion(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        usuario = authenticate(
            request,
            email=email,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect('home')

        return render(
            request,
            'usuarios/login.html',
            {
                'error': 'El correo o la contraseña son incorrectos.'
            }
        )

    return render(request, 'usuarios/login.html')

@login_required
def cerrar_sesion(request):

    logout(request)

    return redirect('login')


def registrarse(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        form = RegistroUsuarioForm(request.POST, request.FILES)

        if form.is_valid():

            usuario = form.save()

            login(request, usuario)

            messages.success(
                request,
                f'Te damos la bienvenida al Proyecto KK, {usuario.username}. '
                'Ya puedes registrar tu primera cagada.'
            )

            return redirect('home')

    else:

        form = RegistroUsuarioForm()

    return render(
        request,
        'usuarios/register.html',
        {
            'form': form
        }
    )

@login_required
def perfil(request):

    if request.method == 'POST':

        form = PerfilUsuarioForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Tu perfil de mierda se actualizó.'
            )

            return redirect('perfil')

    else:

        form = PerfilUsuarioForm(
            instance=request.user
        )

    return render(
        request,
        'usuarios/perfil.html',
        {
            'form': form
        }
    )

@login_required
def cambiar_contrasena(request):

    if request.method == 'POST':

        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            usuario = form.save()

            update_session_auth_hash(
                request,
                usuario
            )

            messages.success(
                request,
                'Tu contraseña de mierda se cambió. Tu sesión sigue abierta.'
            )

            return redirect('perfil')
        
    else:

        form = PasswordChangeForm(
            request.user
        )

    return render(
        request,
        'usuarios/cambiar_contrasena.html',
        {
            'form': form
        }
    )

@login_required
def eliminar_cuenta(request):

    
    if request.method == 'POST':

        password = request.POST.get('password')

        if request.user.check_password(password):

            usuario = request.user

            logout(request)

            usuario.delete()

            messages.info(
                request,
                'Sos una mierda, Tu cuenta y todos tus datos se eliminaron. '
                'Si quieres volver, puedes crear una cuenta nueva.'
            )

            return redirect('registro')

        return render(
            request,
            'usuarios/eliminar_cuenta.html',
            {
                'error': 'La contraseña es incorrecta.'
            }
        )

    return render(
        request,
        'usuarios/eliminar_cuenta.html'
    )
