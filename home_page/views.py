from django.shortcuts import render
from products.models import Product


def home(request):
    featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:4]
    wishlisted_ids = set()
    if request.user.is_authenticated:
        wishlisted_ids = set(request.user.wishlist_items.values_list('product_id', flat=True))
    return render(request, 'home_page/home.html', {'featured_products': featured_products, 'wishlisted_ids': wishlisted_ids})