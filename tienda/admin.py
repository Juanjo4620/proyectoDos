from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from .models import Categoria, Producto, Venta, Rol

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'stock']
    list_filter = ['categoria', 'precio']
    search_fields = ['nombre']
    readonly_fields = ['id']

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'cantidad', 'fecha', 'vendedor', 'get_total']
    list_filter = ['fecha', 'producto__categoria', 'vendedor']
    search_fields = ['producto__nombre', 'vendedor__username']
    readonly_fields = ['fecha', 'id']
    date_hierarchy = 'fecha'
    
    def get_total(self, obj):
        return f"${obj.total():.2f}"
    get_total.short_description = 'Total'

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'descripcion']
    filter_horizontal = ['permisos']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(tipo__in=['vendedor', 'cliente'])
        return qs
