import os
import django
from django.contrib.auth.models import User, Permission, ContentType
from tienda.models import Categoria, Producto, Venta, Rol

def crear_usuario_admin():
    """Crea un usuario administrador si no existe"""
    if User.objects.filter(username='admin').exists():
        print("✓ El usuario admin ya existe")
        return
    
    admin = User.objects.create_superuser('admin', 'admin@tienda.local', 'admin123')
    print("✓ Usuario admin creado")
    print("   Usuario: admin")
    print("   Contraseña: admin123")

def crear_usuario_vendedor():
    """Crea un usuario vendedor de prueba"""
    if User.objects.filter(username='vendedor').exists():
        print("✓ El usuario vendedor ya existe")
        return
    
    user = User.objects.create_user(
        username='vendedor',
        email='vendedor@tienda.local',
        password='vendedor123'
    )
    
    # Asignar permisos de vendedor
    permisos_vendedor = Permission.objects.filter(
        codename__in=['add_venta', 'view_venta', 'view_product_reports']
    )
    user.user_permissions.set(permisos_vendedor)
    
    print("✓ Usuario vendedor creado")
    print("   Usuario: vendedor")
    print("   Contraseña: vendedor123")

def crear_usuario_gerente():
    """Crea un usuario gerente de reportes"""
    if User.objects.filter(username='gerente').exists():
        print("✓ El usuario gerente ya existe")
        return
    
    user = User.objects.create_user(
        username='gerente',
        email='gerente@tienda.local',
        password='gerente123'
    )
    user.is_staff = True
    user.save()
    
    # Asignar permisos de reportes
    permisos_reportes = Permission.objects.filter(
        codename__in=['view_sales_reports', 'export_sales_reports', 'view_product_reports', 'view_categoria_reports']
    )
    user.user_permissions.set(permisos_reportes)
    
    print("✓ Usuario gerente creado")
    print("   Usuario: gerente")
    print("   Contraseña: gerente123")

def crear_categorias():
    """Crea categorías de prueba"""
    categorias = [
        {'nombre': 'Smartphones', 'descripcion': 'Teléfonos móviles y accesorios'},
        {'nombre': 'Computadoras', 'descripcion': 'Laptops, desktops y componentes'},
        {'nombre': 'Audio', 'descripcion': 'Auriculares, altavoces y sonido'},
        {'nombre': 'TV & Video', 'descripcion': 'Televisores y equipos multimedia'},
        {'nombre': 'Accesorios', 'descripcion': 'Cables, cargadores y periféricos'},
    ]
    
    for cat_data in categorias:
        cat, created = Categoria.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={'descripcion': cat_data['descripcion']}
        )
        if created:
            print(f"✓ Categoría creada: {cat.nombre}")
        else:
            print(f"✓ Categoría ya existe: {cat.nombre}")

def crear_productos():
    """Crea productos de prueba"""
    productos = [
        {'nombre': 'iPhone 14', 'categoria': 'Smartphones', 'precio': 899.00, 'stock': 20},
        {'nombre': 'Samsung Galaxy S23', 'categoria': 'Smartphones', 'precio': 799.00, 'stock': 25},
        {'nombre': 'MacBook Pro 14"', 'categoria': 'Computadoras', 'precio': 1999.00, 'stock': 8},
        {'nombre': 'Dell XPS 13', 'categoria': 'Computadoras', 'precio': 1299.00, 'stock': 10},
        {'nombre': 'Sony WH-1000XM5', 'categoria': 'Audio', 'precio': 399.00, 'stock': 30},
        {'nombre': 'Bose QuietComfort 45', 'categoria': 'Audio', 'precio': 329.00, 'stock': 20},
        {'nombre': 'Samsung QLED 55"', 'categoria': 'TV & Video', 'precio': 999.00, 'stock': 5},
        {'nombre': 'LG OLED 48"', 'categoria': 'TV & Video', 'precio': 1199.00, 'stock': 4},
        {'nombre': 'Logitech MX Master 3', 'categoria': 'Accesorios', 'precio': 99.00, 'stock': 40},
        {'nombre': 'Apple AirPods Pro', 'categoria': 'Audio', 'precio': 249.00, 'stock': 35},
        {'nombre': 'SSD Samsung 1TB', 'categoria': 'Computadoras', 'precio': 129.00, 'stock': 50},
        {'nombre': 'Monitor 27" 144Hz', 'categoria': 'Computadoras', 'precio': 329.00, 'stock': 12},
        {'nombre': 'Apple Watch Series 8', 'categoria': 'Accesorios', 'precio': 399.00, 'stock': 18},
        {'nombre': 'Cargador USB-C 65W', 'categoria': 'Accesorios', 'precio': 29.00, 'stock': 100},
    ]
    
    for prod_data in productos:
        categoria = Categoria.objects.get(nombre=prod_data['categoria'])
        prod, created = Producto.objects.get_or_create(
            nombre=prod_data['nombre'],
            defaults={
                'categoria': categoria,
                'precio': prod_data['precio'],
                'stock': prod_data['stock']
            }
        )
        if created:
            print(f"✓ Producto creado: {prod.nombre} (${prod.precio})")

def crear_ventas_prueba():
    """Crea ventas de prueba"""
    if Venta.objects.exists():
        print("✓ Ya existen ventas registradas")
        return
    
    admin = User.objects.get(username='admin')
    productos = list(Producto.objects.all())[:5]
    
    from datetime import datetime, timedelta
    
    for i, prod in enumerate(productos):
        venta = Venta.objects.create(
            producto=prod,
            cantidad=i + 1,
            vendedor=admin,
            fecha=datetime.now().date() - timedelta(days=i)
        )
        print(f"✓ Venta creada: {prod.nombre} (${venta.total():.2f})")

print("=" * 60)
print("Configuración Inicial del Sistema de Tienda")
print("=" * 60)

print("\n[1/5] Creando usuarios...")
crear_usuario_admin()
crear_usuario_vendedor()
crear_usuario_gerente()

print("\n[2/5] Creando categorías...")
crear_categorias()

print("\n[3/5] Creando productos...")
crear_productos()

print("\n[4/5] Creando ventas de prueba...")
crear_ventas_prueba()

print("\n[5/5] Configuración completada!")
print("\n" + "=" * 60)
print("USUARIOS DE PRUEBA CREADOS")
print("=" * 60)
print("\n1. ADMINISTRADOR")
print("   Usuario: admin")
print("   Contraseña: admin123")
print("   Acceso: Completo al sistema")

print("\n2. VENDEDOR")
print("   Usuario: vendedor")
print("   Contraseña: vendedor123")
print("   Acceso: Registrar y ver ventas")

print("\n3. GERENTE DE REPORTES")
print("   Usuario: gerente")
print("   Contraseña: gerente123")
print("   Acceso: Ver y descargar reportes")

print("\n" + "=" * 60)
print("Accede a http://localhost:8000/login/")
print("=" * 60 + "\n")
