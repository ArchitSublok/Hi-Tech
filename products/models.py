from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PriceRange(models.Model):
    label = models.CharField(max_length=50, help_text='Shown to customers, e.g. "Under ₹1,000".')
    min_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Leave blank for no upper limit, e.g. "Over ₹5,000".',
    )
    display_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first.')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'min_value']

    def __str__(self):
        return self.label


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    dealer_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Shown only to approved dealers. Leave blank to charge dealers the regular price.',
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, help_text='Uncheck to hide this product from customers.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        return self.is_active and self.stock > 0

    def price_for(self, user):
        if (
            user.is_authenticated
            and hasattr(user, 'profile')
            and user.profile.is_dealer
            and user.profile.is_approved
            and self.dealer_price is not None
        ):
            return self.dealer_price
        return self.price

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