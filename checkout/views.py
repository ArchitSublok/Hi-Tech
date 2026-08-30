from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from cart.models import Cart
from orders.services import create_order_from_cart, CheckoutError
from payments.choices import PaymentMethod
from payments.validators import available_payment_methods
from .models import Address


@login_required
def checkout_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect('cart:detail')

    subtotal = sum((item.product.price * item.quantity for item in cart.items.select_related('product')), Decimal('0.00'))
    saved_addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')
        coupon_code = request.POST.get('coupon_code', '').strip()

        if address_id and address_id != 'new':
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            address = Address.objects.create(
                user=request.user,
                recipient_name=request.POST.get('recipient_name', '').strip(),
                phone=request.POST.get('phone', '').strip(),
                street_address=request.POST.get('street_address', '').strip(),
                area_locality=request.POST.get('area_locality', '').strip(),
                city=request.POST.get('city', '').strip(),
                state=request.POST.get('state', '').strip(),
                postal_code=request.POST.get('postal_code', '').strip(),
                latitude=request.POST.get('latitude') or None,
                longitude=request.POST.get('longitude') or None,
            )

        try:
            order = create_order_from_cart(request.user, address, payment_method, coupon_code)
        except CheckoutError as exc:
            messages.error(request, str(exc))
        else:
            if order.discount_amount:
                messages.success(request, f"Order {order.number} placed — you saved ₹{order.discount_amount} with {order.coupon_code}.")
            if payment_method == PaymentMethod.UPI:
                return redirect('payments:upi_payment', order_number=order.number)
            messages.success(request, f"Order {order.number} placed successfully.")
            return redirect('orders:order_list')

    return render(request, 'checkout/checkout.html', {
        'saved_addresses': saved_addresses,
        'subtotal': subtotal,
        'order_total': subtotal,
        'available_methods': available_payment_methods(subtotal),
        'cod_threshold': 300,
    })