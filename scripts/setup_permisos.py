"""
Script para configurar los roles y permisos del sistema.
Ejecutar con: python manage.py shell < scripts/setup_permisos.py
"""

from django.contrib.auth.models import Permission, Group, User, ContentType
from tienda.models import Venta, Producto, Categoria, Rol

def crear_permisos():
    """Crea permisos personalizados si no existen"""
    
    # Obtener content types
    venta_ct = ContentType.objects.get_for_model(Venta)
    producto_ct = ContentType.objects.get_for_model(Producto)
    categoria_ct = ContentType.objects.get_for_model(Categoria)
    
    # Crear permisos personalizados
    permisos = [
        ('view_sales_reports', 'Puede ver reportes de ventas', venta_ct),
        ('export_sales_reports', 'Puede exportar reportes en PDF', venta_ct),
        ('view_product_reports', 'Puede ver reportes de productos', producto_ct),
        ('view_categoria_reports', 'Puede ver reportes de categorías', categoria_ct),
    ]
    
    for codename, nombre, content_type in permisos:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=content_type,
            defaults={'name': nombre}
        )
        if created:
            print(f"✓ Permiso creado: {nombre}")
        else:
            print(f"✓ Permiso ya existe: {nombre}")

def crear_roles():
    """Crea los roles predefinidos del sistema"""
    
    # Rol: Administrador
    admin_perms = Permission.objects.filter(
        codename__in=[
            'add_venta', 'change_venta', 'delete_venta', 'view_venta',
            'view_sales_reports', 'export_sales_reports',
            'view_product_reports', 'view_categoria_reports',
        ]
    )
    
    admin_rol, created = Rol.objects.get_or_create(
        tipo='admin',
        defaults={'descripcion': 'Acceso total al sistema'}
    )
    admin_rol.permisos.set(admin_perms)
    print("✓ Rol Administrador configurado" if created else "✓ Rol Administrador ya existe")
    
    # Rol: Vendedor
    vendedor_perms = Permission.objects.filter(
        codename__in=['add_venta', 'view_venta', 'view_product_reports']
    )
    
    vendedor_rol, created = Rol.objects.get_or_create(
        tipo='vendedor',
        defaults={'descripcion': 'Puede registrar ventas y ver reportes básicos'}
    )
    vendedor_rol.permisos.set(vendedor_perms)
    print("✓ Rol Vendedor configurado" if created else "✓ Rol Vendedor ya existe")
    
    # Rol: Gerente de Reportes
    gerente_perms = Permission.objects.filter(
        codename__in=['view_sales_reports', 'export_sales_reports', 'view_product_reports', 'view_categoria_reports']
    )
    
    gerente_rol, created = Rol.objects.get_or_create(
        tipo='gerente',
        defaults={'descripcion': 'Acceso a todos los reportes con descarga en PDF'}
    )
    gerente_rol.permisos.set(gerente_perms)
    print("✓ Rol Gerente configurado" if created else "✓ Rol Gerente ya existe")

if __name__ == '__main__':
    print("Configurando permisos y roles del sistema...")
    crear_permisos()
    print("\nCreando roles...")
    crear_roles()
    print("\n✓ Configuración completada!")
