from django.urls import path
from . import views
from . import views_balance

app_name = "crm"

urlpatterns = [
    # Clientes
    path("clientes/", views.clientes_list, name="clientes_list"),
    path("clientes/nuevo/", views.crear_cliente, name="crear_cliente"),
    path("clientes/<int:cliente_id>/editar/", views.editar_cliente, name="editar_cliente"),
    path("clientes/<int:cliente_id>/borrar/", views.borrar_cliente, name="borrar_cliente"),

    # Ventas
    path("ventas/", views.ventas_list, name="ventas_list"),
    path("ventas/nueva/", views.venta_nueva, name="venta_nueva"),
    path("ventas/<int:venta_id>/editar/", views.venta_editar, name="venta_editar"),
    path("ventas/<int:venta_id>/borrar/", views.venta_borrar, name="venta_borrar"),

    # ✅ Detalle + Ítems
    path("ventas/<int:venta_id>/", views.venta_detalle, name="venta_detalle"),
    path("ventas/<int:venta_id>/items/agregar/", views.venta_item_agregar, name="venta_item_agregar"),
    path("ventas/items/<int:item_id>/borrar/", views.venta_item_borrar, name="venta_item_borrar"),

    # Buscadores
    path("buscar-telefono/", views.buscar_cliente_telefono, name="buscar_cliente_telefono"),
    

    # ✅ Resumen mensual
    path("resumen-mensual/", views.resumen_mensual, name="resumen_mensual"),
    
    path("dashboard/", views.dashboard, name="dashboard"),
    path("inventario/", views.inventario, name="inventario"),

    path("inventario/consumo-bolsas/", views.consumo_bolsas_view, name="consumo_bolsas"),
    
    # ✅ Balance Contable
    path("balance/mensual/", views_balance.balance_mensual, name="balance_mensual"),
    path("balance/anual/", views_balance.balance_anual, name="balance_anual"),
    path("balance/comparativo/", views_balance.balance_comparativo, name="balance_comparativo"),
    
    # API endpoints para balance
    path("api/balance/mensual/<int:anio>/<int:mes>/", views_balance.api_balance_mensual, name="api_balance_mensual"),
    path("api/balance/anual/<int:anio>/", views_balance.api_balance_anual, name="api_balance_anual"),
    path("api/balance/comparativo/", views_balance.api_balance_comparativo, name="api_balance_comparativo"),

]
