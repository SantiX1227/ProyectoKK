from datetime import timedelta

from django import template


register = template.Library()


@register.filter
def duracion(valor):
    """
    Muestra un timedelta de forma legible:
    '1 h 05 min', '3 min 12 s' o '45 s'.
    Si el valor es None devuelve '' para poder usar |default.
    """

    if valor is None or valor == '':
        return ''

    if not isinstance(valor, timedelta):
        return valor

    total_segundos = int(
        valor.total_seconds()
    )

    horas, resto = divmod(
        total_segundos,
        3600
    )

    minutos, segundos = divmod(
        resto,
        60
    )

    if horas:
        return f'{horas} h {minutos:02d} min'

    if minutos:
        return f'{minutos} min {segundos:02d} s'

    return f'{segundos} s'


@register.filter
def distancia(metros):
    """
    Muestra una distancia en metros de forma legible:
    '350 m', '2,4 km' o '128 km'.
    Si el valor es None devuelve '' para poder usar |default.
    """

    if metros is None or metros == '':
        return ''

    metros = float(metros)

    if metros < 1000:
        return f'{round(metros)} m'

    kilometros = metros / 1000

    if kilometros < 100:
        texto = f'{kilometros:.1f}'.replace('.', ',')
    else:
        texto = f'{round(kilometros)}'

    return f'{texto} km'
