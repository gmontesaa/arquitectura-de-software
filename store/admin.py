from django.contrib import admin
from .models import Producto, Carrito, ItemCarrito, Orden, DetalleOrden

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stock', 'fecha_creacion']
    list_filter = ['fecha_creacion']
    search_fields = ['nombre', 'descripcion']

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha_creacion']
    list_filter = ['fecha_creacion']

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'cantidad', 'carrito', 'fecha_agregado']
    list_filter = ['fecha_agregado']

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'total', 'estado', 'fecha_creacion']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['usuario__username']

@admin.register(DetalleOrden)
class DetalleOrdenAdmin(admin.ModelAdmin):
    list_display = ['orden', 'producto', 'cantidad', 'precioUnitario']
    list_filter = ['orden__fecha_creacion']