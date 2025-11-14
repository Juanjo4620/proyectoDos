from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    path('', views.home, name='home'),
    path('ventas/', views.ventas, name='ventas'),
    path('signup/', views.signup, name='signup'),
    path('productos/', views.catalogo, name='productos'),
    
    # Carrito de compras
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_carrito, name='eliminar_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/procesar/', views.procesar_compra, name='procesar_compra'),
    path('compra-exitosa/', views.compra_exitosa, name='compra_exitosa'),
    
    # Reportes
    path('reportes/ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('reportes/categorias/', views.reporte_por_categoria, name='reporte_categorias'),
    path('reportes/productos/', views.reporte_por_producto, name='reporte_productos'),
]
