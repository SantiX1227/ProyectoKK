import math

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
# La leyenda se genera sola a partir de aquí (_leyenda_mapa).
# Los colores de cada nivel están en mapa.css (--nivel-0 … --nivel-4).
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
def _leyenda_mapa():
    """
    Textos de la leyenda a partir de NIVELES_MAPA, para que la
    leyenda nunca se desincronice de los umbrales:
    [{'nivel': 0, 'texto': '0'}, {'nivel': 1, 'texto': '1–2'}, ...]
    """

    leyenda = [
        {
            'nivel': 0,
            'texto': '0'
        }
    ]

    ascendente = sorted(NIVELES_MAPA)

    for indice, (minimo, nivel) in enumerate(ascendente):

        if indice + 1 < len(ascendente):

            maximo = ascendente[indice + 1][0] - 1

            if minimo == maximo:
                texto = f'{minimo}'
            else:
                texto = f'{minimo}–{maximo}'

        else:
            texto = f'{minimo} o más'

        leyenda.append({
            'nivel': nivel,
            'texto': texto
        })

    return leyenda


RADIO_TIERRA_METROS = 6_371_000


def _distancia_metros(latitud_1, longitud_1, latitud_2, longitud_2):
    """
    Distancia en línea recta sobre la superficie de la Tierra
    (fórmula de haversine). Suficiente para distancias de ciudad.
    """

    fi_1 = math.radians(latitud_1)
    fi_2 = math.radians(latitud_2)

    delta_fi = math.radians(latitud_2 - latitud_1)
    delta_lambda = math.radians(longitud_2 - longitud_1)

    a = (
        math.sin(delta_fi / 2) ** 2
        + math.cos(fi_1) * math.cos(fi_2) * math.sin(delta_lambda / 2) ** 2
    )

    return 2 * RADIO_TIERRA_METROS * math.asin(
        math.sqrt(a)
    )


def _formatear_distancia(metros):
    """'350 m', '2,4 km' o '128 km'."""

    if metros < 1000:
        return f'{round(metros)} m'

    kilometros = metros / 1000

    if kilometros < 100:
        texto = f'{kilometros:.1f}'.replace('.', ',')
    else:
        texto = f'{round(kilometros)}'

    return f'{texto} km'


def _datos_geograficos(lugares, ubicaciones, total_cagadas):
    """
    Datos para el panel geográfico y el centro del mapa.

    lugares:     ubicaciones_mapa (dicts, solo las que tienen coordenadas).
    ubicaciones: queryset anotado con 'cantidad' (todas, ordenadas de más
                 a menos cagadas).
    """

    if not lugares:
        return None

    # --- Centro de gravedad -------------------------------------------
    # Promedio de las coordenadas, contando más los lugares más usados.
    # Si todavía no hay cagadas en lugares del mapa, promedio simple.
    if any(lugar['cantidad'] for lugar in lugares):
        pesos = [lugar['cantidad'] for lugar in lugares]
    else:
        pesos = [1] * len(lugares)

    suma_pesos = sum(pesos)

    centro_latitud = sum(
        lugar['latitud'] * peso
        for lugar, peso in zip(lugares, pesos)
    ) / suma_pesos

    centro_longitud = sum(
        lugar['longitud'] * peso
        for lugar, peso in zip(lugares, pesos)
    ) / suma_pesos

    # Distancia de cada lugar al centro
    distancias_al_centro = [
        (
            _distancia_metros(
                centro_latitud,
                centro_longitud,
                lugar['latitud'],
                lugar['longitud']
            ),
            lugar,
            peso
        )
        for lugar, peso in zip(lugares, pesos)
    ]

    # Lugar más cercano al centro (para explicarlo con un nombre)
    distancia_cercano, lugar_cercano, _ = min(
        distancias_al_centro,
        key=lambda item: item[0]
    )

    # Radio de acción: el lugar usado que queda más lejos del centro
    radio, lugar_lejano, _ = max(
        (item for item in distancias_al_centro if item[2]),
        key=lambda item: item[0]
    )

    # --- Los dos lugares más separados entre sí -------------------------
    separacion = None

    for indice, lugar_a in enumerate(lugares):

        for lugar_b in lugares[indice + 1:]:

            distancia = _distancia_metros(
                lugar_a['latitud'],
                lugar_a['longitud'],
                lugar_b['latitud'],
                lugar_b['longitud']
            )

            if separacion is None or distancia > separacion['metros']:
                separacion = {
                    'metros': distancia,
                    'texto': _formatear_distancia(distancia),
                    'lugar_a': lugar_a['nombre'],
                    'lugar_b': lugar_b['nombre'],
                }

    # --- Reparto de cagadas por tipo de lugar (todas las ubicaciones) ----
    # El tipo es texto libre: "casa" y "Casa " cuentan como el mismo.
    por_tipo = {}

    for ubicacion in ubicaciones:

        tipo = (ubicacion.tipo or '').strip() or 'Sin tipo'
        clave = tipo.lower()

        if clave not in por_tipo:
            por_tipo[clave] = {
                'tipo': tipo,
                'cantidad': 0,
                'lugares': 0,
            }

        por_tipo[clave]['cantidad'] += ubicacion.cantidad
        por_tipo[clave]['lugares'] += 1

    total_por_tipo = sum(
        item['cantidad'] for item in por_tipo.values()
    )

    reparto_tipos = sorted(
        por_tipo.values(),
        key=lambda item: (-item['cantidad'], item['tipo'])
    )

    for item in reparto_tipos:

        if total_por_tipo:
            item['porcentaje'] = round(
                item['cantidad'] * 100 / total_por_tipo,
                1
            )
        else:
            item['porcentaje'] = 0

    # --- Favorita (entre todas, tenga o no coordenadas) -----------------
    favorita = ubicaciones[0] if ubicaciones and ubicaciones[0].cantidad else None

    if favorita and total_cagadas:
        porcentaje_favorita = round(
            favorita.cantidad * 100 / total_cagadas,
            1
        )
    else:
        porcentaje_favorita = 0

    return {
        # Va a mapa.js con json_script
        'centro': {
            'latitud': round(centro_latitud, 6),
            'longitud': round(centro_longitud, 6),
            'radio_metros': round(radio),
            'radio_texto': _formatear_distancia(radio),
        },
        'lugar_cercano': lugar_cercano['nombre'],
        'distancia_cercano': _formatear_distancia(distancia_cercano),
        'radio_texto': _formatear_distancia(radio),
        'radio_metros': round(radio),
        'lugar_lejano': lugar_lejano['nombre'],
        'separacion': separacion,
        'reparto_tipos': reparto_tipos,
        'favorita': favorita,
        'porcentaje_favorita': porcentaje_favorita,
        'en_mapa': len(lugares),
        'visitados': sum(1 for lugar in lugares if lugar['cantidad']),
        'sin_estrenar': sum(1 for lugar in lugares if not lugar['cantidad']),
    }


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

    geo = _datos_geograficos(
        ubicaciones_mapa,
        ubicaciones,
        total_cagadas
    )

    return render(
        request,
        'ubicaciones/mapa.html',
        {
            'ubicaciones': ubicaciones,
            'ubicaciones_mapa': ubicaciones_mapa,
            'ubicaciones_sin_coordenadas': ubicaciones_sin_coordenadas,
            'total_cagadas': total_cagadas,
            'leyenda': _leyenda_mapa(),
            'geo': geo,
        }
    )