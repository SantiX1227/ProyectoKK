from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Ubicacion
from .forms import UbicacionForm

@login_required
def listar_ubicaciones(request):

    ubicaciones = Ubicacion.objects.filter(
        usuario=request.user
    )

    return render(
        request,
        'ubicaciones/listar_ubicaciones.html',
        {
            'ubicaciones': ubicaciones
        }
    )

@login_required
def crear_ubicacion(request):

    if request.method == 'POST':

        form = UbicacionForm(
            request.POST
        )

        if form.is_valid():

            ubicacion = form.save(
                commit=False
            )

            ubicacion.usuario = request.user

            ubicacion.save()

            return redirect('listar_ubicaciones')

    else:

        form = UbicacionForm()

    return render(
        request,
        'ubicaciones/crear_ubicaciones.html',
        {
            'form': form
        }
    )