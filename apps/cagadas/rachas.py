"""
Rachas diarias: días seguidos con al menos una cagada.

Un día cuenta según la fecha local (TIME_ZONE) de hora_inicio_cagada.
Lo usan la landing, la analítica y la comparación.
"""

from datetime import timedelta

from django.db.models.functions import TruncDate
from django.utils import timezone


HITOS_RACHA = (
    3,
    7,
    14,
    30,
    50,
    100,
    365,
)


def dias_con_cagadas(cagadas):
    """
    Fechas locales distintas en las que hay al menos una cagada,
    de la más antigua a la más reciente.
    """

    return list(
        cagadas
        .annotate(
            dia=TruncDate('hora_inicio_cagada')
        )
        .values_list(
            'dia',
            flat=True
        )
        .distinct()
        .order_by('dia')
    )


def calcular_rachas(dias):
    """
    Agrupa fechas ordenadas y sin repetir en rachas de días seguidos.
    Devuelve una lista de {'inicio', 'fin', 'dias'}, de la más antigua
    a la más reciente.
    """

    rachas = []

    for dia in dias:

        if (
            rachas
            and dia - rachas[-1]['fin'] == timedelta(days=1)
        ):
            rachas[-1]['fin'] = dia
            rachas[-1]['dias'] += 1

        else:
            rachas.append({
                'inicio': dia,
                'fin': dia,
                'dias': 1,
                'es_actual': False,
            })

    return rachas


def _mejor_racha(rachas):
    """
    La racha más larga. En caso de empate gana la más reciente,
    así la racha en curso cuenta como récord si iguala al anterior.
    """

    return max(
        rachas,
        key=lambda racha: (
            racha['dias'],
            racha['fin']
        ),
        default=None
    )


def racha_mas_larga(cagadas):
    """
    Días de la racha más larga (incluida la que está en curso),
    o None si no hay cagadas. Para el marcador de la comparación.
    """

    mejor = _mejor_racha(
        calcular_rachas(
            dias_con_cagadas(cagadas)
        )
    )

    if mejor is None:
        return None

    return mejor['dias']


def resumen_racha(cagadas, hoy=None):
    """
    Todo lo que necesitan la landing y la analítica.

    estado:
        'activa'      -> hoy ya hay cagada.
        'en_peligro'  -> la última fue ayer: sigue viva hasta medianoche.
        'apagada'     -> no hay racha en curso.
    """

    if hoy is None:
        hoy = timezone.localdate()

    dias = dias_con_cagadas(cagadas)

    rachas = calcular_rachas(dias)

    ultima = rachas[-1] if rachas else None

    if ultima and ultima['fin'] == hoy:
        estado = 'activa'

    elif ultima and ultima['fin'] == hoy - timedelta(days=1):
        estado = 'en_peligro'

    else:
        estado = 'apagada'

    if estado == 'apagada':
        actual = 0
    else:
        actual = ultima['dias']
        ultima['es_actual'] = True

    mejor = _mejor_racha(rachas)

    # ---------------------------------------------------------
    # Días activos: % de días con cagada desde la primera
    # ---------------------------------------------------------

    if dias:
        dias_transcurridos = (hoy - dias[0]).days + 1

        porcentaje_dias_activos = round(
            len(dias) / dias_transcurridos * 100
        )
    else:
        porcentaje_dias_activos = None

    if rachas:
        media = round(
            len(dias) / len(rachas),
            1
        )
    else:
        media = None

    # ---------------------------------------------------------
    # Siguiente hito
    # ---------------------------------------------------------

    siguiente_hito = next(
        (
            hito
            for hito in HITOS_RACHA
            if hito > actual
        ),
        None
    )

    if siguiente_hito:
        faltan_para_hito = siguiente_hito - actual

        progreso_hito = round(
            actual / siguiente_hito * 100
        )
    else:
        faltan_para_hito = None
        progreso_hito = 100

    return {
        'actual': actual,
        'estado': estado,
        'mejor': mejor,
        'es_record': bool(
            actual
            and mejor is ultima
        ),
        'pasadas': [
            racha
            for racha in reversed(rachas)
            if not racha['es_actual']
        ],
        'total_rachas': len(rachas),
        'media': media,
        'dias_activos': len(dias),
        'porcentaje_dias_activos': porcentaje_dias_activos,
        'siguiente_hito': siguiente_hito,
        'faltan_para_hito': faltan_para_hito,
        'progreso_hito': progreso_hito,
    }