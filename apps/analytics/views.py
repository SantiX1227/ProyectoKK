from django.contrib.auth.decorators import login_required
from django.db.models import (
    Count,
    Avg,
    Max,
    Min,
    Sum
)
from django.db.models.functions import (
    ExtractHour,
    ExtractWeekDay,
    TruncMonth
)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from apps.cagadas.models import Cagada

Usuario = get_user_model()


@login_required
def analytics(request):
    """
    Calcula y estructura las métricas de uso del usuario autenticado:
    resumen general, distribución temporal, análisis por categorías
    y analítica espacial/geográfica para renderizar el panel de estadísticas.
    """

    cagadas = Cagada.objects.filter(
        usuario=request.user
    )

    # =========================================================
    # FASE A - RESUMEN PERSONAL
    # =========================================================

    resumen = cagadas.aggregate(
        total_cagadas=Count('id'),
        duracion_total=Sum('duracion'),
        duracion_promedio=Avg('duracion'),
        cagada_mas_larga=Max('duracion'),
        cagada_mas_corta=Min('duracion'),
        calificacion_promedio=Avg('calificacion'),
        primera_cagada=Min('hora_inicio_cagada'),
        ultima_cagada=Max('hora_inicio_cagada'),
    )

    categoria_mas_usada = (
        cagadas
        .values('categorizacion')
        .annotate(
            cantidad=Count('id')
        )
        .order_by('-cantidad')
        .first()
    )

    ubicacion_mas_usada = (
        cagadas
        .filter(
            ubicacion__isnull=False
        )
        .values(
            'ubicacion',
            'ubicacion__nombre'
        )
        .annotate(
            cantidad=Count('id')
        )
        .order_by('-cantidad')
        .first()
    )

    if categoria_mas_usada:
        categoria_mas_usada_nombre = dict(
            Cagada.CATEGORIAS
        ).get(
            categoria_mas_usada['categorizacion']
        )
    else:
        categoria_mas_usada_nombre = None

    # =========================================================
    # FASE B - ANÁLISIS TEMPORAL
    # =========================================================

    # ---------------------------------------------------------
    # 1. CAGADAS POR DÍA DE LA SEMANA
    # ---------------------------------------------------------

    resultados_dia = (
        cagadas
        .annotate(
            dia_semana=ExtractWeekDay(
                'hora_inicio_cagada'
            )
        )
        .values('dia_semana')
        .annotate(
            cantidad=Count('id')
        )
        .order_by('dia_semana')
    )

    nombres_dias = {
        1: 'Domingo',
        2: 'Lunes',
        3: 'Martes',
        4: 'Miércoles',
        5: 'Jueves',
        6: 'Viernes',
        7: 'Sábado',
    }

    cagadas_por_dia = {
        nombre: 0
        for nombre in nombres_dias.values()
    }

    for resultado in resultados_dia:
        nombre = nombres_dias[
            resultado['dia_semana']
        ]

        cagadas_por_dia[nombre] = (
            resultado['cantidad']
        )

    # ---------------------------------------------------------
    # 2. CAGADAS POR HORA DEL DÍA
    # ---------------------------------------------------------

    resultados_hora = (
        cagadas
        .annotate(
            hora=ExtractHour(
                'hora_inicio_cagada'
            )
        )
        .values('hora')
        .annotate(
            cantidad=Count('id')
        )
        .order_by('hora')
    )

    cagadas_por_hora = {
        hora: 0
        for hora in range(24)
    }

    for resultado in resultados_hora:
        cagadas_por_hora[
            resultado['hora']
        ] = resultado['cantidad']

    # ---------------------------------------------------------
    # 3. CAGADAS POR MES
    # ---------------------------------------------------------

    cagadas_por_mes = (
        cagadas
        .annotate(
            mes=TruncMonth(
                'hora_inicio_cagada'
            )
        )
        .values('mes')
        .annotate(
            cantidad=Count('id')
        )
        .order_by('mes')
    )

    # ---------------------------------------------------------
    # 4. DURACIÓN PROMEDIO POR DÍA DE LA SEMANA
    # ---------------------------------------------------------

    resultados_duracion_dia = (
        cagadas
        .annotate(
            dia_semana=ExtractWeekDay(
                'hora_inicio_cagada'
            )
        )
        .values('dia_semana')
        .annotate(
            duracion_promedio=Avg('duracion')
        )
        .order_by('dia_semana')
    )

    duracion_promedio_por_dia = {
        nombre: None
        for nombre in nombres_dias.values()
    }

    for resultado in resultados_duracion_dia:
        nombre = nombres_dias[
            resultado['dia_semana']
        ]

        duracion_promedio_por_dia[nombre] = (
            resultado['duracion_promedio']
        )

    # ---------------------------------------------------------
    # 5. CALIFICACIÓN PROMEDIO POR DÍA DE LA SEMANA
    # ---------------------------------------------------------

    resultados_calificacion_dia = (
        cagadas
        .annotate(
            dia_semana=ExtractWeekDay(
                'hora_inicio_cagada'
            )
        )
        .values('dia_semana')
        .annotate(
            calificacion_promedio=Avg(
                'calificacion'
            )
        )
        .order_by('dia_semana')
    )

    calificacion_promedio_por_dia = {
        nombre: None
        for nombre in nombres_dias.values()
    }

    for resultado in resultados_calificacion_dia:
        nombre = nombres_dias[
            resultado['dia_semana']
        ]

        calificacion_promedio_por_dia[nombre] = (
            resultado['calificacion_promedio']
        )

    # ---------------------------------------------------------
    # 6. DURACIÓN PROMEDIO POR HORA
    # ---------------------------------------------------------

    resultados_duracion_hora = (
        cagadas
        .annotate(
            hora=ExtractHour(
                'hora_inicio_cagada'
            )
        )
        .values('hora')
        .annotate(
            duracion_promedio=Avg('duracion')
        )
        .order_by('hora')
    )

    duracion_promedio_por_hora = {
        hora: None
        for hora in range(24)
    }

    for resultado in resultados_duracion_hora:
        duracion_promedio_por_hora[
            resultado['hora']
        ] = resultado['duracion_promedio']

    # =========================================================
    # FASE C - ANÁLISIS POR CATEGORÍAS
    # =========================================================

    total_cagadas = resumen['total_cagadas']

    # ---------------------------------------------------------
    # 1-5. ESTADÍSTICAS GENERALES POR CATEGORÍA
    # ---------------------------------------------------------

    estadisticas_categoria = (
        cagadas
        .values('categorizacion')
        .annotate(
            cantidad=Count('id'),
            duracion_total=Sum('duracion'),
            duracion_promedio=Avg('duracion'),
            calificacion_promedio=Avg(
                'calificacion'
            )
        )
        .order_by('categorizacion')
    )

    nombres_categorias = dict(
        Cagada.CATEGORIAS
    )

    analitica_categorias = []

    for categoria in estadisticas_categoria:

        cantidad = categoria['cantidad']

        if total_cagadas:
            porcentaje = (
                cantidad / total_cagadas
            ) * 100
        else:
            porcentaje = 0

        analitica_categorias.append({
            'id': categoria['categorizacion'],

            'nombre': nombres_categorias.get(
                categoria['categorizacion'],
                'Categoría desconocida'
            ),

            'cantidad': cantidad,

            'porcentaje': porcentaje,

            'duracion_total': (
                categoria['duracion_total']
            ),

            'duracion_promedio': (
                categoria['duracion_promedio']
            ),

            'calificacion_promedio': (
                categoria['calificacion_promedio']
            ),
        })

    # ---------------------------------------------------------
    # 6. CATEGORÍA CON MAYOR DURACIÓN PROMEDIO
    # ---------------------------------------------------------

    categoria_mayor_duracion = (
        cagadas
        .values('categorizacion')
        .annotate(
            duracion_promedio=Avg('duracion')
        )
        .order_by(
            '-duracion_promedio'
        )
        .first()
    )

    if categoria_mayor_duracion:

        categoria_mayor_duracion_nombre = (
            nombres_categorias.get(
                categoria_mayor_duracion[
                    'categorizacion'
                ],
                'Categoría desconocida'
            )
        )

        categoria_mayor_duracion_valor = (
            categoria_mayor_duracion[
                'duracion_promedio'
            ]
        )

    else:

        categoria_mayor_duracion_nombre = None
        categoria_mayor_duracion_valor = None

    # ---------------------------------------------------------
    # 7. CATEGORÍA MÁS FRECUENTE
    # ---------------------------------------------------------

    categoria_mas_frecuente = (
        cagadas
        .values('categorizacion')
        .annotate(
            cantidad=Count('id')
        )
        .order_by('-cantidad')
        .first()
    )

    if categoria_mas_frecuente:

        categoria_mas_frecuente_nombre = (
            nombres_categorias.get(
                categoria_mas_frecuente[
                    'categorizacion'
                ],
                'Categoría desconocida'
            )
        )

        categoria_mas_frecuente_cantidad = (
            categoria_mas_frecuente['cantidad']
        )

    else:

        categoria_mas_frecuente_nombre = None
        categoria_mas_frecuente_cantidad = None

    # ---------------------------------------------------------
    # 8. CATEGORÍA MEJOR CALIFICADA
    # ---------------------------------------------------------

    categoria_mejor_calificada = (
        cagadas
        .values('categorizacion')
        .annotate(
            calificacion_promedio=Avg(
                'calificacion'
            )
        )
        .order_by(
            '-calificacion_promedio'
        )
        .first()
    )

    if categoria_mejor_calificada:

        categoria_mejor_calificada_nombre = (
            nombres_categorias.get(
                categoria_mejor_calificada[
                    'categorizacion'
                ],
                'Categoría desconocida'
            )
        )

        categoria_mejor_calificada_valor = (
            categoria_mejor_calificada[
                'calificacion_promedio'
            ]
        )

    else:

        categoria_mejor_calificada_nombre = None
        categoria_mejor_calificada_valor = None

    # ---------------------------------------------------------
    # 9. CATEGORÍA PEOR CALIFICADA
    # ---------------------------------------------------------

    categoria_peor_calificada = (
        cagadas
        .values('categorizacion')
        .annotate(
            calificacion_promedio=Avg(
                'calificacion'
            )
        )
        .order_by(
            'calificacion_promedio'
        )
        .first()
    )

    if categoria_peor_calificada:

        categoria_peor_calificada_nombre = (
            nombres_categorias.get(
                categoria_peor_calificada[
                    'categorizacion'
                ],
                'Categoría desconocida'
            )
        )

        categoria_peor_calificada_valor = (
            categoria_peor_calificada[
                'calificacion_promedio'
            ]
        )

    else:

        categoria_peor_calificada_nombre = None
        categoria_peor_calificada_valor = None

    # ---------------------------------------------------------
    # 10. DISTRIBUCIÓN DE CALIFICACIONES
    # ---------------------------------------------------------

    distribucion_calificaciones = (
        cagadas
        .values(
            'categorizacion',
            'calificacion'
        )
        .annotate(
            cantidad=Count('id')
        )
        .order_by(
            'categorizacion',
            'calificacion'
        )
    )

    distribucion_por_categoria = {}

    for resultado in distribucion_calificaciones:

        categoria_id = resultado[
            'categorizacion'
        ]

        if categoria_id not in (
            distribucion_por_categoria
        ):
            distribucion_por_categoria[
                categoria_id
            ] = []

        distribucion_por_categoria[
            categoria_id
        ].append({
            'calificacion': (
                resultado['calificacion']
            ),
            'cantidad': (
                resultado['cantidad']
            ),
        })

    # =========================================================
    # FASE D - ANALÍTICA ESPACIAL
    # =========================================================

    estadisticas_ubicacion = (
        cagadas
        .filter(ubicacion__isnull=False)
        .values(
            'ubicacion',
            'ubicacion__nombre',
            'ubicacion__latitud',
            'ubicacion__longitud'
        )
        .annotate(
            cantidad=Count('id'),
            duracion_total=Sum('duracion'),
            duracion_promedio=Avg('duracion'),
            calificacion_promedio=Avg('calificacion')
        )
        .order_by('-cantidad')
    )

    analitica_ubicaciones = []

    for ubicacion in estadisticas_ubicacion:
        cantidad = ubicacion['cantidad']

        if total_cagadas:
            porcentaje = (cantidad / total_cagadas) * 100
        else:
            porcentaje = 0

        analitica_ubicaciones.append({
            'id': ubicacion['ubicacion'],
            'nombre': ubicacion['ubicacion__nombre'],
            'cantidad': cantidad,
            'porcentaje': porcentaje,
            'duracion_total': ubicacion['duracion_total'],
            'duracion_promedio': ubicacion['duracion_promedio'],
            'calificacion_promedio': ubicacion['calificacion_promedio'],
            'latitud': ubicacion['ubicacion__latitud'],
            'longitud': ubicacion['ubicacion__longitud'],
        })

    ubicacion_mas_utilizada = (
        cagadas
        .filter(ubicacion__isnull=False)
        .values(
            'ubicacion',
            'ubicacion__nombre'
        )
        .annotate(
            cantidad=Count('id')
        )
        .order_by('-cantidad')
        .first()
    )

    if ubicacion_mas_utilizada:
        ubicacion_mas_utilizada_nombre = (
            ubicacion_mas_utilizada['ubicacion__nombre']
        )
        ubicacion_mas_utilizada_cantidad = (
            ubicacion_mas_utilizada['cantidad']
        )
    else:
        ubicacion_mas_utilizada_nombre = None
        ubicacion_mas_utilizada_cantidad = None

    ubicacion_mayor_duracion = (
        cagadas
        .filter(ubicacion__isnull=False)
        .values(
            'ubicacion',
            'ubicacion__nombre'
        )
        .annotate(
            duracion_promedio=Avg('duracion')
        )
        .order_by('-duracion_promedio')
        .first()
    )

    if ubicacion_mayor_duracion:
        ubicacion_mayor_duracion_nombre = (
            ubicacion_mayor_duracion['ubicacion__nombre']
        )
        ubicacion_mayor_duracion_valor = (
            ubicacion_mayor_duracion['duracion_promedio']
        )
    else:
        ubicacion_mayor_duracion_nombre = None
        ubicacion_mayor_duracion_valor = None

    ubicacion_menor_duracion = (
        cagadas
        .filter(ubicacion__isnull=False)
        .values(
            'ubicacion',
            'ubicacion__nombre'
        )
        .annotate(
            duracion_promedio=Avg('duracion')
        )
        .order_by('duracion_promedio')
        .first()
    )

    if ubicacion_menor_duracion:
        ubicacion_menor_duracion_nombre = (
            ubicacion_menor_duracion['ubicacion__nombre']
        )
        ubicacion_menor_duracion_valor = (
            ubicacion_menor_duracion['duracion_promedio']
        )
    else:
        ubicacion_menor_duracion_nombre = None
        ubicacion_menor_duracion_valor = None

    ubicacion_mejor_calificada = (
        cagadas
        .filter(ubicacion__isnull=False)
        .values(
            'ubicacion',
            'ubicacion__nombre'
        )
        .annotate(
            calificacion_promedio=Avg('calificacion')
        )
        .order_by('-calificacion_promedio')
        .first()
    )

    if ubicacion_mejor_calificada:
        ubicacion_mejor_calificada_nombre = (
            ubicacion_mejor_calificada['ubicacion__nombre']
        )
        ubicacion_mejor_calificada_valor = (
            ubicacion_mejor_calificada['calificacion_promedio']
        )
    else:
        ubicacion_mejor_calificada_nombre = None
        ubicacion_mejor_calificada_valor = None

    ubicacion_peor_calificada = (
        cagadas
        .filter(ubicacion__isnull=False)
        .values(
            'ubicacion',
            'ubicacion__nombre'
        )
        .annotate(
            calificacion_promedio=Avg('calificacion')
        )
        .order_by('calificacion_promedio')
        .first()
    )

    if ubicacion_peor_calificada:
        ubicacion_peor_calificada_nombre = (
            ubicacion_peor_calificada['ubicacion__nombre']
        )
        ubicacion_peor_calificada_valor = (
            ubicacion_peor_calificada['calificacion_promedio']
        )
    else:
        ubicacion_peor_calificada_nombre = None
        ubicacion_peor_calificada_valor = None

    ubicacion_mayor_tiempo = (
        cagadas
        .filter(ubicacion__isnull=False)
        .values(
            'ubicacion',
            'ubicacion__nombre'
        )
        .annotate(
            duracion_total=Sum('duracion')
        )
        .order_by('-duracion_total')
        .first()
    )

    if ubicacion_mayor_tiempo:
        ubicacion_mayor_tiempo_nombre = (
            ubicacion_mayor_tiempo['ubicacion__nombre']
        )
        ubicacion_mayor_tiempo_valor = (
            ubicacion_mayor_tiempo['duracion_total']
        )
    else:
        ubicacion_mayor_tiempo_nombre = None
        ubicacion_mayor_tiempo_valor = None

    # =========================================================
    # USUARIOS DISPONIBLES PARA COMPARACIÓN
    # =========================================================
    usuarios_comparables = (
        Usuario.objects
        .filter(is_active=True)
        .exclude(id=request.user.id)
        .order_by('username')
    )

    # =========================================================
    # CONTEXTO ANALYTICS INDIVIDUAL
    # =========================================================

    contexto = {
        # Fase A
        'resumen': resumen,
        'categoria_mas_usada': (
            categoria_mas_usada_nombre
        ),
        'ubicacion_mas_usada': (
            ubicacion_mas_usada[
                'ubicacion__nombre'
            ]
            if ubicacion_mas_usada
            else None
        ),

        # Fase B
        'cagadas_por_dia': cagadas_por_dia,
        'cagadas_por_hora': cagadas_por_hora,
        'cagadas_por_mes': cagadas_por_mes,
        'duracion_promedio_por_dia': (
            duracion_promedio_por_dia
        ),
        'calificacion_promedio_por_dia': (
            calificacion_promedio_por_dia
        ),
        'duracion_promedio_por_hora': (
            duracion_promedio_por_hora
        ),

        # Fase C
        'analitica_categorias': (
            analitica_categorias
        ),
        'categoria_mayor_duracion_nombre': (
            categoria_mayor_duracion_nombre
        ),
        'categoria_mayor_duracion_valor': (
            categoria_mayor_duracion_valor
        ),
        'categoria_mas_frecuente_nombre': (
            categoria_mas_frecuente_nombre
        ),
        'categoria_mas_frecuente_cantidad': (
            categoria_mas_frecuente_cantidad
        ),
        'categoria_mejor_calificada_nombre': (
            categoria_mejor_calificada_nombre
        ),
        'categoria_mejor_calificada_valor': (
            categoria_mejor_calificada_valor
        ),
        'categoria_peor_calificada_nombre': (
            categoria_peor_calificada_nombre
        ),
        'categoria_peor_calificada_valor': (
            categoria_peor_calificada_valor
        ),
        'distribucion_por_categoria': (
            distribucion_por_categoria
        ),

        # Fase D
        'analitica_ubicaciones': analitica_ubicaciones,
        'ubicacion_mas_utilizada_nombre': ubicacion_mas_utilizada_nombre,
        'ubicacion_mas_utilizada_cantidad': ubicacion_mas_utilizada_cantidad,
        'ubicacion_mayor_duracion_nombre': ubicacion_mayor_duracion_nombre,
        'ubicacion_mayor_duracion_valor': ubicacion_mayor_duracion_valor,
        'ubicacion_menor_duracion_nombre': ubicacion_menor_duracion_nombre,
        'ubicacion_menor_duracion_valor': ubicacion_menor_duracion_valor,
        'ubicacion_mejor_calificada_nombre': ubicacion_mejor_calificada_nombre,
        'ubicacion_mejor_calificada_valor': ubicacion_mejor_calificada_valor,
        'ubicacion_peor_calificada_nombre': ubicacion_peor_calificada_nombre,
        'ubicacion_peor_calificada_valor': ubicacion_peor_calificada_valor,
        'ubicacion_mayor_tiempo_nombre': ubicacion_mayor_tiempo_nombre,
        'ubicacion_mayor_tiempo_valor': ubicacion_mayor_tiempo_valor,

        #Fase E
        'usuarios_comparables': usuarios_comparables,
    }

    return render(
        request,
        'analytics/analytics.html',
        contexto
    )


# =========================================================
# FASE E - ANÁLISIS DE COMPARACIÓN ENTRE USUARIOS
# =========================================================
@login_required
def analytics_comparacion(request, usuario_id):
    """
    Compara las métricas públicas de uso entre el usuario autenticado
    y otro usuario seleccionado (resumen, categorías, temporalidad y ubicaciones).
    """

    usuario_actual = request.user

    usuario_comparado = get_object_or_404(
        Usuario,
        id=usuario_id
    )

    # No permitimos compararse contra uno mismo
    if usuario_comparado.id == usuario_actual.id:
        return redirect('analytics')

    # ==========================================
    # DATOS PÚBLICOS DE AMBOS USUARIOS
    # ==========================================

    cagadas_actual = Cagada.objects.filter(
        usuario=usuario_actual,
        visible_para_otros=True
    )

    cagadas_comparado = Cagada.objects.filter(
        usuario=usuario_comparado,
        visible_para_otros=True
    )

    # ==========================================
    # RESUMEN GENERAL
    # ==========================================

    resumen_actual = cagadas_actual.aggregate(
        total_cagadas=Count('id'),
        duracion_total=Sum('duracion'),
        duracion_promedio=Avg('duracion'),
        calificacion_promedio=Avg('calificacion'),
    )

    resumen_comparado = cagadas_comparado.aggregate(
        total_cagadas=Count('id'),
        duracion_total=Sum('duracion'),
        duracion_promedio=Avg('duracion'),
        calificacion_promedio=Avg('calificacion'),
    )

    # ==========================================
    # CATEGORÍAS
    # ==========================================

    estadisticas_actual = (
        cagadas_actual
        .values('categorizacion')
        .annotate(
            cantidad=Count('id'),
            duracion_promedio=Avg('duracion'),
            calificacion_promedio=Avg('calificacion'),
        )
    )

    estadisticas_comparado = (
        cagadas_comparado
        .values('categorizacion')
        .annotate(
            cantidad=Count('id'),
            duracion_promedio=Avg('duracion'),
            calificacion_promedio=Avg('calificacion'),
        )
    )

    categorias_actual = {
        item['categorizacion']: item
        for item in estadisticas_actual
    }

    categorias_comparado = {
        item['categorizacion']: item
        for item in estadisticas_comparado
    }

    nombres_categorias = dict(Cagada.CATEGORIAS)

    comparacion_categorias = []

    total_actual = resumen_actual['total_cagadas'] or 0
    total_comparado = resumen_comparado['total_cagadas'] or 0

    for categoria_id, nombre in nombres_categorias.items():

        actual = categorias_actual.get(categoria_id, {})
        comparado = categorias_comparado.get(categoria_id, {})

        cantidad_actual = actual.get('cantidad', 0)
        cantidad_comparado = comparado.get('cantidad', 0)

        comparacion_categorias.append({
            'id': categoria_id,
            'nombre': nombre,

            'actual': {
                'cantidad': cantidad_actual,
                'porcentaje': (
                    cantidad_actual / total_actual * 100
                    if total_actual else 0
                ),
                'duracion_promedio': actual.get(
                    'duracion_promedio'
                ),
                'calificacion_promedio': actual.get(
                    'calificacion_promedio'
                ),
            },

            'comparado': {
                'cantidad': cantidad_comparado,
                'porcentaje': (
                    cantidad_comparado / total_comparado * 100
                    if total_comparado else 0
                ),
                'duracion_promedio': comparado.get(
                    'duracion_promedio'
                ),
                'calificacion_promedio': comparado.get(
                    'calificacion_promedio'
                ),
            }
        })

    # ==========================================
    # TEMPORAL
    # ==========================================

    def datos_temporales(cagadas):

        por_dia = (
            cagadas
            .annotate(dia=ExtractWeekDay('hora_inicio_cagada'))
            .values('dia')
            .annotate(
                cantidad=Count('id'),
                duracion_promedio=Avg('duracion'),
                calificacion_promedio=Avg('calificacion'),
            )
            .order_by('dia')
        )

        por_hora = (
            cagadas
            .annotate(hora=ExtractHour('hora_inicio_cagada'))
            .values('hora')
            .annotate(
                cantidad=Count('id'),
                duracion_promedio=Avg('duracion'),
            )
            .order_by('hora')
        )

        return {
            'por_dia': {
                item['dia']: item
                for item in por_dia
            },
            'por_hora': {
                item['hora']: item
                for item in por_hora
            },
        }

    temporal_actual = datos_temporales(cagadas_actual)
    temporal_comparado = datos_temporales(cagadas_comparado)

    # ==========================================
    # COMPARACIÓN POR DÍA
    # ==========================================

    nombres_dias = {
        1: 'Domingo',
        2: 'Lunes',
        3: 'Martes',
        4: 'Miércoles',
        5: 'Jueves',
        6: 'Viernes',
        7: 'Sábado',
    }

    comparacion_dias = []

    for dia_id, nombre in nombres_dias.items():

        actual = temporal_actual['por_dia'].get(dia_id, {})
        comparado = temporal_comparado['por_dia'].get(dia_id, {})

        comparacion_dias.append({
            'id': dia_id,
            'nombre': nombre,

            'actual': {
                'cantidad': actual.get('cantidad', 0),
                'duracion_promedio': actual.get(
                    'duracion_promedio'
                ),
                'calificacion_promedio': actual.get(
                    'calificacion_promedio'
                ),
            },

            'comparado': {
                'cantidad': comparado.get('cantidad', 0),
                'duracion_promedio': comparado.get(
                    'duracion_promedio'
                ),
                'calificacion_promedio': comparado.get(
                    'calificacion_promedio'
                ),
            }
        })

    # ==========================================
    # COMPARACIÓN POR HORA
    # ==========================================

    comparacion_horas = []

    for hora in range(24):

        actual = temporal_actual['por_hora'].get(hora, {})
        comparado = temporal_comparado['por_hora'].get(hora, {})

        comparacion_horas.append({
            'hora': hora,

            'actual': {
                'cantidad': actual.get('cantidad', 0),
                'duracion_promedio': actual.get(
                    'duracion_promedio'
                ),
            },

            'comparado': {
                'cantidad': comparado.get('cantidad', 0),
                'duracion_promedio': comparado.get(
                    'duracion_promedio'
                ),
            }
        })

    # ==========================================
    # UBICACIONES
    # ==========================================
    # Solamente contamos cuántas ubicaciones públicas
    # diferentes utiliza cada usuario.
    #
    # NO enviamos nombres ni coordenadas del otro usuario.

    ubicaciones_actual = (
        cagadas_actual
        .filter(ubicacion__isnull=False)
        .values('ubicacion')
        .distinct()
        .count()
    )

    ubicaciones_comparado = (
        cagadas_comparado
        .filter(ubicacion__isnull=False)
        .values('ubicacion')
        .distinct()
        .count()
    )

    usuarios_comparables = (
        Usuario.objects
        .filter(is_active=True)
        .exclude(id=request.user.id)
        .order_by('username')
    )

    # ==========================================
    # CONTEXTO COMPARACIÓN
    # ==========================================

    context = {
        'usuario_actual': usuario_actual,
        'usuario_comparado': usuario_comparado,

        'resumen_actual': resumen_actual,
        'resumen_comparado': resumen_comparado,

        'comparacion_categorias': comparacion_categorias,

        'comparacion_dias': comparacion_dias,
        'comparacion_horas': comparacion_horas,

        'ubicaciones_actual': ubicaciones_actual,
        'ubicaciones_comparado': ubicaciones_comparado,

        'usuarios_comparables': usuarios_comparables,
    }

    return render(
        request,
        'analytics/comparacion.html',
        context
    )