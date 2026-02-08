# Módulo de Balance Contable

Sistema completo de contabilidad y análisis financiero para tu aplicación Django de distribución.

## 🎯 Características

### Balance Mensual
- Estado de resultados completo (ingresos, costos, gastos, utilidades)
- Análisis de márgenes (bruto, operacional, neto)
- Distribución de ventas por canal
- KPIs principales del mes
- Cálculo automático de IVA
- Exportación a JSON

### Balance Anual
- Comparativa mes a mes durante todo el año
- Totales y promedios anuales
- Gráficos interactivos de evolución
- Análisis de tendencias
- Exportación completa de datos

### Balance Comparativo
- Comparación entre múltiples años (hasta 5)
- Cálculo de tasas de crecimiento
- Análisis de variaciones año a año
- Visualización gráfica de comparativas

## 📦 Archivos Agregados

```
crm/
├── services_balance.py          # Lógica de cálculo de balances
├── views_balance.py             # Vistas web y API endpoints
├── urls.py                      # Rutas actualizadas
└── templates/crm/
    ├── balance_mensual.html     # Template balance mensual
    ├── balance_anual.html       # Template balance anual
    └── balance_comparativo.html # Template comparativo
```

## 🚀 Instalación

### 1. Los archivos ya están en tu repositorio
Todos los archivos necesarios han sido creados en las ubicaciones correctas.

### 2. No requiere dependencias adicionales
El módulo usa las bibliotecas que ya tienes instaladas:
- Django
- python-dateutil (para cálculos de fechas)

### 3. Las URLs ya están configuradas
El archivo `crm/urls.py` ya incluye todas las rutas necesarias.

## 📖 Uso

### Acceder a los Balances

**Balance Mensual:**
```
http://tu-dominio/crm/balance/mensual/
http://tu-dominio/crm/balance/mensual/?mes=12&anio=2025
```

**Balance Anual:**
```
http://tu-dominio/crm/balance/anual/
http://tu-dominio/crm/balance/anual/?anio=2025
```

**Balance Comparativo:**
```
http://tu-dominio/crm/balance/comparativo/
http://tu-dominio/crm/balance/comparativo/?anios=2024,2025,2026
```

### API Endpoints (JSON)

**Balance Mensual:**
```
GET /crm/api/balance/mensual/<anio>/<mes>/
Ejemplo: /crm/api/balance/mensual/2025/12/
```

**Balance Anual:**
```
GET /crm/api/balance/anual/<anio>/
Ejemplo: /crm/api/balance/anual/2025/
```

**Balance Comparativo:**
```
GET /crm/api/balance/comparativo/?anios=2024,2025
```

### Usar en código Python

```python
from crm.services_balance import (
    calcular_balance_mensual,
    calcular_balance_anual,
    calcular_comparativa_anual
)

# Balance de diciembre 2025
balance = calcular_balance_mensual(2025, 12)
print(f"Utilidad neta: ${balance['utilidad_neta']}")
print(f"Margen neto: {balance['margen_neto_pct']}%")

# Balance de todo 2025
balance_anual = calcular_balance_anual(2025)
print(f"Total ingresos: ${balance_anual['totales']['ingresos_bruto']}")

# Comparar 2024 vs 2025
comparativa = calcular_comparativa_anual([2024, 2025])
```

## 💡 Estructura de Datos

### Balance Mensual
```python
{
    'periodo': {
        'anio': 2025,
        'mes': 12,
        'mes_nombre': 'Diciembre'
    },
    'ingresos': {
        'total_bruto': Decimal('1500000.00'),  # Con IVA
        'total_neto': Decimal('1260504.20'),   # Sin IVA
        'iva': Decimal('239495.80'),
        'kilos_vendidos': Decimal('1250.00'),
        'num_ventas': 45,
        'ticket_promedio': Decimal('33333.33'),
        'por_canal': {
            'Instagram': Decimal('500000.00'),
            'WhatsApp': Decimal('700000.00'),
            'Web': Decimal('300000.00')
        }
    },
    'costos': {
        'cmv': Decimal('625000.00'),           # Costo Mercadería Vendida
        'costo_promedio_kg': Decimal('500.00'),
        'kilos_vendidos': Decimal('1250.00')
    },
    'gastos': {
        'total_neto': Decimal('200000.00'),    # Sin IVA
        'total_iva': Decimal('38000.00'),
        'total': Decimal('238000.00'),         # Con IVA
        'por_tipo': {
            'Arriendo': {'neto': 100000, 'iva': 19000, 'total': 119000, 'cantidad': 1},
            'Bencina': {'neto': 50000, 'iva': 9500, 'total': 59500, 'cantidad': 3},
            ...
        }
    },
    'utilidad_bruta': Decimal('635504.20'),    # Ingresos neto - CMV
    'utilidad_operacional': Decimal('435504.20'), # Utilidad bruta - Gastos neto
    'utilidad_neta': Decimal('397504.20'),     # Utilidad operacional - IVA gastos
    'margen_bruto_pct': Decimal('50.40'),
    'margen_operacional_pct': Decimal('34.54'),
    'margen_neto_pct': Decimal('31.53')
}
```

## 📊 Cálculos Explicados

### Ingresos
- **Total Bruto**: Suma de todas las ventas (con IVA)
- **Total Neto**: Total bruto / 1.19 (sin IVA)
- **IVA**: Total bruto - Total neto

### Costo de Mercadería Vendida (CMV)
- Se calcula el **costo promedio ponderado** de todas las importaciones activas
- CMV = Kilos vendidos × Costo promedio por kg

### Gastos Operacionales
- Incluye todos los gastos registrados en el período
- Se calcula IVA solo para gastos que lo aplican
- Clasificados por tipo (arriendo, bencina, servicios, etc.)

### Utilidades
1. **Utilidad Bruta** = Ingresos neto - CMV
2. **Utilidad Operacional** = Utilidad bruta - Gastos neto
3. **Utilidad Neta** = Utilidad operacional - IVA gastos

### Márgenes
- **Margen Bruto %** = (Utilidad bruta / Ingresos neto) × 100
- **Margen Operacional %** = (Utilidad operacional / Ingresos neto) × 100
- **Margen Neto %** = (Utilidad neta / Ingresos neto) × 100

## 🎨 Características de la Interfaz

### Balance Mensual
- Selector de mes y año
- 4 KPIs principales en tarjetas
- Estado de resultados detallado
- Distribución de ventas por canal
- Análisis visual de márgenes
- Botones de impresión y exportación

### Balance Anual
- Resumen anual con totales y promedios
- Tabla mes a mes con todos los indicadores
- Gráfico de evolución de ingresos y utilidad
- Gráfico de márgenes mensuales
- Enlaces rápidos a cada mes

### Balance Comparativo
- Selector de múltiples años (hasta 5)
- Tabla comparativa completa
- Cálculo automático de variaciones
- Gráfico combinado (barras + línea)
- Indicadores de crecimiento

## 🔧 Personalización

### Agregar nuevos tipos de gastos
Edita `crm/models.py` en la clase `GastoOperacional.Tipo`:

```python
class Tipo(models.TextChoices):
    ARRIENDO = "arriendo", "Arriendo"
    BENCINA = "bencina", "Bencina"
    # ... tipos existentes ...
    TU_NUEVO_TIPO = "tu_codigo", "Tu Descripción"
```

### Modificar cálculo de costos
Edita `crm/services_balance.py` en la función `calcular_balance_mensual()`:

```python
# Línea ~53: Modificar lógica de costo promedio
# Puedes cambiar cómo se calcula el costo promedio ponderado
```

### Agregar nuevos KPIs
1. Calcula el KPI en `services_balance.py`
2. Agrégalo al diccionario de retorno
3. Muéstralo en el template correspondiente

## 📱 Integración con Dashboard

Para agregar enlaces en tu dashboard existente, edita `crm/templates/crm/dashboard.html`:

```html
<div class="col-md-4">
    <div class="card">
        <div class="card-body">
            <h5>📊 Balance Contable</h5>
            <a href="{% url 'crm:balance_mensual' %}" class="btn btn-primary btn-block">
                Balance Mensual
            </a>
            <a href="{% url 'crm:balance_anual' %}" class="btn btn-info btn-block mt-2">
                Balance Anual
            </a>
            <a href="{% url 'crm:balance_comparativo' %}" class="btn btn-success btn-block mt-2">
                Comparar Años
            </a>
        </div>
    </div>
</div>
```

## 🐛 Troubleshooting

### Error: "No module named 'dateutil'"
```bash
pip install python-dateutil
```

### Los gráficos no se muestran
Verifica que Chart.js se está cargando correctamente. Los templates incluyen el CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

### Decimals en JSON
Los endpoints API convierten Decimals a strings automáticamente para compatibilidad JSON.

### Fechas incorrectas
El sistema usa `timezone.now()` de Django. Asegúrate de tener configurada la zona horaria correcta en `settings.py`:
```python
TIME_ZONE = 'America/Santiago'  # Para Chile
USE_TZ = True
```

## 📝 Próximas Mejoras Sugeridas

1. **Exportación a Excel**: Agregar botón para descargar balances en formato .xlsx
2. **Gráficos adicionales**: Tortas, áreas apiladas, etc.
3. **Proyecciones**: Calcular proyecciones basadas en tendencias
4. **Alertas**: Notificaciones cuando márgenes bajen de umbrales
5. **Presupuestos**: Comparar resultados vs presupuesto planificado
6. **Cash Flow**: Agregar análisis de flujo de caja
7. **Indicadores financieros**: ROI, ROE, punto de equilibrio, etc.

## 👥 Soporte

Para preguntas o sugerencias, contacta al equipo de desarrollo o abre un issue en el repositorio.

---

**Versión**: 1.0  
**Fecha**: Febrero 2026  
**Desarrollado para**: Sistema de Distribución Django
