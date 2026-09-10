from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegistroUsuarioForm

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