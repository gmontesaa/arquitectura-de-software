from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto, Carrito, ItemCarrito, Orden, DetalleOrden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction

def product_list(request):
    productos = Producto.objects.all()
    return render(request, 'store/product_list.html', {'productos': productos})

def product_detail(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'store/product_detail.html', {'producto': producto})

@login_required
def get_or_create_cart(user):
    cart, created = Carrito.objects.get_or_create(usuario=user)
    return cart

@login_required
def add_to_cart(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    cart = get_or_create_cart(request.user)
    item, created = ItemCarrito.objects.get_or_create(carrito=cart, producto=producto)
    item.cantidad += 1
    item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart = get_or_create_cart(request.user)
    return render(request, 'store/cart.html', {'cart': cart})

@login_required
@transaction.atomic
def create_order(request):
    cart = get_or_create_cart(request.user)
    if cart.items.count() == 0:
        return redirect('product_list')
    orden = Orden.objects.create(usuario=request.user, total=0)
    for item in cart.items.all():
        DetalleOrden.objects.create(
            orden=orden,
            producto=item.producto,
            cantidad=item.cantidad,
            precioUnitario=item.producto.precio
        )
    orden.calcular_total()
    # limpiar carrito
    cart.items.all().delete()
    return render(request, 'store/order_confirm.html', {'orden': orden})
