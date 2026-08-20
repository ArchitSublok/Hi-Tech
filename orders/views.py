from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .services import CheckoutError, create_order_from_cart


@login_required
def order_list(request):
    orders = request.user.orders.prefetch_related('items').all()
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
@require_POST
def checkout(request):
    try:
        order = create_order_from_cart(request.user)
    except CheckoutError as exc:
        messages.error(request, str(exc))
        return redirect('cart:detail')

    messages.success(request, f'Order {order.number} was placed successfully. We will keep you updated.')
    return redirect('orders:order_list')
