# crm/services_balance.py
from decimal import Decimal
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Q, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from .models import Venta, Importacion, GastoOperacional


def calcular_balance_mensual(anio, mes):
    """
    Calcula el balance completo para un mes específico.
    
    Returns:
        dict con estructura:
        {
            'periodo': {'anio': int, 'mes': int, 'mes_nombre': str},
            'ingresos': {...},
            'costos': {...},
            'gastos': {...},
            'utilidad_bruta': Decimal,
            'utilidad_operacional': Decimal,
            'utilidad_neta': Decimal,
            'margen_bruto_pct': Decimal,
            'margen_operacional_pct': Decimal,
            'margen_neto_pct': Decimal,
        }
    """
    # Crear fecha de inicio y fin del mes
    fecha_inicio = date(anio, mes, 1)
    if mes == 12:
        fecha_fin = date(anio + 1, 1, 1)
    else:
        fecha_fin = date(anio, mes + 1, 1)
    
    # === INGRESOS ===
    ventas = Venta.objects.filter(
        fecha__gte=fecha_inicio,
        fecha__lt=fecha_fin
    )
    
    total_ventas_bruto = ventas.aggregate(
        total=Sum('monto_total')
    )['total'] or Decimal('0.00')
    
    # Calcular neto e IVA
    total_ventas_neto = (total_ventas_bruto / Decimal('1.19')).quantize(Decimal('0.01'))
    iva_ventas = (total_ventas_bruto - total_ventas_neto).quantize(Decimal('0.01'))
    
    kilos_vendidos = ventas.aggregate(
        total=Sum('kilos_total')
    )['total'] or Decimal('0.00')
    
    num_ventas = ventas.count()
    ticket_promedio = (total_ventas_bruto / num_ventas).quantize(Decimal('0.01')) if num_ventas > 0 else Decimal('0.00')
    
    # Ventas por canal
    ventas_por_canal = {}
    for canal_code, canal_name in Venta.Canal.choices:
        total = ventas.filter(canal=canal_code).aggregate(
            total=Sum('monto_total')
        )['total'] or Decimal('0.00')
        ventas_por_canal[canal_name] = total
    
    ingresos = {
        'total_bruto': total_ventas_bruto,
        'total_neto': total_ventas_neto,
        'iva': iva_ventas,
        'kilos_vendidos': kilos_vendidos,
        'num_ventas': num_ventas,
        'ticket_promedio': ticket_promedio,
        'por_canal': ventas_por_canal,
    }
    
    # === COSTOS DE MERCADERÍA ===
    # Obtener importaciones activas en el período
    importaciones = Importacion.objects.filter(
        activo=True,
        fecha__lte=fecha_fin
    )
    
    # Calcular costo promedio ponderado
    if importaciones.exists():
        total_kilos = Decimal('0.00')
        total_costo = Decimal('0.00')
        
        for imp in importaciones:
            kilos_netos = imp.kilos_ingresados - imp.merma_kg
            total_kilos += kilos_netos
            total_costo += imp.costo_total
        
        if total_kilos > 0:
            costo_promedio_kg = (total_costo / total_kilos).quantize(Decimal('0.01'))
        else:
            costo_promedio_kg = Decimal('0.00')
    else:
        costo_promedio_kg = Decimal('0.00')
    
    # Costo de mercadería vendida (CMV)
    cmv = (kilos_vendidos * costo_promedio_kg).quantize(Decimal('0.01'))
    
    costos = {
        'cmv': cmv,
        'costo_promedio_kg': costo_promedio_kg,
        'kilos_vendidos': kilos_vendidos,
    }
    
    # === GASTOS OPERACIONALES ===
    gastos_mes = GastoOperacional.objects.filter(
        fecha__gte=fecha_inicio,
        fecha__lt=fecha_fin
    )
    
    gastos_por_tipo = {}
    total_gastos_neto = Decimal('0.00')
    total_iva_gastos = Decimal('0.00')
    
    for tipo_code, tipo_name in GastoOperacional.Tipo.choices:
        gastos_tipo = gastos_mes.filter(tipo=tipo_code)
        neto = gastos_tipo.aggregate(total=Sum('monto_neto'))['total'] or Decimal('0.00')
        
        # Calcular IVA solo para gastos que lo aplican
        iva = Decimal('0.00')
        for gasto in gastos_tipo.filter(aplica_iva=True):
            iva += gasto.iva
        
        total = neto + iva
        
        gastos_por_tipo[tipo_name] = {
            'neto': neto,
            'iva': iva,
            'total': total,
            'cantidad': gastos_tipo.count()
        }
        
        total_gastos_neto += neto
        total_iva_gastos += iva
    
    total_gastos = total_gastos_neto + total_iva_gastos
    
    gastos = {
        'total_neto': total_gastos_neto,
        'total_iva': total_iva_gastos,
        'total': total_gastos,
        'por_tipo': gastos_por_tipo,
    }
    
    # === UTILIDADES ===
    utilidad_bruta = (total_ventas_neto - cmv).quantize(Decimal('0.01'))
    utilidad_operacional = (utilidad_bruta - total_gastos_neto).quantize(Decimal('0.01'))
    
    # La utilidad neta considera también el IVA (es la utilidad real después de impuestos)
    # En Chile, el IVA es un impuesto que se paga/recupera, pero afecta el flujo de caja
    utilidad_neta = (utilidad_operacional - total_iva_gastos).quantize(Decimal('0.01'))
    
    # Márgenes porcentuales
    if total_ventas_neto > 0:
        margen_bruto_pct = ((utilidad_bruta / total_ventas_neto) * Decimal('100')).quantize(Decimal('0.01'))
        margen_operacional_pct = ((utilidad_operacional / total_ventas_neto) * Decimal('100')).quantize(Decimal('0.01'))
        margen_neto_pct = ((utilidad_neta / total_ventas_neto) * Decimal('100')).quantize(Decimal('0.01'))
    else:
        margen_bruto_pct = Decimal('0.00')
        margen_operacional_pct = Decimal('0.00')
        margen_neto_pct = Decimal('0.00')
    
    # Nombre del mes en español
    meses_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    return {
        'periodo': {
            'anio': anio,
            'mes': mes,
            'mes_nombre': meses_es[mes - 1],
        },
        'ingresos': ingresos,
        'costos': costos,
        'gastos': gastos,
        'utilidad_bruta': utilidad_bruta,
        'utilidad_operacional': utilidad_operacional,
        'utilidad_neta': utilidad_neta,
        'margen_bruto_pct': margen_bruto_pct,
        'margen_operacional_pct': margen_operacional_pct,
        'margen_neto_pct': margen_neto_pct,
    }


def calcular_balance_anual(anio):
    """
    Calcula el balance para todos los meses de un año.
    
    Returns:
        {
            'anio': int,
            'meses': [balance_mes1, balance_mes2, ...],
            'totales': {...},
            'promedios': {...}
        }
    """
    meses_data = []
    
    # Calcular balance para cada mes
    for mes in range(1, 13):
        balance_mes = calcular_balance_mensual(anio, mes)
        meses_data.append(balance_mes)
    
    # Calcular totales anuales
    total_ingresos = sum(m['ingresos']['total_bruto'] for m in meses_data)
    total_ingresos_neto = sum(m['ingresos']['total_neto'] for m in meses_data)
    total_cmv = sum(m['costos']['cmv'] for m in meses_data)
    total_gastos = sum(m['gastos']['total'] for m in meses_data)
    total_gastos_neto = sum(m['gastos']['total_neto'] for m in meses_data)
    total_kilos = sum(m['ingresos']['kilos_vendidos'] for m in meses_data)
    total_ventas = sum(m['ingresos']['num_ventas'] for m in meses_data)
    
    utilidad_bruta_anual = sum(m['utilidad_bruta'] for m in meses_data)
    utilidad_operacional_anual = sum(m['utilidad_operacional'] for m in meses_data)
    utilidad_neta_anual = sum(m['utilidad_neta'] for m in meses_data)
    
    # Calcular márgenes anuales
    if total_ingresos_neto > 0:
        margen_bruto_anual = ((utilidad_bruta_anual / total_ingresos_neto) * Decimal('100')).quantize(Decimal('0.01'))
        margen_operacional_anual = ((utilidad_operacional_anual / total_ingresos_neto) * Decimal('100')).quantize(Decimal('0.01'))
        margen_neto_anual = ((utilidad_neta_anual / total_ingresos_neto) * Decimal('100')).quantize(Decimal('0.01'))
    else:
        margen_bruto_anual = Decimal('0.00')
        margen_operacional_anual = Decimal('0.00')
        margen_neto_anual = Decimal('0.00')
    
    # Promedios mensuales
    ticket_promedio_anual = (total_ingresos / total_ventas).quantize(Decimal('0.01')) if total_ventas > 0 else Decimal('0.00')
    
    totales = {
        'ingresos_bruto': total_ingresos,
        'ingresos_neto': total_ingresos_neto,
        'cmv': total_cmv,
        'gastos': total_gastos,
        'gastos_neto': total_gastos_neto,
        'kilos_vendidos': total_kilos,
        'num_ventas': total_ventas,
        'utilidad_bruta': utilidad_bruta_anual,
        'utilidad_operacional': utilidad_operacional_anual,
        'utilidad_neta': utilidad_neta_anual,
        'margen_bruto_pct': margen_bruto_anual,
        'margen_operacional_pct': margen_operacional_anual,
        'margen_neto_pct': margen_neto_anual,
    }
    
    promedios = {
        'ingresos_mensual': (total_ingresos / Decimal('12')).quantize(Decimal('0.01')),
        'gastos_mensual': (total_gastos / Decimal('12')).quantize(Decimal('0.01')),
        'utilidad_mensual': (utilidad_neta_anual / Decimal('12')).quantize(Decimal('0.01')),
        'ticket_promedio': ticket_promedio_anual,
        'ventas_mensuales': int(total_ventas / 12),
    }
    
    return {
        'anio': anio,
        'meses': meses_data,
        'totales': totales,
        'promedios': promedios,
    }


def calcular_comparativa_anual(anios):
    """
    Compara múltiples años.
    
    Args:
        anios: lista de años a comparar, ej: [2024, 2025, 2026]
    
    Returns:
        {
            'anios': [datos_año1, datos_año2, ...],
            'comparativa': {...}
        }
    """
    anios_data = []
    
    for anio in anios:
        balance = calcular_balance_anual(anio)
        anios_data.append(balance)
    
    # Calcular tasas de crecimiento año a año
    comparativa = {}
    
    if len(anios_data) > 1:
        for i in range(1, len(anios_data)):
            anio_actual = anios_data[i]
            anio_anterior = anios_data[i-1]
            
            crecimiento_ingresos = Decimal('0.00')
            crecimiento_utilidad = Decimal('0.00')
            
            if anio_anterior['totales']['ingresos_bruto'] > 0:
                crecimiento_ingresos = (
                    ((anio_actual['totales']['ingresos_bruto'] - anio_anterior['totales']['ingresos_bruto']) / 
                     anio_anterior['totales']['ingresos_bruto']) * Decimal('100')
                ).quantize(Decimal('0.01'))
            
            if anio_anterior['totales']['utilidad_neta'] != 0:
                crecimiento_utilidad = (
                    ((anio_actual['totales']['utilidad_neta'] - anio_anterior['totales']['utilidad_neta']) / 
                     abs(anio_anterior['totales']['utilidad_neta'])) * Decimal('100')
                ).quantize(Decimal('0.01'))
            
            comparativa[f'{anio_anterior["anio"]}-{anio_actual["anio"]}'] = {
                'crecimiento_ingresos_pct': crecimiento_ingresos,
                'crecimiento_utilidad_pct': crecimiento_utilidad,
            }
    
    return {
        'anios': anios_data,
        'comparativa': comparativa,
    }
