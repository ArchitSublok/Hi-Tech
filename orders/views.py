from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def order_list(request):
    orders = request.user.orders.prefetch_related('items').all()
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def checkout(request):
    """Legacy one-click checkout URL — redirects to the full checkout page,
    which collects a shipping address and payment method before placing the order."""
    return redirect('checkout:checkout')