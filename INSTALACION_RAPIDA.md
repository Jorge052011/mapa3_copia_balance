# 🚀 Guía de Instalación - Módulo de Balance Contable

## ⚡ Instalación Rápida

### Paso 1: Los archivos ya están listos
Todos los archivos necesarios han sido creados en tu repositorio:

```
crm/
├── services_balance.py          ✅ Lógica de cálculo
├── views_balance.py             ✅ Vistas y API
├── urls.py                      ✅ Rutas actualizadas
├── test_balance.py              ✅ Script de prueba
├── generar_balance_command.py   ✅ Comando Django
└── templates/crm/
    ├── balance_mensual.html     ✅ Template mensual
    ├── balance_anual.html       ✅ Template anual
    └── balance_comparativo.html ✅ Template comparativo

BALANCE_README.md                ✅ Documentación completa
```

### Paso 2: Verificar que todo funcione

```bash
# 1. Ir al directorio del proyecto
cd mapa3_copia-main

# 2. Activar tu entorno virtual (si usas uno)
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# 3. Verificar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones (por si acaso)
python manage.py migrate

# 5. Probar las vistas (opcional)
python manage.py shell
>>> from crm.services_balance import calcular_balance_mensual
>>> balance = calcular_balance_mensual(2026, 2)
>>> print(balance['utilidad_neta'])
>>> exit()
```

### Paso 3: Configurar el comando de gestión (opcional)

Si quieres usar el comando `python manage.py generar_balance`:

```bash
# Crear el directorio de comandos
mkdir -p crm/management/commands

# Crear __init__.py vacíos
touch crm/management/__init__.py
touch crm/management/commands/__init__.py

# Mover el comando
mv crm/generar_balance_command.py crm/management/commands/generar_balance.py

# Probar el comando
python manage.py generar_balance --tipo mensual
```

### Paso 4: Acceder al sistema

```bash
# Iniciar el servidor
python manage.py runserver

# Abrir en el navegador:
# http://localhost:8000/crm/balance/mensual/
# http://localhost:8000/crm/balance/anual/
# http://localhost:8000/crm/balance/comparativo/
```

## 🎯 URLs Disponibles

### Vistas Web (Interfaz HTML)
- **Balance Mensual**: `/crm/balance/mensual/`
- **Balance Anual**: `/crm/balance/anual/`
- **Balance Comparativo**: `/crm/balance/comparativo/`

### API Endpoints (JSON)
- **Balance Mensual**: `/crm/api/balance/mensual/<anio>/<mes>/`
- **Balance Anual**: `/crm/api/balance/anual/<anio>/`
- **Balance Comparativo**: `/crm/api/balance/comparativo/?anios=2024,2025`

## 📝 Primeros Pasos

### 1. Ver balance del mes actual
```
http://localhost:8000/crm/balance/mensual/
```

### 2. Ver balance de un mes específico
```
http://localhost:8000/crm/balance/mensual/?mes=12&anio=2025
```

### 3. Ver balance anual
```
http://localhost:8000/crm/balance/anual/?anio=2025
```

### 4. Comparar años
```
http://localhost:8000/crm/balance/comparativo/?anios=2024,2025
```

## 🧪 Probar con datos de ejemplo

### Opción 1: Desde el shell de Django
```bash
python manage.py shell

# Ejecutar el script de prueba
>>> exec(open('crm/test_balance.py').read())
>>> generar_reporte_mensual(2026, 2)
>>> generar_reporte_anual(2026)
```

### Opción 2: Usando el comando de gestión (si lo instalaste)
```bash
# Reporte mensual actual
python manage.py generar_balance

# Reporte anual
python manage.py generar_balance --tipo anual --anio 2025

# Comparativa
python manage.py generar_balance --tipo comparativo --anios 2024,2025

# Exportar a CSV
python manage.py generar_balance --tipo anual --anio 2025 --formato csv
```

### Opción 3: Usando curl (API)
```bash
# Balance mensual
curl http://localhost:8000/crm/api/balance/mensual/2026/2/

# Balance anual
curl http://localhost:8000/crm/api/balance/anual/2025/

# Comparativa
curl "http://localhost:8000/crm/api/balance/comparativo/?anios=2024,2025"
```

## 🔗 Integrar en el Dashboard

Edita `crm/templates/crm/dashboard.html` y agrega:

```html
<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0">📊 Balance Contable</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4">
                        <a href="{% url 'crm:balance_mensual' %}" class="btn btn-primary btn-block btn-lg">
                            📅 Balance Mensual
                        </a>
                    </div>
                    <div class="col-md-4">
                        <a href="{% url 'crm:balance_anual' %}" class="btn btn-info btn-block btn-lg">
                            📊 Balance Anual
                        </a>
                    </div>
                    <div class="col-md-4">
                        <a href="{% url 'crm:balance_comparativo' %}" class="btn btn-success btn-block btn-lg">
                            📈 Comparar Años
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

## ✅ Checklist de Verificación

- [ ] Archivos creados en las ubicaciones correctas
- [ ] `crm/urls.py` incluye las nuevas rutas
- [ ] Servidor Django funcionando
- [ ] Puedes acceder a `/crm/balance/mensual/`
- [ ] Los cálculos se ejecutan sin errores
- [ ] Los templates se renderizan correctamente
- [ ] Los gráficos (Chart.js) se muestran
- [ ] La API JSON responde correctamente

## 🐛 Solución de Problemas

### Error: "No module named 'dateutil'"
```bash
pip install python-dateutil
```

### Error: "TemplateDoesNotExist"
Verifica que los archivos estén en:
```
crm/templates/crm/balance_mensual.html
crm/templates/crm/balance_anual.html
crm/templates/crm/balance_comparativo.html
```

### Error: "No reverse match for 'crm:balance_mensual'"
Verifica que `crm/urls.py` incluya:
```python
from . import views_balance
```
Y las rutas correspondientes.

### Los gráficos no se muestran
Verifica tu conexión a internet para cargar Chart.js desde CDN.

### Error 500 al acceder
Revisa los logs:
```bash
python manage.py runserver
# Mira la consola para ver el error específico
```

## 📚 Documentación Completa

Lee `BALANCE_README.md` para:
- Explicación detallada de cálculos
- Estructura de datos
- Personalización
- API completa
- Ejemplos avanzados

## 🎉 ¡Listo!

Tu sistema de balance contable está instalado y listo para usar. Ahora puedes:

1. ✅ Ver balances mensuales con detalle completo
2. ✅ Analizar el rendimiento anual mes a mes
3. ✅ Comparar años y ver tasas de crecimiento
4. ✅ Exportar datos en JSON
5. ✅ Imprimir reportes
6. ✅ Usar la API para integraciones

---

**¿Necesitas ayuda?** Consulta `BALANCE_README.md` o revisa el código en:
- `crm/services_balance.py` - Lógica de cálculo
- `crm/views_balance.py` - Vistas y API
- `crm/test_balance.py` - Ejemplos de uso
