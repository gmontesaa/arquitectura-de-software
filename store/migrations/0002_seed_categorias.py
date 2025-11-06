from django.db import migrations


def seed_categories_and_assign_products(apps, schema_editor):
    Categoria = apps.get_model('store', 'Categoria')
    Producto = apps.get_model('store', 'Producto')

    # Crear categorías base (idempotente por unique en nombre)
    nombres = [
        'Cerámica', 'Textil', 'Madera', 'Joyería', 'Cuero', 'Vidrio', 'Piedra', 'Metal', 'Otros'
    ]
    nombre_to_cat = {}
    for nombre in nombres:
        cat, _ = Categoria.objects.get_or_create(nombre=nombre)
        nombre_to_cat[nombre] = cat

    # Mapeo de palabras clave -> categoría
    keyword_map = [
        (['ceram', 'barro', 'arcilla'], 'Cerámica'),
        (['textil', 'tej', 'tela', 'lana', 'algod'], 'Textil'),
        (['madera', 'tallado', 'tallar'], 'Madera'),
        (['joy', 'collar', 'arete', 'pulsera', 'anillo'], 'Joyería'),
        (['cuero', 'piel'], 'Cuero'),
        (['vidrio', 'cristal', 'soplado'], 'Vidrio'),
        (['piedra', 'mármol', 'marmol', 'ónix', 'onix'], 'Piedra'),
        (['metal', 'hierro', 'bronce', 'cobre', 'aluminio'], 'Metal'),
    ]

    for producto in Producto.objects.all():
        texto = f"{producto.nombre} {producto.descripcion or ''}".lower()
        asignada = None
        for keywords, nombre_cat in keyword_map:
            if any(k in texto for k in keywords):
                asignada = nombre_to_cat[nombre_cat]
                break
        if asignada is None:
            asignada = nombre_to_cat['Otros']
        # Solo actualizar si cambió o estaba vacío
        if producto.categoria_id != asignada.id:
            producto.categoria = asignada
            producto.save(update_fields=['categoria'])


def unseed_categories_and_unassign_products(apps, schema_editor):
    Categoria = apps.get_model('store', 'Categoria')
    Producto = apps.get_model('store', 'Producto')

    nombres = [
        'Cerámica', 'Textil', 'Madera', 'Joyería', 'Cuero', 'Vidrio', 'Piedra', 'Metal', 'Otros'
    ]
    # Desasignar productos que pertenezcan a estas categorías creadas por el seed
    productos = Producto.objects.filter(categoria__nombre__in=nombres)
    for p in productos:
        p.categoria = None
        p.save(update_fields=['categoria'])
    # Eliminar categorías sembradas
    Categoria.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories_and_assign_products, unseed_categories_and_unassign_products),
    ]


