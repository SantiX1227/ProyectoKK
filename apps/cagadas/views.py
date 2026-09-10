from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import CagadaForm


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

            cagada.duracion = (
                cagada.hora_final_cagada
                - cagada.hora_inicio_cagada
            )

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