from decimal import Decimal

from django.utils import timezone

from .models import Coupon


class CouponError(Exception):
    """A customer-facing coupon validation error."""


def get_valid_coupon(code, cart_items, subtotal):
    code = (code or '').strip().upper()
    if not code:
        raise CouponError('Enter a coupon code.')

    try:
        coupon = Coupon.objects.get(code__iexact=code)
    except Coupon.DoesNotExist as exc:
        raise CouponError('That coupon code was not found.') from exc

    now = timezone.now()
    if not coupon.is_active:
        raise CouponError('This coupon is no longer active.')
    if now < coupon.valid_from:
        raise CouponError('This coupon is not active yet.')
    if now > coupon.valid_until:
        raise CouponError('This coupon has expired.')
    if coupon.usage_limit is not None and coupon.times_used >= coupon.usage_limit:
        raise CouponError('This coupon has reached its usage limit.')
    if subtotal < coupon.minimum_order_value:
        raise CouponError(f'Add ₹{coupon.minimum_order_value - subtotal} more to use this coupon.')

    restricted_products = set(coupon.products.values_list('id', flat=True))
    if restricted_products:
        cart_product_ids = {item.product_id for item in cart_items}
        if not restricted_products & cart_product_ids:
            raise CouponError('This coupon does not apply to any item in your cart.')

    return coupon


def calculate_discount(coupon, cart_items, subtotal):
    restricted_products = set(coupon.products.values_list('id', flat=True))
    if restricted_products:
        eligible_total = sum(
            (item.product.price * item.quantity for item in cart_items if item.product_id in restricted_products),
            Decimal('0.00'),
        )
    else:
        eligible_total = subtotal

    if coupon.discount_type == coupon.DiscountType.PERCENTAGE:
        discount = eligible_total * (coupon.discount_value / Decimal('100'))
    else:
        discount = coupon.discount_value

    return min(discount, eligible_total)