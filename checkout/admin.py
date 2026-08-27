from django.contrib import admin

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'user', 'area_locality', 'city', 'postal_code', 'is_default')
    list_filter = ('is_default', 'city', 'state')
    search_fields = ('recipient_name', 'phone', 'street_address', 'area_locality', 'user__email')
