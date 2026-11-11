from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count, Max, Q
from django.urls import reverse
from django.utils import formats, timezone

from apps.cagadas.models import Cagada
from apps.core.templatetags.formato import duracion as formatear_duracion

from .models import Ubicacion
from .forms import UbicacionForm


# Mapa: nivel de color según el número de cagadas en la ubicación.
# Pares (mínimo de cagadas, nivel), de mayor a menor. Sin cagadas → nivel 0.
# Si cambias los umbrales, actualiza también la leyenda (paso 4) y mapa.css.
NIVELES_MAPA = (
    (11, 4),
    (6, 3),
    (3, 2),
    (1, 1),
)


def _nivel_mapa(cantidad):

    for minimo, nivel in NIVELES_MAPA:

        if cantidad >= minimo:
            return nivel

    return 0

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
                        'y quedó seleccionada en tu registro de mierda.'
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

@login_required
def mapa_ubicaciones(request):

    # Solo cuentan las cagadas del propio usuario
    filtro_propias = Q(
        cagadas__usuario=request.user
    )

    ubicaciones = (
        Ubicacion.objects
        .filter(
            usuario=request.user
        )
        .annotate(
            cantidad=Count(
                'cagadas',
                filter=filtro_propias
            ),
            duracion_promedio=Avg(
                'cagadas__duracion',
                filter=filtro_propias
            ),
            calificacion_promedio=Avg(
                'cagadas__calificacion',
                filter=filtro_propias
            ),
            ultima_visita=Max(
                'cagadas__hora_inicio_cagada',
                filter=filtro_propias
            ),
        )
        .order_by(
            '-cantidad',
            'nombre'
        )
    )

    total_cagadas = Cagada.objects.filter(
        usuario=request.user
    ).count()

    maximo = max(
        (ubicacion.cantidad for ubicacion in ubicaciones),
        default=0
    )

    ubicaciones_mapa = []
    ubicaciones_sin_coordenadas = []

    for ubicacion in ubicaciones:

        if ubicacion.latitud is None or ubicacion.longitud is None:

            ubicaciones_sin_coordenadas.append(
                ubicacion
            )

            continue

        if total_cagadas:
            porcentaje = round(
                ubicacion.cantidad * 100 / total_cagadas,
                1
            )
        else:
            porcentaje = 0

        if ubicacion.calificacion_promedio is not None:
            calificacion_promedio = round(
                float(ubicacion.calificacion_promedio),
                1
            )
        else:
            calificacion_promedio = None

        if ubicacion.ultima_visita:
            ultima_visita = formats.date_format(
                timezone.localtime(ubicacion.ultima_visita),
                'DATE_FORMAT'
            )
        else:
            ultima_visita = None

        ubicaciones_mapa.append({
            'id': ubicacion.id,
            'nombre': ubicacion.nombre,
            'tipo': ubicacion.tipo,
            'latitud': float(ubicacion.latitud),
            'longitud': float(ubicacion.longitud),
            'cantidad': ubicacion.cantidad,
            'porcentaje': porcentaje,
            'nivel': _nivel_mapa(ubicacion.cantidad),
            'favorita': maximo > 0 and ubicacion.cantidad == maximo,
            'duracion_promedio': formatear_duracion(
                ubicacion.duracion_promedio
            ),
            'calificacion_promedio': calificacion_promedio,
            'ultima_visita': ultima_visita,
            'url_editar': reverse(
                'editar_ubicacion',
                args=[ubicacion.id]
            ),
        })

    return render(
        request,
        'ubicaciones/mapa.html',
        {
            'ubicaciones': ubicaciones,
            'ubicaciones_mapa': ubicaciones_mapa,
            'ubicaciones_sin_coordenadas': ubicaciones_sin_coordenadas,
            'total_cagadas': total_cagadas,
        }
    )