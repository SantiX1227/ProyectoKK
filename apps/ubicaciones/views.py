from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Ubicacion


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
