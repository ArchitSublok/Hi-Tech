from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .models import Cart, CartItem


def _cart_for(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_detail(request):
    cart = _cart_for(request.user)
    items = cart.items.select_related('product').order_by('created_at')
    return render(request, 'cart/cart_detail.html', {'cart': cart, 'items': items})


@login_required
@require_POST
@transaction.atomic
def add_to_cart(request, product_id):
    product = get_object_or_404(Product.objects.select_for_update(), pk=product_id, is_active=True)
    if product.stock == 0:
        messages.error(request, f'{product.name} is out of stock.')
        return redirect(request.POST.get('next') or 'products')

    try:
        quantity = max(1, int(request.POST.get('quantity', 1)))
    except (TypeError, ValueError):
        quantity = 1

    cart = _cart_for(request.user)
    item, created = CartItem.objects.select_for_update().get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 0},
    )
    desired_quantity = quantity if created else item.quantity + quantity
    if desired_quantity > product.stock:
        messages.error(request, f'Only {product.stock} unit(s) of {product.name} are available.')
    else:
        item.quantity = desired_quantity
        item.save(update_fields=['quantity', 'updated_at'])
        messages.success(request, f'{product.name} was added to your cart.')
    return redirect(request.POST.get('next') or 'cart:detail')


@login_required
@require_POST
@transaction.atomic
def update_cart_item(request, item_id):
    item = get_object_or_404(
        CartItem.objects.select_for_update().select_related('product', 'cart'),
        pk=item_id,
        cart__user=request.user,
    )
    try:
        quantity = int(request.POST.get('quantity', item.quantity))
    except (TypeError, ValueError):
        quantity = item.quantity

    if quantity <= 0:
        item.delete()
        messages.info(request, f'{item.product.name} was removed from your cart.')
    elif not item.product.is_active or item.product.stock < quantity:
        messages.error(request, f'Only {item.product.stock} unit(s) of {item.product.name} are available.')
    else:
        item.quantity = quantity
        item.save(update_fields=['quantity', 'updated_at'])
        messages.success(request, 'Cart updated.')
    return redirect('cart:detail')


@login_required
@require_POST
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    name = item.product.name
    item.delete()
    messages.info(request, f'{name} was removed from your cart.')
    return redirect('cart:detail')


def cart_summary(request):
    
    if not request.user.is_authenticated:
        return {'cart_count': 0}
    try:
        return {'cart_count': request.user.cart.total_items}
    except Cart.DoesNotExist:
        return {'cart_count': 0}
    
