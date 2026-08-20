from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'unit_price', 'quantity')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'user', 'status', 'subtotal', 'created_at')
    list_filter = ('status',)
    search_fields = ('number', 'user__email')
    readonly_fields = ('number', 'user', 'subtotal', 'created_at', 'updated_at', 'stock_reduced')
    inlines = [OrderItemInline]
