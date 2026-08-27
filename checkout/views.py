from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404

from cart.models import Cart
from orders.services import CheckoutError, calculate_order_total, create_order_from_cart
from payments.choices import COD_THRESHOLD
from payments.validators import PaymentValidationError, available_payment_methods, validate_payment_method
from .forms import AddressForm
from .models import Address


@login_required
def checkout_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect('cart:detail')

    cart_items = cart.items.select_related('product')
    order_total = calculate_order_total(cart_items)
    saved_addresses = Address.objects.filter(user=request.user)
    address_form = AddressForm()

    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')
        try:
            validate_payment_method(order_total, payment_method)
        except PaymentValidationError as exc:
            # Keep the server authoritative if a client submits a hidden COD option.
            return HttpResponseBadRequest(str(exc))

        if address_id and address_id != 'new':
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            address_form = AddressForm(request.POST)
            address = None
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = request.user
                address.save()
            else:
                messages.error(request, 'Please correct the delivery address errors below.')

        if address:
            try:
                order = create_order_from_cart(request.user, address, payment_method)
            except CheckoutError as exc:
                messages.error(request, str(exc))
            else:
                messages.success(request, f"Order {order.number} placed successfully.")
                return redirect('orders:order_list')

    return render(request, 'checkout/checkout.html', {
        'saved_addresses': saved_addresses,
        'address_form': address_form,
        'order_total': order_total,
        'available_methods': available_payment_methods(order_total),
        'cod_threshold': COD_THRESHOLD,
    })
