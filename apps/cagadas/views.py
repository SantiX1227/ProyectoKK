from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CagadaForm, EditarCagadaForm
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

@login_required
def detalle_cagada(request, id):

    cagada = get_object_or_404(
        Cagada.objects.select_related(
            'ubicacion'
        ),
        id=id,
        usuario=request.user
    )

    return render(
        request,
        'cagadas/detalle.html',
        {
            'cagada': cagada
        }
    )

@login_required
def editar_cagada(request, id):

    cagada = get_object_or_404(
        Cagada,
        id=id,
        usuario=request.user
    )

    if request.method == 'POST':

        form = EditarCagadaForm(
            request.POST,
            instance=cagada,
            usuario=request.user
        )

        if form.is_valid():

            form.save()

            return redirect(
                'detalle_cagada',
                id=cagada.id
            )

    else:

        form = CagadaForm(
            instance=cagada,
            usuario=request.user
        )

    return render(
        request,
        'cagadas/editar.html',
        {
            'form': form,
            'cagada': cagada
        }
    )


@login_required
def eliminar_cagada(request, id):

    cagada = get_object_or_404(
        Cagada,
        id=id,
        usuario=request.user
    )

    if request.method == 'POST':

        cagada.delete()

        return redirect(
            'historial_cagadas'
        )

    return render(
        request,
        'cagadas/eliminar.html',
        {
            'cagada': cagada
        }
    )