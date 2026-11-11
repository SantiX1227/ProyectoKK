from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

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

                    messages.success(
                        request,
                        f'La ubicación «{ubicacion.nombre}» se creó '
                        'y quedó seleccionada en tu registro.'
                    )

                    return redirect(
                        'registrar_cagada'
                    )

                messages.success(
                    request,
                    f'La ubicación «{ubicacion.nombre}» se creó.'
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

            ubicacion = form.save()

            messages.success(
                request,
                f'La ubicación «{ubicacion.nombre}» se actualizó.'
            )

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

        nombre = ubicacion.nombre

        ubicacion.delete()

        messages.success(
            request,
            f'La ubicación «{nombre}» se eliminó. '
            'Tus cagadas registradas allí se conservan, '
            'pero sin ubicación.'
        )

        return redirect('listar_ubicaciones')

    return render(
        request,
        'ubicaciones/eliminar_ubicaciones.html',
        {
            'ubicacion': ubicacion
        }
    )