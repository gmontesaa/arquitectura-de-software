# Artesanías - Proyecto Django (esqueleto)

Proyecto demo de comercio electrónico para venta de productos artesanales.

Resumen:
- Django project: `artesanias`
- App: `store`
- Funcionalidades: catálogo, carrito, órdenes, admin para gestionar productos.

Instrucciones rápidas:
1. Crear y activar un entorno virtual (Python 3.10+ recomendado).
2. `pip install -r requirements.txt`
3. `django-admin startproject artesanias .` (si quieres usar manage.py generado aquí)
4. `python manage.py makemigrations`
5. `python manage.py migrate`
6. `python manage.py createsuperuser` (para acceder al admin)
7. `python manage.py runserver` y visitar http://127.0.0.1:8000/

Notas:
- Este repositorio contiene un esqueleto con los archivos principales (models, views, urls, templates).
- Está pensado para ser educativo y extensible.