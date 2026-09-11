from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404
from apps.cagadas.models import Cagada
from django.core.paginator import Paginator
from .forms import FeedFilterForm


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

        usuario = form.cleaned_data.get(
            'usuario'
        )

        calificacion = form.cleaned_data.get(
            'calificacion'
        )

        categoria = form.cleaned_data.get(
            'categoria'
        )

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
        20
    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    return render(
        request,
        'feed/feed.html',
        {
            'cagadas': page_obj,
            'page_obj': page_obj,
            'filter_form': form,
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