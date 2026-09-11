from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404, redirect
from apps.cagadas.models import Cagada
from django.core.paginator import Paginator
from .forms import FeedFilterForm
from .models import Reaccion
from django.http import JsonResponse


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
            cagadas = cagadas.filter(
                usuario__username__icontains=usuario
            )

        if calificacion:
            cagadas = cagadas.filter(
                calificacion=calificacion
            )

        if categoria:
            cagadas = cagadas.filter(
                categorizacion=categoria
            )

    paginator = Paginator(
        cagadas,
        10
    )

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    reacciones = Reaccion.objects.filter(
        cagada__in=page_obj.object_list
    )

    for cagada in page_obj.object_list:

        reacciones_cagada = reacciones.filter(
            cagada=cagada
        )

        reaccion_usuario = reacciones_cagada.filter(
            usuario=request.user
        ).first()

        cagada.reaccion_usuario = (
            reaccion_usuario.tipo
            if reaccion_usuario
            else None
        )

        cagada.reacciones_display = []

        for tipo, nombre in Reaccion.TIPOS_REACCION:

            cantidad = reacciones_cagada.filter(
                tipo=tipo
            ).count()

            cagada.reacciones_display.append({
                'tipo': tipo,
                'nombre': nombre,
                'cantidad': cantidad,
                'seleccionada': (
                    cagada.reaccion_usuario == tipo
                )
            })

        reaccion_usuario = reacciones_cagada.filter(
            usuario=request.user
        ).first()

        cagada.reaccion_usuario = (
            reaccion_usuario.tipo
            if reaccion_usuario
            else None
        )

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
        Cagada.objects.select_related(
            'usuario',
            'ubicacion'
        ),
        id=id,
        visible_para_otros=True
    )

    return render(
        request,
        'feed/detallepublico.html',
        {
            'cagada': cagada
        }
    )
@login_required
def reaccionar_cagada(request, id, tipo):

    if request.method != 'POST':
        return redirect('feed_cagadas')

    cagada = get_object_or_404(
        Cagada,
        id=id,
        visible_para_otros=True
    )

    tipos_validos = dict(Reaccion.TIPOS_REACCION)

    if tipo not in tipos_validos:
        return redirect('feed_cagadas')

    reaccion, creada = Reaccion.objects.get_or_create(
        usuario=request.user,
        cagada=cagada,
        defaults={
            'tipo': tipo
        }
    )

    if not creada:

        if reaccion.tipo == tipo:
            reaccion.delete()

        else:
            reaccion.tipo = tipo
            reaccion.save(update_fields=['tipo'])

    # Si la petición viene desde JavaScript,
    # devolvemos los datos sin recargar la página.
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        reacciones = Reaccion.objects.filter(
            cagada=cagada
        )

        conteos = {
            tipo_reaccion: reacciones.filter(
                tipo=tipo_reaccion
            ).count()
            for tipo_reaccion, _ in Reaccion.TIPOS_REACCION
        }

        reaccion_usuario = reacciones.filter(
            usuario=request.user
        ).first()

        return JsonResponse({
            'reacciones': conteos,
            'reaccion_usuario': (
                reaccion_usuario.tipo
                if reaccion_usuario
                else None
            )
        })

    return redirect(
        request.META.get(
            'HTTP_REFERER',
            '/feed/'
        )
    )