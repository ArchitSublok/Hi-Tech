from urllib.parse import quote

from django.conf import settings


def build_upi_link(amount, order_number):
    payee = quote(settings.UPI_PAYEE_NAME)
    note = quote(f"Order {order_number}")
    return f"upi://pay?pa={settings.UPI_ID}&pn={payee}&am={amount}&cu=INR&tn={note}"


def build_upi_qr_url(upi_link, size=260):
    return f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={quote(upi_link)}"