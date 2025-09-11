from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    def __str__(self): return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagenURL = models.URLField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    def __str__(self): return self.nombre

class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')
    created = models.DateTimeField(auto_now_add=True)
    def total(self):
        return sum([item.subtotal() for item in self.items.all()])

class ItemCarrito(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    cantidad = models.PositiveIntegerField(default=1)
    def subtotal(self): return self.producto.precio * self.cantidad

class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    def calcular_total(self):
        total = sum([d.subtotal() for d in self.detalles.all()])
        self.total = total
        self.save()
        return total

class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField()
    precioUnitario = models.DecimalField(max_digits=10, decimal_places=2)
    def subtotal(self): return self.cantidad * self.precioUnitario
