from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import CagadaForm
from .models import Cagada


@login_required
def registrar_cagada(request):

    if request.method == 'POST':

        form = CagadaForm(
            request.POST,
            usuario=request.user
        )

        if form.is_valid():

            cagada = form.save(
                commit=False
            )

            cagada.usuario = request.user

            cagada.save()

            return redirect('home')

        return render(
            request,
            'cagadas/registrar.html',
            {
                'form': form
            }
        )

    datos_guardados = request.session.pop(
        'cagada_borrador',
        None
    )

    ubicacion_seleccionada = request.session.pop(
        'cagada_ubicacion_seleccionada',
        None
    )

    if datos_guardados:

        form = CagadaForm(
            initial=datos_guardados,
            usuario=request.user
        )

        if ubicacion_seleccionada:

            form.initial['ubicacion'] = (
                ubicacion_seleccionada
            )

    else:

        form = CagadaForm(
            usuario=request.user
        )

    return render(
        request,
        'cagadas/registrar.html',
        {
            'form': form
        }
    )

@login_required
def historial_cagadas(request):

    cagadas = Cagada.objects.filter(
        usuario=request.user
    ).select_related(
        'ubicacion'
    ).order_by(
        '-hora_inicio_cagada'
    )

    return render(
        request,
        'cagadas/historial.html',
        {
            'cagadas': cagadas
        }
    )