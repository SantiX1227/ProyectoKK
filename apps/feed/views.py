from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.cagadas.models import Cagada
from .forms import FeedFilterForm
from .models import Reaccion


@login_required
def feed_cagadas(request):
    cagadas = Cagada.objects.filter(
        visible_para_otros=True
    ).select_related(
        'usuario',
        'ubicacion'
    ).order_by(
        '-hora_inicio_cagada'
    )

    form = FeedFilterForm(request.GET)
    if form.is_valid():
        usuario = form.cleaned_data.get('usuario')
        calificacion = form.cleaned_data.get('calificacion')
        categoria = form.cleaned_data.get('categoria')

        if usuario:
            cagadas = cagadas.filter(usuario__username__icontains=usuario)
        if calificacion:
            cagadas = cagadas.filter(calificacion=calificacion)
        if categoria:
            cagadas = cagadas.filter(categorizacion=categoria)

    paginator = Paginator(cagadas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 1. Agrupación y conteo de reacciones por cagada y tipo en una sola query
    conteos_reacciones = (
        Reaccion.objects
        .filter(cagada__in=page_obj.object_list)
        .values('cagada_id', 'tipo')
        .annotate(cantidad=Count('id'))
    )

    conteos = defaultdict(dict)
    for reaccion in conteos_reacciones:
        conteos[reaccion['cagada_id']][reaccion['tipo']] = reaccion['cantidad']

    # 2. Reacciones del usuario actual en una sola query
    reacciones_usuario = {
        reaccion.cagada_id: reaccion.tipo
        for reaccion in Reaccion.objects.filter(
            cagada__in=page_obj.object_list,
            usuario=request.user
        )
    }

    # 3. Armado de la estructura para el template sin hacer queries adicionales
    for cagada in page_obj.object_list:
        tipo_usuario = reacciones_usuario.get(cagada.id)
        cagada.reaccion_usuario = tipo_usuario
        cagada.reacciones_display = []

        for tipo, nombre in Reaccion.TIPOS_REACCION:
            cantidad = conteos[cagada.id].get(tipo, 0)
            cagada.reacciones_display.append({
                'tipo': tipo,
                'nombre': nombre,
                'cantidad': cantidad,
                'seleccionada': (tipo_usuario == tipo)
            })

    return render(
        request,
        'feed/feed.html',
        {
            'cagadas': page_obj,
            'page_obj': page_obj,
            'filter_form': form,
            'reacciones_disponibles': Reaccion.TIPOS_REACCION,
        }
    )


@login_required
def detalle_cagada_publica(request, id):
    cagada = get_object_or_404(
        Cagada.objects.select_related('usuario', 'ubicacion'),
        id=id,
        visible_para_otros=True
    )

    return render(
        request,
        'feed/detallepublico.html',
        {'cagada': cagada}
    )


@login_required
def reaccionar_cagada(request, id, tipo):
    if request.method != 'POST':
        return redirect('feed_cagadas')

    cagada = get_object_or_404(Cagada, id=id, visible_para_otros=True)
    tipos_validos = dict(Reaccion.TIPOS_REACCION)

    if tipo not in tipos_validos:
        return redirect('feed_cagadas')

    reaccion, creada = Reaccion.objects.get_or_create(
        usuario=request.user,
        cagada=cagada,
        defaults={'tipo': tipo}
    )

    if not creada:
        if reaccion.tipo == tipo:
            reaccion.delete()
        else:
            reaccion.tipo = tipo
            reaccion.save(update_fields=['tipo'])

    # Si la petición viene desde JavaScript (AJAX/Fetch)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        conteos_query = (
            Reaccion.objects
            .filter(cagada=cagada)
            .values('tipo')
            .annotate(cantidad=Count('id'))
        )
        conteos_map = {item['tipo']: item['cantidad'] for item in conteos_query}
        conteos = {
            tipo_reaccion: conteos_map.get(tipo_reaccion, 0)
            for tipo_reaccion, _ in Reaccion.TIPOS_REACCION
        }

        reaccion_usuario = Reaccion.objects.filter(
            cagada=cagada,
            usuario=request.user
        ).first()

        return JsonResponse({
            'reacciones': conteos,
            'reaccion_usuario': reaccion_usuario.tipo if reaccion_usuario else None
        })

    return redirect(request.META.get('HTTP_REFERER', '/feed/'))