from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categorías"
        permissions = [
            ("view_categoria_reports", "Puede ver reportes de categorías"),
        ]
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    
    class Meta:
        permissions = [
            ("view_product_reports", "Puede ver reportes de productos"),
        ]
    
    def __str__(self):
        return self.nombre

class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateField(auto_now_add=True)
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        permissions = [
            ("view_sales_reports", "Puede ver reportes de ventas"),
            ("export_sales_reports", "Puede descargar reportes en PDF"),
        ]
        ordering = ['-fecha']
    
    def total(self):
        return self.cantidad * self.producto.precio
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.fecha}"

class Rol(models.Model):
    """
    Modelo para gestionar roles de usuario con permisos específicos
    """
    OPCIONES_TIPO = [
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
        ('gerente', 'Gerente de Reportes'),
        ('cliente', 'Cliente'),
    ]
    
    tipo = models.CharField(max_length=20, choices=OPCIONES_TIPO, unique=True)
    descripcion = models.TextField()
    permisos = models.ManyToManyField(Permission, blank=True)
    
    def __str__(self):
        return self.get_tipo_display()
    
    class Meta:
        verbose_name_plural = "Roles"

class CarritoItem(models.Model):
    """
    Modelo para gestionar items en el carrito de compras de un usuario
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carrito_items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('usuario', 'producto')
        ordering = ['-fecha_agregado']
    
    def subtotal(self):
        return self.cantidad * self.producto.precio
    
    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre} x{self.cantidad}"
