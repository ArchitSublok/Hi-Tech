from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from cart.models import Cart, CartItem
from products.models import Category, Product

from .models import Order
from .services import CheckoutError, change_order_status, create_order_from_cart


class CheckoutServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('buyer', 'buyer@example.com', 'safe-password-123')
        category = Category.objects.create(name='Laptops')
        self.product = Product.objects.create(
            name='Work Laptop',
            description='A reliable test product.',
            price=Decimal('49999.00'),
            category=category,
            stock=4,
        )

    def test_checkout_creates_order_snapshot_and_reduces_stock(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        order = create_order_from_cart(self.user)

        self.product.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CONFIRMED)
        self.assertEqual(order.subtotal, Decimal('99998.00'))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product_name, 'Work Laptop')
        self.assertEqual(self.product.stock, 2)
        self.assertFalse(cart.items.exists())

    def test_checkout_refuses_more_than_available_stock(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=5)

        with self.assertRaises(CheckoutError):
            create_order_from_cart(self.user)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 4)
        self.assertEqual(Order.objects.count(), 0)

    def test_cancelling_and_reactivating_order_adjusts_stock_once(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        order = create_order_from_cart(self.user)

        change_order_status(order, Order.Status.CANCELLED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 4)

        change_order_status(order, Order.Status.PROCESSING)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_customer_can_add_to_cart_then_checkout_through_views(self):
        self.client.force_login(self.user)

        add_response = self.client.post(reverse('cart:add', args=[self.product.id]), {'quantity': 2})
        checkout_response = self.client.post(reverse('orders:checkout'))

        self.product.refresh_from_db()
        self.assertRedirects(add_response, reverse('cart:detail'))
        self.assertRedirects(checkout_response, reverse('orders:order_list'))
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(self.product.stock, 2)
