"""
Cálculos geográficos compartidos (mapa y comparación).

Todo se calcula en el servidor, sin servicios externos: las
coordenadas nunca salen de la app. Para mostrar una distancia
en plantillas, usar el filtro |distancia de core/templatetags/formato.py.
"""

import math


RADIO_TIERRA_METROS = 6_371_000


def distancia_metros(latitud_1, longitud_1, latitud_2, longitud_2):
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


def mayor_distancia(puntos):
    """
    Mayor distancia en metros entre dos de los puntos dados
    [(latitud, longitud), ...]. None si hay menos de dos.
    Compara cada par: con decenas de lugares es instantáneo.
    """

    puntos = [
        (float(latitud), float(longitud))
        for latitud, longitud in puntos
    ]

    if len(puntos) < 2:
        return None

    mayor = 0

    for indice, (latitud_a, longitud_a) in enumerate(puntos):

        for latitud_b, longitud_b in puntos[indice + 1:]:

            mayor = max(
                mayor,
                distancia_metros(
                    latitud_a,
                    longitud_a,
                    latitud_b,
                    longitud_b
                )
            )

    return mayor
