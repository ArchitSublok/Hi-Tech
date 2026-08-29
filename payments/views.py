from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from orders.models import Order

from .utils import build_upi_link, build_upi_qr_url


@login_required
def upi_payment(request, order_number):
    order = get_object_or_404(Order, number=order_number, user=request.user)
    upi_link = build_upi_link(order.subtotal, order.number)
    qr_url = build_upi_qr_url(upi_link)
    return render(request, 'payments/upi_payment.html', {
        'order': order,
        'upi_link': upi_link,
        'qr_url': qr_url,
    })