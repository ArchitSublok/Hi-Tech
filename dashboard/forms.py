from django import forms
from django.contrib.auth import authenticate

from coupons.models import Coupon

from orders.models import Order
from products.models import Category, Product


class StaffLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('email') or not cleaned.get('password'):
            return cleaned
        self.user = authenticate(self.request, email=cleaned['email'], password=cleaned['password'])
        if self.user is None:
            raise forms.ValidationError('Incorrect email or password.')
        if not self.user.is_staff:
            raise forms.ValidationError('This account does not have management access.')
        return cleaned

    def get_user(self):
        return self.user


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category', 'stock', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'min': '0'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Image files must be 5 MB or smaller.')
        return image


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['stock', 'is_active']
        widgets = {'stock': forms.NumberInput(attrs={'min': '0'})}


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_type', 'discount_value', 'products', 'minimum_order_value', 'valid_from', 'valid_until', 'usage_limit', 'is_active']
        widgets = {
            'discount_value': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'minimum_order_value': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'usage_limit': forms.NumberInput(attrs={'min': '1'}),
        }

    def clean_code(self):
        return self.cleaned_data['code'].strip().upper()

    def clean(self):
        cleaned = super().clean()
        valid_from = cleaned.get('valid_from')
        valid_until = cleaned.get('valid_until')
        if valid_from and valid_until and valid_until <= valid_from:
            self.add_error('valid_until', 'End date must be after the start date.')
        return cleaned