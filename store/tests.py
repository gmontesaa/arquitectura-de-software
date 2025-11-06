from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from django.contrib.auth.models import User
from .models import Producto, Carrito, ItemCarrito
class SmokeTest(TestCase):
    def test_add_to_cart(self):
        u = User.objects.create_user('testuser','t@x.com','pass')
        p = Producto.objects.create(nombre='A', precio=10, stock=5)
        self.client.login(username='testuser', password='pass')
        resp = self.client.post(reverse('add_to_cart', args=[p.pk]), {'cantidad': 2})
        self.assertEqual(resp.status_code, 302)
        # stock no cambia hasta confirmar orden
        p.refresh_from_db()
        self.assertEqual(p.stock, 5)

    def test_api_products_returns_json(self):
        Producto.objects.create(nombre='Prod1', precio=12, stock=3)
        Producto.objects.create(nombre='Prod2', precio=6, stock=0)  # fuera de stock, no debe salir
        resp = self.client.get(reverse('api_products'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('results', data)
        self.assertEqual(data['count'], 1)
        self.assertIn('detalle_url', data['results'][0])

    def test_i18n_switch_language(self):
        with translation.override('en'):
            url = reverse('product_list')
            self.assertTrue(url.startswith('/en/'))
