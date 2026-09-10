from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

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

@login_required
def editar_ubicacion(request, id):

    ubicacion = get_object_or_404(
        Ubicacion,
        id=id,
        usuario=request.user
    )

    if request.method == 'POST':

        form = UbicacionForm(
            request.POST,
            instance=ubicacion
        )

        if form.is_valid():

            form.save()

            return redirect('listar_ubicaciones')

    else:

        form = UbicacionForm(
            instance=ubicacion
        )

    return render(
        request,
        'ubicaciones/editar_ubicaciones.html',
        {
            'form': form,
            'ubicacion': ubicacion
        }
    )