"""
Script de ejemplo para probar el sistema de balance contable

Este script muestra cómo usar las funciones de balance programáticamente
y genera un reporte de ejemplo.

Uso:
    python manage.py shell < test_balance.py
    
O desde el shell de Django:
    from crm.scripts import test_balance
    test_balance.generar_reporte_completo()
"""

from datetime import datetime
from crm.services_balance import (
    calcular_balance_mensual,
    calcular_balance_anual,
    calcular_comparativa_anual
)


def generar_reporte_mensual(anio, mes):
    """Genera un reporte de balance mensual en consola"""
    print("=" * 80)
    print(f"BALANCE MENSUAL - {mes:02d}/{anio}")
    print("=" * 80)
    
    balance = calcular_balance_mensual(anio, mes)
    
    print(f"\n📅 PERÍODO: {balance['periodo']['mes_nombre']} {balance['periodo']['anio']}\n")
    
    print("💰 INGRESOS:")
    print(f"  Total Bruto (con IVA): ${balance['ingresos']['total_bruto']:,.0f}")
    print(f"  Total Neto (sin IVA):  ${balance['ingresos']['total_neto']:,.0f}")
    print(f"  IVA:                   ${balance['ingresos']['iva']:,.0f}")
    print(f"  Kilos Vendidos:        {balance['ingresos']['kilos_vendidos']:,.0f} kg")
    print(f"  Número de Ventas:      {balance['ingresos']['num_ventas']}")
    print(f"  Ticket Promedio:       ${balance['ingresos']['ticket_promedio']:,.0f}")
    
    print("\n📦 COSTOS:")
    print(f"  Costo Mercadería Vendida: ${balance['costos']['cmv']:,.0f}")
    print(f"  Costo Promedio/kg:        ${balance['costos']['costo_promedio_kg']:,.2f}")
    
    print("\n💸 GASTOS OPERACIONALES:")
    print(f"  Total Gastos (sin IVA): ${balance['gastos']['total_neto']:,.0f}")
    print(f"  IVA Gastos:             ${balance['gastos']['total_iva']:,.0f}")
    print(f"  Total con IVA:          ${balance['gastos']['total']:,.0f}")
    
    print("\n  Detalle por tipo:")
    for tipo, datos in balance['gastos']['por_tipo'].items():
        if datos['neto'] > 0:
            print(f"    - {tipo:20s}: ${datos['total']:>10,.0f} ({datos['cantidad']} registro(s))")
    
    print("\n📈 UTILIDADES:")
    print(f"  Utilidad Bruta:        ${balance['utilidad_bruta']:>12,.0f} ({balance['margen_bruto_pct']:>5.1f}%)")
    print(f"  Utilidad Operacional:  ${balance['utilidad_operacional']:>12,.0f} ({balance['margen_operacional_pct']:>5.1f}%)")
    print(f"  Utilidad Neta:         ${balance['utilidad_neta']:>12,.0f} ({balance['margen_neto_pct']:>5.1f}%)")
    
    print("\n📊 VENTAS POR CANAL:")
    for canal, monto in balance['ingresos']['por_canal'].items():
        if monto > 0:
            porcentaje = (monto / balance['ingresos']['total_bruto']) * 100
            print(f"  {canal:15s}: ${monto:>10,.0f} ({porcentaje:>5.1f}%)")
    
    print("\n" + "=" * 80)
    
    return balance


def generar_reporte_anual(anio):
    """Genera un reporte de balance anual en consola"""
    print("=" * 80)
    print(f"BALANCE ANUAL {anio}")
    print("=" * 80)
    
    balance = calcular_balance_anual(anio)
    
    print(f"\n📊 TOTALES ANUALES {anio}:\n")
    print(f"  Ingresos Brutos:       ${balance['totales']['ingresos_bruto']:>15,.0f}")
    print(f"  Ingresos Netos:        ${balance['totales']['ingresos_neto']:>15,.0f}")
    print(f"  Costo Mercadería:      ${balance['totales']['cmv']:>15,.0f}")
    print(f"  Gastos Operacionales:  ${balance['totales']['gastos_neto']:>15,.0f}")
    print(f"  Utilidad Bruta:        ${balance['totales']['utilidad_bruta']:>15,.0f}")
    print(f"  Utilidad Neta:         ${balance['totales']['utilidad_neta']:>15,.0f}")
    print(f"  Kilos Vendidos:        {balance['totales']['kilos_vendidos']:>15,.0f} kg")
    print(f"  Número de Ventas:      {balance['totales']['num_ventas']:>15,}")
    
    print(f"\n💹 MÁRGENES ANUALES:\n")
    print(f"  Margen Bruto:          {balance['totales']['margen_bruto_pct']:>15.2f}%")
    print(f"  Margen Operacional:    {balance['totales']['margen_operacional_pct']:>15.2f}%")
    print(f"  Margen Neto:           {balance['totales']['margen_neto_pct']:>15.2f}%")
    
    print(f"\n📈 PROMEDIOS MENSUALES:\n")
    print(f"  Ingresos/mes:          ${balance['promedios']['ingresos_mensual']:>15,.0f}")
    print(f"  Gastos/mes:            ${balance['promedios']['gastos_mensual']:>15,.0f}")
    print(f"  Utilidad/mes:          ${balance['promedios']['utilidad_mensual']:>15,.0f}")
    print(f"  Ticket Promedio:       ${balance['promedios']['ticket_promedio']:>15,.0f}")
    print(f"  Ventas/mes:            {balance['promedios']['ventas_mensuales']:>15,}")
    
    print("\n📅 EVOLUCIÓN MENSUAL:\n")
    print(f"{'Mes':<12} {'Ingresos':>12} {'Utilidad':>12} {'Margen %':>10} {'Ventas':>8}")
    print("-" * 60)
    
    for mes in balance['meses']:
        print(f"{mes['periodo']['mes_nombre']:<12} "
              f"${mes['ingresos']['total_neto']:>11,.0f} "
              f"${mes['utilidad_neta']:>11,.0f} "
              f"{mes['margen_neto_pct']:>9.1f}% "
              f"{mes['ingresos']['num_ventas']:>7}")
    
    print("=" * 80)
    
    return balance


def generar_comparativa(anios):
    """Genera una comparativa entre años"""
    print("=" * 100)
    print(f"COMPARATIVA DE AÑOS: {', '.join(map(str, anios))}")
    print("=" * 100)
    
    comparativa = calcular_comparativa_anual(anios)
    
    print(f"\n{'Concepto':<30} ", end='')
    for anio_data in comparativa['anios']:
        print(f"{anio_data['anio']:>15} ", end='')
    if len(anios) > 1:
        print("Variación", end='')
    print()
    print("-" * 100)
    
    # Ingresos
    print(f"{'Ingresos Totales':<30} ", end='')
    for anio_data in comparativa['anios']:
        print(f"${anio_data['totales']['ingresos_bruto']:>14,.0f} ", end='')
    if len(anios) == 2:
        key = list(comparativa['comparativa'].keys())[0]
        var = comparativa['comparativa'][key]['crecimiento_ingresos_pct']
        print(f"{var:>13.1f}%", end='')
    print()
    
    # Utilidad Neta
    print(f"{'Utilidad Neta':<30} ", end='')
    for anio_data in comparativa['anios']:
        utilidad = anio_data['totales']['utilidad_neta']
        print(f"${utilidad:>14,.0f} ", end='')
    if len(anios) == 2:
        key = list(comparativa['comparativa'].keys())[0]
        var = comparativa['comparativa'][key]['crecimiento_utilidad_pct']
        print(f"{var:>13.1f}%", end='')
    print()
    
    # Margen Neto
    print(f"{'Margen Neto %':<30} ", end='')
    for anio_data in comparativa['anios']:
        print(f"{anio_data['totales']['margen_neto_pct']:>14.2f}% ", end='')
    print()
    
    # Ventas
    print(f"{'Número de Ventas':<30} ", end='')
    for anio_data in comparativa['anios']:
        print(f"{anio_data['totales']['num_ventas']:>15,} ", end='')
    print()
    
    # Kilos
    print(f"{'Kilos Vendidos':<30} ", end='')
    for anio_data in comparativa['anios']:
        print(f"{anio_data['totales']['kilos_vendidos']:>14,.0f} kg ", end='')
    print()
    
    print("\n" + "=" * 100)
    
    return comparativa


def generar_reporte_completo():
    """Genera todos los reportes disponibles"""
    hoy = datetime.now()
    anio_actual = hoy.year
    mes_actual = hoy.month
    
    # Reporte del mes actual
    print("\n🎯 GENERANDO REPORTE DEL MES ACTUAL...")
    generar_reporte_mensual(anio_actual, mes_actual)
    
    # Reporte del año actual
    print("\n\n🎯 GENERANDO REPORTE DEL AÑO ACTUAL...")
    generar_reporte_anual(anio_actual)
    
    # Comparativa últimos 3 años (si existen datos)
    print("\n\n🎯 GENERANDO COMPARATIVA DE AÑOS...")
    anios = [anio_actual - 2, anio_actual - 1, anio_actual]
    generar_comparativa(anios)
    
    print("\n✅ Reportes generados exitosamente!\n")


def exportar_a_csv(anio):
    """
    Exporta el balance anual a formato CSV
    
    Args:
        anio: Año a exportar
        
    Returns:
        str: Nombre del archivo generado
    """
    import csv
    from datetime import datetime
    
    balance = calcular_balance_anual(anio)
    filename = f"balance_{anio}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Encabezados
        writer.writerow([
            'Mes', 'Ingresos Bruto', 'Ingresos Neto', 'CMV', 
            'Gastos', 'Utilidad Bruta', 'Utilidad Neta', 
            'Margen Bruto %', 'Margen Neto %', 'Ventas', 'Kilos'
        ])
        
        # Datos mensuales
        for mes in balance['meses']:
            writer.writerow([
                mes['periodo']['mes_nombre'],
                mes['ingresos']['total_bruto'],
                mes['ingresos']['total_neto'],
                mes['costos']['cmv'],
                mes['gastos']['total_neto'],
                mes['utilidad_bruta'],
                mes['utilidad_neta'],
                mes['margen_bruto_pct'],
                mes['margen_neto_pct'],
                mes['ingresos']['num_ventas'],
                mes['ingresos']['kilos_vendidos'],
            ])
        
        # Totales
        writer.writerow([])
        writer.writerow([
            'TOTAL',
            balance['totales']['ingresos_bruto'],
            balance['totales']['ingresos_neto'],
            balance['totales']['cmv'],
            balance['totales']['gastos_neto'],
            balance['totales']['utilidad_bruta'],
            balance['totales']['utilidad_neta'],
            balance['totales']['margen_bruto_pct'],
            balance['totales']['margen_neto_pct'],
            balance['totales']['num_ventas'],
            balance['totales']['kilos_vendidos'],
        ])
    
    print(f"✅ Balance exportado a: {filename}")
    return filename


# Si se ejecuta directamente
if __name__ == '__main__':
    generar_reporte_completo()
