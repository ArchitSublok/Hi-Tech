from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_display', 'is_active', 'times_used', 'usage_limit', 'valid_until')
    list_filter = ('is_active', 'discount_type')
    search_fields = ('code',)
    filter_horizontal = ('products',)