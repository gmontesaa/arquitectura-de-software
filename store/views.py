from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto, Carrito, ItemCarrito, Orden, DetalleOrden, Categoria
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.utils.translation import gettext as _
import requests
from .product_loader import ApiProductLoader, HardcodedProductLoader

def product_list(request):
    q = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria')
    sort = request.GET.get('sort', 'recent')
    productos = Producto.objects.all()
    if q:
        productos = productos.filter(nombre__icontains=q)
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    sort_map = {
        'recent': '-fecha_creacion',
        'price_asc': 'precio',
        'price_desc': '-precio',
        'name_asc': 'nombre',
        'name_desc': '-nombre',
    }
    productos = productos.order_by(sort_map.get(sort, '-fecha_creacion'))
    paginator = Paginator(productos, 12)
    page = request.GET.get('page')
    try:
        productos_page = paginator.page(page)
    except PageNotAnInteger:
        productos_page = paginator.page(1)
    except EmptyPage:
        productos_page = paginator.page(paginator.num_pages)
    categorias = Categoria.objects.all().order_by('nombre')
    clima = get_medellin_weather()
    contexto = {
        'productos': productos_page,
        'q': q,
        'categorias': categorias,
        'categoria_seleccionada': int(categoria_id) if categoria_id else None,
        'sort': sort,
        'page_obj': productos_page,
        'clima': clima,
    }
    return render(request, 'store/product_list.html', contexto)

def product_detail(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    relacionados = Producto.objects.none()
    clima = get_medellin_weather()
    if producto.categoria_id:
        relacionados = (Producto.objects
                         .filter(categoria_id=producto.categoria_id)
                         .exclude(pk=producto.pk)
                         .order_by('-fecha_creacion')[:4])
    contexto = {
        'producto': producto,
        'relacionados': relacionados,
        'clima': clima,
    }
    return render(request, 'store/product_detail.html', contexto)

def get_or_create_cart(user):
    cart, created = Carrito.objects.get_or_create(usuario=user)
    return cart

def pago_ficticio(request):
    if request.method == "POST":
        # Simula el pago exitoso
        return render(request, "store/pago.html", {"exito": True})
    return render(request, "store/pago.html", {"exito": False})

@login_required
def add_to_cart(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    cart = get_or_create_cart(request.user)
    # cantidad solicitada (por defecto 1)
    try:
        cantidad_solicitada = int(request.POST.get('cantidad', '1'))
    except ValueError:
        cantidad_solicitada = 1
    if cantidad_solicitada < 1:
        cantidad_solicitada = 1

    if producto.stock <= 0:
        messages.error(request, _('%(name)s está sin stock') % {'name': producto.nombre})
        return redirect('product_list')
    item, created = ItemCarrito.objects.get_or_create(
        carrito=cart,
        producto=producto,
        defaults={'cantidad': cantidad_solicitada}
    )
    if not created:
        # Validar que la nueva cantidad no exceda el stock disponible
        nueva_cantidad = item.cantidad + cantidad_solicitada
        if nueva_cantidad > producto.stock:
            messages.error(request, _('No hay stock suficiente de %(name)s') % {'name': producto.nombre})
            return redirect('product_list')
        item.cantidad = nueva_cantidad
        item.save()
        messages.success(request, _('Se agregaron %(qty)s unidad(es) de %(name)s al carrito') % {'qty': cantidad_solicitada, 'name': producto.nombre})
    else:
        # Validado arriba y creado con la cantidad solicitada
        if cantidad_solicitada > producto.stock:
            # Si la cantidad solicitada supera el stock, corregimos o avisamos
            item.cantidad = producto.stock
            item.save(update_fields=['cantidad'])
            messages.warning(request, _('Cantidad ajustada a stock disponible (%(stock)s) para %(name)s') % {'stock': producto.stock, 'name': producto.nombre})
        else:
            messages.success(request, f'Se agregaron {cantidad_solicitada} unidad(es) de {producto.nombre} al carrito')
    
    # Redirigir al catálogo con un mensaje de confirmación
    return redirect('product_list')

@login_required
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request.user)
    item = get_object_or_404(ItemCarrito, pk=item_id, carrito=cart)
    if request.method == 'POST':
        nombre = item.producto.nombre
        item.delete()
        messages.info(request, _('Se eliminó %(name)s del carrito') % {'name': nombre})
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart = get_or_create_cart(request.user)
    return render(request, 'store/cart.html', {'cart': cart})

from django.http import JsonResponse
from django.urls import reverse

def api_products(request):
    productos = Producto.objects.filter(stock__gt=0).order_by('-fecha_creacion')
    data = []
    for p in productos:
        data.append({
            'id': p.pk,
            'nombre': p.nombre,
            'precio': float(p.precio),
            'stock': p.stock,
            'categoria': p.categoria.nombre if getattr(p, 'categoria', None) else None,
            'detalle_url': request.build_absolute_uri(reverse('product_detail', args=[p.pk])),
            'imagen_url': request.build_absolute_uri(p.imagen.url) if p.imagen else None,
        })
    return JsonResponse({'count': len(data), 'results': data})

@login_required
@transaction.atomic
def create_order(request):
    cart = get_or_create_cart(request.user)
    if cart.items.count() == 0:
        return redirect('product_list')
    next_url = request.POST.get('next') or request.GET.get('next')
    # Validar stock antes de crear la orden
    for item in cart.items.all():
        if item.cantidad > item.producto.stock:
            messages.error(request, _('Sin stock suficiente para %(name)s. Disponible: %(stock)s') % {'name': item.producto.nombre, 'stock': item.producto.stock})
            return redirect('view_cart')

    orden = Orden.objects.create(usuario=request.user, total=0)
    for item in cart.items.all():
        DetalleOrden.objects.create(
            orden=orden,
            producto=item.producto,
            cantidad=item.cantidad,
            precioUnitario=item.producto.precio
        )
        # Descontar stock al confirmar
        producto = item.producto
        producto.stock -= item.cantidad
        producto.save(update_fields=['stock'])
    orden.calcular_total()
    # limpiar carrito
    cart.items.all().delete()
    if next_url:
        return redirect(next_url)
    return render(request, 'store/order_confirm.html', {'orden': orden})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, _('¡Cuenta creada exitosamente para %(username)s!') % {'username': username})
            # Iniciar sesión automáticamente después del registro
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
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
            messages.success(request, _('¡Bienvenido de vuelta, %(username)s!') % {'username': username})
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('product_list')
        else:
            messages.error(request, _('Usuario o contraseña incorrectos.'))
    return render(request, 'store/login.html')

def user_logout(request):
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, _('Has cerrado sesión exitosamente.'))
    return redirect('product_list')

def external_products(request):
    url = 'URL_DEL_SERVICIO_EXTERNO'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        productos = data.get('results', [])
    except Exception as e:
        productos = []
        messages.error(request, f'Error al consumir el servicio externo: {e}')
    return render(request, 'store/external_products.html', {'productos': productos})

def cargar_productos(request):
    # Cambia aquí la implementación según la fuente deseada
    loader = HardcodedProductLoader()  # O ApiProductLoader()
    productos = loader.load_products()
    return render(request, "store/productos_externos.html", {"productos": productos})

def get_medellin_weather():
    api_key = '6401c6a1e707c70cb4992b3391a366e9'
    url = f'https://api.openweathermap.org/data/2.5/weather?q=Medellin,CO&appid={api_key}&units=metric&lang=es'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        clima = {
            'temp': data['main']['temp'],
            'desc': data['weather'][0]['description'].capitalize(),
            'icon': data['weather'][0]['icon'],
        }
    except Exception:
        clima = None
    return clima
