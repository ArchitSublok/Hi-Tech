from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class ManagementAccessTests(TestCase):
    def test_customer_cannot_access_management_dashboard(self):
        customer = User.objects.create_user('customer', 'customer@example.com', 'safe-password-123')
        self.client.force_login(customer)

        response = self.client.get(reverse('management:home'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('management:login'), response.url)

    def test_staff_can_access_management_dashboard(self):
        manager = User.objects.create_user('manager', 'manager@example.com', 'safe-password-123', is_staff=True)
        self.client.force_login(manager)

        response = self.client.get(reverse('management:home'))

        self.assertEqual(response.status_code, 200)

    def test_public_and_management_pages_render(self):
        category = Category.objects.create(name='Accessories')
        product = Product.objects.create(name='Keyboard', price='1999.00', category=category, stock=3)
        manager = User.objects.create_user('manager', 'manager@example.com', 'safe-password-123', is_staff=True)

        for url in (reverse('home'), reverse('products'), reverse('product_detail', args=[product.id]), reverse('about')):
            self.assertEqual(self.client.get(url).status_code, 200)

        self.client.force_login(manager)
        for url in (reverse('management:products'), reverse('management:categories'), reverse('management:inventory'), reverse('management:orders'), reverse('management:users')):
            self.assertEqual(self.client.get(url).status_code, 200)
