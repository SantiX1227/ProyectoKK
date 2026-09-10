from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404
from apps.cagadas.models import Cagada


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

    return render(
        request,
        'feed/feed.html',
        {
            'cagadas': cagadas
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
        'cagadas/detalle_publico.html',
        {
            'cagada': cagada
        }
    )