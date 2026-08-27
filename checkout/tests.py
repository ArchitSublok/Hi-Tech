from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from cart.models import Cart, CartItem
from checkout.models import Address
from payments.choices import PaymentMethod
from payments.validators import PaymentValidationError, available_payment_methods, validate_payment_method
from products.models import Category, Product


class PaymentRulesTests(TestCase):
    def test_cod_is_available_only_below_300(self):
        self.assertIn(PaymentMethod.COD, [value for value, _ in available_payment_methods(Decimal('299.99'))])
        self.assertNotIn(PaymentMethod.COD, [value for value, _ in available_payment_methods(Decimal('300.00'))])

    def test_cod_is_rejected_server_side_at_300_or_more(self):
        with self.assertRaises(PaymentValidationError):
            validate_payment_method(Decimal('300.00'), PaymentMethod.COD)


class CheckoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('customer', 'customer@example.com', 'secure-password-123')
        self.category = Category.objects.create(name='Components')
        self.product = Product.objects.create(
            name='Controller', category=self.category, price=Decimal('300.00'), stock=5
        )
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        self.address = Address.objects.create(
            user=self.user,
            recipient_name='Customer',
            phone='9876543210',
            street_address='1 Market Road',
            area_locality='Central',
            city='Delhi',
            state='Delhi',
            postal_code='110001',
        )
        self.client.force_login(self.user)

    def test_checkout_hides_cod_for_300_order_total(self):
        response = self.client.get('/checkout/')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'value="cod"')
        self.assertContains(response, 'value="upi"')

    def test_checkout_rejects_tampered_cod_submission(self):
        response = self.client.post('/checkout/', {
            'address_id': self.address.id,
            'payment_method': PaymentMethod.COD,
        })

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Cash on Delivery is only available', status_code=400)
