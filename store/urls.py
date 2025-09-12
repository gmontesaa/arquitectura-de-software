from django.urls import path
from . import views
urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('producto/<int:pk>/', views.product_detail, name='product_detail'),
    path('carrito/', views.view_cart, name='view_cart'),
    path('carrito/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('orden/create/', views.create_order, name='create_order'),
    path('registro/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
