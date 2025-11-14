#!/usr/bin/env python
"""
Script interactivo para configurar el sistema inicial.
Ejecutar con: python manage.py shell < scripts/init_system.py
"""

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
        {'nombre': 'Electrónica', 'descripcion': 'Productos electrónicos y tecnología'},
        {'nombre': 'Ropa', 'descripcion': 'Prendas de vestir y accesorios'},
        {'nombre': 'Alimentos', 'descripcion': 'Productos alimenticios'},
        {'nombre': 'Hogar', 'descripcion': 'Productos para el hogar'},
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
        {'nombre': 'Laptop Dell', 'categoria': 'Electrónica', 'precio': 1200.00, 'stock': 15},
        {'nombre': 'Mouse Inalámbrico', 'categoria': 'Electrónica', 'precio': 35.00, 'stock': 50},
        {'nombre': 'Teclado Mecánico', 'categoria': 'Electrónica', 'precio': 150.00, 'stock': 25},
        {'nombre': 'Monitor 24"', 'categoria': 'Electrónica', 'precio': 250.00, 'stock': 10},
        
        {'nombre': 'Camiseta Básica', 'categoria': 'Ropa', 'precio': 25.00, 'stock': 100},
        {'nombre': 'Pantalón Jeans', 'categoria': 'Ropa', 'precio': 60.00, 'stock': 80},
        {'nombre': 'Zapatos Deportivos', 'categoria': 'Ropa', 'precio': 85.00, 'stock': 40},
        {'nombre': 'Chaqueta de Cuero', 'categoria': 'Ropa', 'precio': 180.00, 'stock': 20},
        
        {'nombre': 'Arroz (1kg)', 'categoria': 'Alimentos', 'precio': 5.00, 'stock': 200},
        {'nombre': 'Aceite de Oliva (500ml)', 'categoria': 'Alimentos', 'precio': 8.50, 'stock': 150},
        {'nombre': 'Café Premium (250g)', 'categoria': 'Alimentos', 'precio': 12.00, 'stock': 100},
        
        {'nombre': 'Almohada de Memoria', 'categoria': 'Hogar', 'precio': 45.00, 'stock': 60},
        {'nombre': 'Juego de Sábanas', 'categoria': 'Hogar', 'precio': 80.00, 'stock': 40},
        {'nombre': 'Lámpara LED', 'categoria': 'Hogar', 'precio': 35.00, 'stock': 75},
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
    productos = Producto.objects.all()[:5]
    
    from datetime import datetime, timedelta
    
    for i, prod in enumerate(productos):
        venta = Venta.objects.create(
            producto=prod,
            cantidad=i + 1,
            vendedor=admin,
            fecha=datetime.now().date() - timedelta(days=i)
        )
        print(f"✓ Venta creada: {prod.nombre} (${venta.total():.2f})")

def main():
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

if __name__ == '__main__':
    main()
