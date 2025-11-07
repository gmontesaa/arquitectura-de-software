from django.urls import path
from . import views
urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('producto/<int:pk>/', views.product_detail, name='product_detail'),
    path('carrito/', views.view_cart, name='view_cart'),
    path('carrito/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('api/products/', views.api_products, name='api_products'),
    path('carrito/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('orden/create/', views.create_order, name='create_order'),
    path('registro/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('external-products/', views.external_products, name='external_products'),
    path('productos-externos/', views.cargar_productos, name='productos_externos'),
    path('pago/', views.pago_ficticio, name='pago_ficticio'),
]
