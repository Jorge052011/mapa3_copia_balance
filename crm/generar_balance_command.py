"""
Comandos de gestión Django personalizados para el sistema de balance

Para usar estos comandos:
1. Crear el directorio: crm/management/commands/
2. Colocar este archivo en ese directorio
3. Ejecutar: python manage.py <nombre_comando>
"""

from django.core.management.base import BaseCommand
from datetime import datetime
from crm.services_balance import (
    calcular_balance_mensual,
    calcular_balance_anual,
    calcular_comparativa_anual
)
from decimal import Decimal


class Command(BaseCommand):
    help = 'Genera reportes de balance contable'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            type=str,
            default='mensual',
            choices=['mensual', 'anual', 'comparativo'],
            help='Tipo de reporte a generar'
        )
        parser.add_argument(
            '--mes',
            type=int,
            help='Mes (1-12) para reporte mensual'
        )
        parser.add_argument(
            '--anio',
            type=int,
            help='Año para el reporte'
        )
        parser.add_argument(
            '--anios',
            type=str,
            help='Años separados por comas para comparativa (ej: 2024,2025)'
        )
        parser.add_argument(
            '--formato',
            type=str,
            default='texto',
            choices=['texto', 'json', 'csv'],
            help='Formato de salida'
        )
        parser.add_argument(
            '--archivo',
            type=str,
            help='Archivo de salida (opcional)'
        )

    def handle(self, *args, **options):
        hoy = datetime.now()
        tipo = options['tipo']
        formato = options['formato']
        
        if tipo == 'mensual':
            mes = options['mes'] or hoy.month
            anio = options['anio'] or hoy.year
            self.generar_mensual(anio, mes, formato, options.get('archivo'))
            
        elif tipo == 'anual':
            anio = options['anio'] or hoy.year
            self.generar_anual(anio, formato, options.get('archivo'))
            
        elif tipo == 'comparativo':
            if options['anios']:
                anios = [int(a) for a in options['anios'].split(',')]
            else:
                anios = [hoy.year - 2, hoy.year - 1, hoy.year]
            self.generar_comparativo(anios, formato, options.get('archivo'))

    def generar_mensual(self, anio, mes, formato, archivo):
        """Genera reporte mensual"""
        balance = calcular_balance_mensual(anio, mes)
        
        if formato == 'json':
            self._exportar_json(balance, archivo)
        elif formato == 'csv':
            self._exportar_csv_mensual(balance, archivo)
        else:
            self._mostrar_mensual_texto(balance)

    def generar_anual(self, anio, formato, archivo):
        """Genera reporte anual"""
        balance = calcular_balance_anual(anio)
        
        if formato == 'json':
            self._exportar_json(balance, archivo)
        elif formato == 'csv':
            self._exportar_csv_anual(balance, archivo)
        else:
            self._mostrar_anual_texto(balance)

    def generar_comparativo(self, anios, formato, archivo):
        """Genera reporte comparativo"""
        comparativa = calcular_comparativa_anual(anios)
        
        if formato == 'json':
            self._exportar_json(comparativa, archivo)
        elif formato == 'csv':
            self._exportar_csv_comparativo(comparativa, archivo)
        else:
            self._mostrar_comparativo_texto(comparativa)

    def _mostrar_mensual_texto(self, balance):
        """Muestra balance mensual en consola"""
        self.stdout.write(self.style.SUCCESS("=" * 80))
        self.stdout.write(self.style.SUCCESS(
            f"BALANCE MENSUAL - {balance['periodo']['mes_nombre']} {balance['periodo']['anio']}"
        ))
        self.stdout.write(self.style.SUCCESS("=" * 80))
        
        self.stdout.write(f"\n💰 INGRESOS:")
        self.stdout.write(f"  Total Bruto: ${balance['ingresos']['total_bruto']:,.0f}")
        self.stdout.write(f"  Total Neto:  ${balance['ingresos']['total_neto']:,.0f}")
        self.stdout.write(f"  Ventas:      {balance['ingresos']['num_ventas']}")
        
        self.stdout.write(f"\n📈 UTILIDADES:")
        self.stdout.write(self.style.SUCCESS(
            f"  Utilidad Neta: ${balance['utilidad_neta']:,.0f} "
            f"({balance['margen_neto_pct']:.1f}%)"
        ))

    def _mostrar_anual_texto(self, balance):
        """Muestra balance anual en consola"""
        self.stdout.write(self.style.SUCCESS("=" * 80))
        self.stdout.write(self.style.SUCCESS(f"BALANCE ANUAL {balance['anio']}"))
        self.stdout.write(self.style.SUCCESS("=" * 80))
        
        self.stdout.write(f"\n📊 TOTALES:")
        self.stdout.write(f"  Ingresos: ${balance['totales']['ingresos_bruto']:,.0f}")
        self.stdout.write(self.style.SUCCESS(
            f"  Utilidad: ${balance['totales']['utilidad_neta']:,.0f}"
        ))

    def _mostrar_comparativo_texto(self, comparativa):
        """Muestra comparativa en consola"""
        anios_str = ', '.join(str(a['anio']) for a in comparativa['anios'])
        self.stdout.write(self.style.SUCCESS("=" * 80))
        self.stdout.write(self.style.SUCCESS(f"COMPARATIVA: {anios_str}"))
        self.stdout.write(self.style.SUCCESS("=" * 80))
        
        for anio_data in comparativa['anios']:
            self.stdout.write(f"\n{anio_data['anio']}:")
            self.stdout.write(
                f"  Ingresos: ${anio_data['totales']['ingresos_bruto']:,.0f}"
            )
            self.stdout.write(
                f"  Utilidad: ${anio_data['totales']['utilidad_neta']:,.0f}"
            )

    def _exportar_json(self, data, archivo):
        """Exporta a JSON"""
        import json
        
        # Convertir Decimals a strings
        def decimal_to_str(obj):
            if isinstance(obj, Decimal):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: decimal_to_str(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_str(item) for item in obj]
            return obj
        
        data_convertida = decimal_to_str(data)
        
        if archivo:
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(data_convertida, f, indent=2, ensure_ascii=False)
            self.stdout.write(self.style.SUCCESS(f"✅ Exportado a: {archivo}"))
        else:
            self.stdout.write(json.dumps(data_convertida, indent=2, ensure_ascii=False))

    def _exportar_csv_mensual(self, balance, archivo):
        """Exporta balance mensual a CSV"""
        import csv
        
        nombre = archivo or f"balance_mensual_{balance['periodo']['anio']}_{balance['periodo']['mes']:02d}.csv"
        
        with open(nombre, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Concepto', 'Valor'])
            writer.writerow(['Periodo', f"{balance['periodo']['mes_nombre']} {balance['periodo']['anio']}"])
            writer.writerow([])
            writer.writerow(['INGRESOS'])
            writer.writerow(['Total Bruto', balance['ingresos']['total_bruto']])
            writer.writerow(['Total Neto', balance['ingresos']['total_neto']])
            writer.writerow(['Kilos Vendidos', balance['ingresos']['kilos_vendidos']])
            writer.writerow(['Número de Ventas', balance['ingresos']['num_ventas']])
            writer.writerow([])
            writer.writerow(['UTILIDADES'])
            writer.writerow(['Utilidad Bruta', balance['utilidad_bruta']])
            writer.writerow(['Utilidad Neta', balance['utilidad_neta']])
            writer.writerow(['Margen Neto %', balance['margen_neto_pct']])
        
        self.stdout.write(self.style.SUCCESS(f"✅ Exportado a: {nombre}"))

    def _exportar_csv_anual(self, balance, archivo):
        """Exporta balance anual a CSV"""
        import csv
        
        nombre = archivo or f"balance_anual_{balance['anio']}.csv"
        
        with open(nombre, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Mes', 'Ingresos Bruto', 'Ingresos Neto', 'CMV', 
                'Gastos', 'Utilidad Neta', 'Margen %', 'Ventas'
            ])
            
            for mes in balance['meses']:
                writer.writerow([
                    mes['periodo']['mes_nombre'],
                    mes['ingresos']['total_bruto'],
                    mes['ingresos']['total_neto'],
                    mes['costos']['cmv'],
                    mes['gastos']['total_neto'],
                    mes['utilidad_neta'],
                    mes['margen_neto_pct'],
                    mes['ingresos']['num_ventas'],
                ])
            
            writer.writerow([])
            writer.writerow([
                'TOTAL',
                balance['totales']['ingresos_bruto'],
                balance['totales']['ingresos_neto'],
                balance['totales']['cmv'],
                balance['totales']['gastos_neto'],
                balance['totales']['utilidad_neta'],
                balance['totales']['margen_neto_pct'],
                balance['totales']['num_ventas'],
            ])
        
        self.stdout.write(self.style.SUCCESS(f"✅ Exportado a: {nombre}"))

    def _exportar_csv_comparativo(self, comparativa, archivo):
        """Exporta comparativa a CSV"""
        import csv
        
        anios_str = '_'.join(str(a['anio']) for a in comparativa['anios'])
        nombre = archivo or f"comparativa_{anios_str}.csv"
        
        with open(nombre, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Encabezados
            headers = ['Concepto'] + [str(a['anio']) for a in comparativa['anios']]
            writer.writerow(headers)
            
            # Datos
            writer.writerow(['Ingresos Totales'] + 
                          [a['totales']['ingresos_bruto'] for a in comparativa['anios']])
            writer.writerow(['Utilidad Neta'] + 
                          [a['totales']['utilidad_neta'] for a in comparativa['anios']])
            writer.writerow(['Margen Neto %'] + 
                          [a['totales']['margen_neto_pct'] for a in comparativa['anios']])
        
        self.stdout.write(self.style.SUCCESS(f"✅ Exportado a: {nombre}"))


# Ejemplo de uso desde línea de comandos:
"""
# Balance del mes actual
python manage.py generar_balance

# Balance de diciembre 2025
python manage.py generar_balance --tipo mensual --mes 12 --anio 2025

# Balance anual 2025
python manage.py generar_balance --tipo anual --anio 2025

# Comparar 2024 vs 2025
python manage.py generar_balance --tipo comparativo --anios 2024,2025

# Exportar a JSON
python manage.py generar_balance --tipo anual --anio 2025 --formato json --archivo balance_2025.json

# Exportar a CSV
python manage.py generar_balance --tipo anual --anio 2025 --formato csv --archivo balance_2025.csv
"""
