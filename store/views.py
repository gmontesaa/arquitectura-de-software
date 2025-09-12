from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto, Carrito, ItemCarrito, Orden, DetalleOrden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.contrib import messages

def product_list(request):
    productos = Producto.objects.all()
    return render(request, 'store/product_list.html', {'productos': productos})

def product_detail(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'store/product_detail.html', {'producto': producto})

def get_or_create_cart(user):
    cart, created = Carrito.objects.get_or_create(usuario=user)
    return cart

@login_required
def add_to_cart(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    cart = get_or_create_cart(request.user)
    item, created = ItemCarrito.objects.get_or_create(
        carrito=cart,
        producto=producto,
        defaults={'cantidad': 1}
    )
    if not created:
        item.cantidad += 1
        item.save()
        messages.success(request, f'Se agregó otra unidad de {producto.nombre} al carrito')
    else:
        messages.success(request, f'{producto.nombre} se agregó al carrito')
    
    # Redirigir al catálogo con un mensaje de confirmación
    return redirect('product_list')

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

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'¡Cuenta creada exitosamente para {username}!')
            # Iniciar sesión automáticamente después del registro
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido de vuelta, {username}!')
            return redirect('product_list')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'store/login.html')

def user_logout(request):
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('product_list')