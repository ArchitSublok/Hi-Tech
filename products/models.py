from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, help_text='Uncheck to hide this product from customers.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        return self.is_active and self.stock > 0

    @property
    def sold_quantity(self):
        from orders.models import OrderItem

        return OrderItem.objects.filter(
            product=self,
            order__status__in=['confirmed', 'processing', 'shipped', 'completed'],
        ).aggregate(total=models.Sum('quantity'))['total'] or 0


class Order(models.Model):
    """Legacy product-level purchases retained for existing database compatibility.

    New checkouts are represented by ``orders.Order`` and ``orders.OrderItem``.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bought {self.product.name}"
