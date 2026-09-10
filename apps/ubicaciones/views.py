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

    desde_registro_cagada = False

    if request.method == 'POST':

        origen = request.POST.get('origen')

        if origen == 'registrar_cagada':

            datos_cagada = request.POST.dict()

            datos_cagada.pop(
                'csrfmiddlewaretoken',
                None
            )

            datos_cagada.pop(
                'origen',
                None
            )

            request.session['cagada_borrador'] = (
                datos_cagada
            )

            desde_registro_cagada = True

            form = UbicacionForm()

        else:

            form = UbicacionForm(
                request.POST
            )

            if form.is_valid():

                ubicacion = form.save(
                    commit=False
                )

                ubicacion.usuario = request.user

                ubicacion.save()

                if request.POST.get(
                    'volver_a_cagada'
                ) == '1':

                    request.session[
                        'cagada_ubicacion_seleccionada'
                    ] = ubicacion.id

                    return redirect(
                        'registrar_cagada'
                    )

                return redirect(
                    'listar_ubicaciones'
                )

    else:

        form = UbicacionForm()

    return render(
        request,
        'ubicaciones/crear_ubicaciones.html',
        {
            'form': form,
            'desde_registro_cagada': (
                desde_registro_cagada
            )
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

@login_required
def eliminar_ubicacion(request, id):

    ubicacion = get_object_or_404(
        Ubicacion,
        id=id,
        usuario=request.user
    )

    if request.method == 'POST':

        ubicacion.delete()

        return redirect('listar_ubicaciones')

    return render(
        request,
        'ubicaciones/eliminar_ubicaciones.html',
        {
            'ubicacion': ubicacion
        }
    )