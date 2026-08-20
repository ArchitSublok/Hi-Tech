from django.contrib import admin
from .models import Product, Category, Order



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'updated_at')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'description')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Order)
class LegacyOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'ordered_at')
    readonly_fields = ('ordered_at',)
