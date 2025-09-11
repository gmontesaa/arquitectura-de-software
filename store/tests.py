from django.test import TestCase
from django.contrib.auth.models import User
from .models import Producto, Carrito, ItemCarrito
class SmokeTest(TestCase):
    def test_add_to_cart(self):
        u = User.objects.create_user('testuser','t@x.com','pass')
        p = Producto.objects.create(nombre='A', precio=10, stock=5)
        self.client.login(username='testuser', password='pass')
        resp = self.client.get(f'/carrito/add/{p.pk}/')
        self.assertEqual(resp.status_code, 302)
