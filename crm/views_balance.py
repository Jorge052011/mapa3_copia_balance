# crm/views_balance.py
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from .services_balance import (
    calcular_balance_mensual,
    calcular_balance_anual,
    calcular_comparativa_anual
)
from decimal import Decimal


def balance_mensual(request):
    """Vista para mostrar el balance de un mes específico"""
    # Obtener mes y año de la query string o usar el mes actual
    hoy = timezone.now()
    mes = int(request.GET.get('mes', hoy.month))
    anio = int(request.GET.get('anio', hoy.year))
    
    # Validar rango
    if not (1 <= mes <= 12):
        mes = hoy.month
    
    balance = calcular_balance_mensual(anio, mes)
    
    # Convertir Decimals a float para el template
    context = _convertir_decimales(balance)
    context['mes_actual'] = mes
    context['anio_actual'] = anio
    
    # Generar opciones para el selector de mes
    meses = []
    for i in range(1, 13):
        meses.append({
            'numero': i,
            'nombre': balance['periodo']['mes_nombre'] if i == mes else [
                'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
            ][i-1]
        })
    context['meses'] = meses
    
    # Años disponibles (últimos 3 años + año actual)
    anio_inicio = hoy.year - 3
    context['anios'] = list(range(anio_inicio, hoy.year + 1))
    
    return render(request, 'crm/balance_mensual.html', context)


def balance_anual(request):
    """Vista para mostrar el balance anual"""
    hoy = timezone.now()
    anio = int(request.GET.get('anio', hoy.year))
    
    balance = calcular_balance_anual(anio)
    
    context = _convertir_decimales(balance)
    context['anio_actual'] = anio
    
    # Años disponibles
    anio_inicio = hoy.year - 3
    context['anios'] = list(range(anio_inicio, hoy.year + 1))
    
    return render(request, 'crm/balance_anual.html', context)


def balance_comparativo(request):
    """Vista para comparar múltiples años"""
    hoy = timezone.now()
    
    # Por defecto, comparar los últimos 3 años
    anios_param = request.GET.get('anios', '')
    if anios_param:
        anios = [int(a) for a in anios_param.split(',') if a.isdigit()]
    else:
        anios = [hoy.year - 2, hoy.year - 1, hoy.year]
    
    # Limitar a máximo 5 años
    anios = anios[:5]
    
    comparativa = calcular_comparativa_anual(anios)
    
    context = _convertir_decimales(comparativa)
    context['anios_seleccionados'] = anios
    
    # Años disponibles
    anio_inicio = hoy.year - 5
    context['anios_disponibles'] = list(range(anio_inicio, hoy.year + 1))
    
    return render(request, 'crm/balance_comparativo.html', context)


# ===== API ENDPOINTS =====

def api_balance_mensual(request, anio, mes):
    """API endpoint para obtener balance mensual en JSON"""
    try:
        if not (1 <= mes <= 12):
            return JsonResponse({'error': 'Mes inválido'}, status=400)
        
        balance = calcular_balance_mensual(anio, mes)
        data = _convertir_decimales_json(balance)
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_balance_anual(request, anio):
    """API endpoint para obtener balance anual en JSON"""
    try:
        balance = calcular_balance_anual(anio)
        data = _convertir_decimales_json(balance)
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_balance_comparativo(request):
    """API endpoint para comparar múltiples años"""
    try:
        anios_param = request.GET.get('anios', '')
        if not anios_param:
            return JsonResponse({'error': 'Parámetro anios requerido'}, status=400)
        
        anios = [int(a) for a in anios_param.split(',') if a.isdigit()]
        if not anios:
            return JsonResponse({'error': 'Años inválidos'}, status=400)
        
        comparativa = calcular_comparativa_anual(anios)
        data = _convertir_decimales_json(comparativa)
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ===== UTILIDADES =====

def _convertir_decimales(obj):
    """Convierte recursivamente Decimals a float para templates"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _convertir_decimales(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convertir_decimales(item) for item in obj]
    else:
        return obj


def _convertir_decimales_json(obj):
    """Convierte recursivamente Decimals a string para JSON"""
    if isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: _convertir_decimales_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convertir_decimales_json(item) for item in obj]
    else:
        return obj
