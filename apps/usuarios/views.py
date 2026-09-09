from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


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


def cerrar_sesion(request):

    logout(request)

    return redirect('login')

def home(request):

    if not request.user.is_authenticated:
        return redirect('login')

    return render(
        request,
        'home/landing.html'
    )