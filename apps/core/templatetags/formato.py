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
