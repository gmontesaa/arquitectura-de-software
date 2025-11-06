# Artesanías - Proyecto Django (esqueleto)

Proyecto demo de comercio electrónico para venta de productos artesanales.

Resumen:
- Django project: `artesanias`
- App: `store`
- Funcionalidades: catálogo con búsqueda, filtrado por categoría, ordenamiento y paginación; carrito; órdenes; admin; i18n ES/EN; endpoint JSON público; pruebas unitarias.

Instrucciones rápidas:
1. Crear y activar un entorno virtual (Python 3.10+ recomendado).
2. `pip install -r requirements.txt`
3. `django-admin startproject artesanias .` (si quieres usar manage.py generado aquí)
4. `python manage.py makemigrations`
5. `python manage.py migrate`
6. `python manage.py createsuperuser` (para acceder al admin)
7. `python manage.py runserver` y visitar http://127.0.0.1:8000/

Internacionalización (i18n) ES/EN:
- Selector de idioma en la barra superior. Rutas con prefijo `/es/` y `/en/` (ej. `http://127.0.0.1:8000/en/`).
- Traducciones ubicadas en `locale/es/LC_MESSAGES/django.po` y `locale/en/LC_MESSAGES/django.po`.
- Compilar traducciones (Windows sin gettext):

```powershell
python -m pip install polib -q
$code = @'
import os, polib
base = os.getcwd()
locale_dir = os.path.join(base, "locale")
for root, _, files in os.walk(locale_dir):
    for f in files:
        if f.endswith(".po"):
            po_path = os.path.join(root, f)
            mo_path = os.path.join(root, f[:-3] + ".mo")
            po = polib.pofile(po_path)
            os.makedirs(os.path.dirname(mo_path), exist_ok=True)
            po.save_as_mofile(mo_path)
            print("Compilado:", mo_path)
'@
$script = Join-Path (Get-Location) "compile_translations.py"
Set-Content -Path $script -Value $code -Encoding UTF8
python $script
Remove-Item $script
```

Endpoint JSON público:
- URL: `/api/products/`
- Respuesta: productos con `stock > 0` incluyendo `detalle_url` e `imagen_url`.

Rutas principales:
- `/` catálogo con búsqueda (`q`), categoría (`categoria`), orden (`sort`), paginación (`page`).
- `/producto/<id>/` detalle con relacionados.
- `/carrito/` ver carrito (elimina y crea orden).
- `/api/products/` JSON de productos en stock.
- `/admin/` panel de administración.

Pruebas:
- Ejecutar: `python manage.py test`
- Incluyen: prueba de añadir al carrito (stock no baja hasta confirmar) y prueba del endpoint JSON.

Usabilidad:
- Plantillas unificadas con `base.html`, navegación superior, breadcrumbs en detalle, responsivo.
- Formularios consistentes (login/registro) con persistencia de valores ante errores.

Notas:
- Este repositorio contiene un esqueleto con los archivos principales (models, views, urls, templates).
- Está pensado para ser educativo y extensible.