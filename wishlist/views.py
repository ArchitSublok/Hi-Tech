from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .models import WishlistItem


@login_required
def wishlist_detail(request):
    items = WishlistItem.objects.filter(user=request.user).select_related('product', 'product__category')
    return render(request, 'wishlist/wishlist_detail.html', {'items': items})


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
        messages.info(request, f'{product.name} was removed from your wishlist.')
    else:
        messages.success(request, f'{product.name} was added to your wishlist.')
    return redirect(request.POST.get('next') or 'wishlist:detail')


@login_required
@require_POST
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem, pk=item_id, user=request.user)
    name = item.product.name
    item.delete()
    messages.info(request, f'{name} was removed from your wishlist.')
    return redirect('wishlist:detail')


def wishlist_summary(request):
    if not request.user.is_authenticated:
        return {'wishlist_count': 0}
    return {'wishlist_count': WishlistItem.objects.filter(user=request.user).count()}