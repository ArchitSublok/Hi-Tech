from decimal import Decimal

from .choices import COD_THRESHOLD, PaymentMethod


class PaymentValidationError(Exception):
    """Raised when a payment method isn't allowed for a given order total."""


def available_payment_methods(order_total: Decimal):
    """Return which payment methods the frontend should show for this total."""
    if order_total < COD_THRESHOLD:
        return list(PaymentMethod.choices)
    return [c for c in PaymentMethod.choices if c[0] != PaymentMethod.COD]


def validate_payment_method(order_total: Decimal, payment_method: str):
    """Server-side safeguard — never trust the frontend alone."""
    if order_total >= COD_THRESHOLD and payment_method == PaymentMethod.COD:
        raise PaymentValidationError(
            f"Cash on Delivery is only available for orders under ₹{COD_THRESHOLD}."
        )
    if payment_method not in PaymentMethod.values:
        raise PaymentValidationError("Please select a valid payment method.")