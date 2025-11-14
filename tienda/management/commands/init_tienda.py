from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from tienda.models import Categoria, Producto, Venta
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Inicializa el sistema con usuarios, categorías, productos y ventas de prueba'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Configuración Inicial del Sistema de Tienda'))
        self.stdout.write(self.style.SUCCESS('='*60))

        # Crear usuarios
        self.stdout.write(self.style.WARNING('\n[1/5] Creando usuarios...'))
        self.crear_usuarios()

        # Crear categorías
        self.stdout.write(self.style.WARNING('\n[2/5] Creando categorías...'))
        self.crear_categorias()

        # Crear productos
        self.stdout.write(self.style.WARNING('\n[3/5] Creando productos...'))
        self.crear_productos()

        # Crear ventas
        self.stdout.write(self.style.WARNING('\n[4/5] Creando ventas de prueba...'))
        self.crear_ventas()

        # Mostrar resumen
        self.stdout.write(self.style.SUCCESS('\n[5/5] ¡Configuración completada!'))
        self.mostrar_resumen()

    def crear_usuarios(self):
        usuarios = [
            {'username': 'admin', 'email': 'admin@tienda.local', 'password': 'admin123', 'is_superuser': True},
            {'username': 'vendedor', 'email': 'vendedor@tienda.local', 'password': 'vendedor123', 'is_superuser': False},
            {'username': 'gerente', 'email': 'gerente@tienda.local', 'password': 'gerente123', 'is_superuser': False},
        ]

        for user_data in usuarios:
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(f"✓ El usuario {user_data['username']} ya existe")
                continue

            if user_data['is_superuser']:
                User.objects.create_superuser(
                    user_data['username'],
                    user_data['email'],
                    user_data['password']
                )
            else:
                user = User.objects.create_user(
                    user_data['username'],
                    user_data['email'],
                    user_data['password']
                )
                if user_data['username'] == 'gerente':
                    user.is_staff = True
                    user.save()

            self.stdout.write(f"✓ Usuario creado: {user_data['username']}")

    def crear_categorias(self):
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
                self.stdout.write(f"✓ Categoría creada: {cat.nombre}")

    def crear_productos(self):
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
                self.stdout.write(f"✓ Producto creado: {prod.nombre} (${prod.precio})")

    def crear_ventas(self):
        if Venta.objects.exists():
            self.stdout.write("✓ Ya existen ventas registradas")
            return

        admin = User.objects.get(username='admin')
        productos = list(Producto.objects.all())[:5]

        for i, prod in enumerate(productos):
            venta = Venta.objects.create(
                producto=prod,
                cantidad=i + 1,
                vendedor=admin,
                fecha=datetime.now().date() - timedelta(days=i)
            )
            self.stdout.write(f"✓ Venta creada: {prod.nombre} (${venta.total():.2f})")

    def mostrar_resumen(self):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('USUARIOS DE PRUEBA CREADOS'))
        self.stdout.write(self.style.SUCCESS('='*60))

        self.stdout.write('\n1. ADMINISTRADOR')
        self.stdout.write('   Usuario: admin')
        self.stdout.write('   Contraseña: admin123')
        self.stdout.write('   Acceso: Completo al sistema')

        self.stdout.write('\n2. VENDEDOR')
        self.stdout.write('   Usuario: vendedor')
        self.stdout.write('   Contraseña: vendedor123')
        self.stdout.write('   Acceso: Registrar y ver ventas')

        self.stdout.write('\n3. GERENTE DE REPORTES')
        self.stdout.write('   Usuario: gerente')
        self.stdout.write('   Contraseña: gerente123')
        self.stdout.write('   Acceso: Ver y descargar reportes')

        self.stdout.write('\n' + '='*60)
        self.stdout.write('Accede a http://localhost:8000/login/')
        self.stdout.write('='*60 + '\n')
