from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from products.models import Product


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage off'
        FIXED = 'fixed', 'Fixed amount off'

    code = models.CharField(max_length=32, unique=True)
    discount_type = models.CharField(max_length=12, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    products = models.ManyToManyField(Product, blank=True, related_name='coupons', help_text='Leave empty to apply this coupon to every product in the store.')
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text='Leave blank for unlimited uses.')
    times_used = models.PositiveIntegerField(default=0, editable=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='coupons_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def discount_display(self):
        if self.discount_type == self.DiscountType.PERCENTAGE:
            return f"{self.discount_value:g}% off"
        return f"₹{self.discount_value} off"