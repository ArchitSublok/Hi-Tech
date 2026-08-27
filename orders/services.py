from collections import defaultdict
from decimal import Decimal

from django.db import transaction

from cart.models import Cart
from payments.validators import validate_payment_method
from products.models import Product

from .models import Order, OrderItem


class CheckoutError(Exception):
    """A customer-facing checkout validation error."""


def calculate_order_total(cart_items):
    """Return the final checkout total used for payment eligibility.

    This store currently has no configured shipping, tax, or discount rules, so
    each is zero and the final total equals the product subtotal. Keeping the
    calculation in one place means those adjustments can be added without
    changing payment validation code.
    """
    subtotal = sum(
        (item.product.price * item.quantity for item in cart_items),
        Decimal('0.00'),
    )
    shipping = Decimal('0.00')
    taxes = Decimal('0.00')
    discounts = Decimal('0.00')
    return subtotal + shipping + taxes - discounts


@transaction.atomic
def create_order_from_cart(user, address, payment_method):
    """Create an immutable purchase record and reduce stock in one transaction."""
    try:
        cart = Cart.objects.select_for_update().get(user=user)
    except Cart.DoesNotExist as exc:
        raise CheckoutError('Your cart is empty.') from exc

    cart_items = list(cart.items.select_related('product').order_by('product_id'))
    if not cart_items:
        raise CheckoutError('Your cart is empty.')

    requested = defaultdict(int)
    for item in cart_items:
        requested[item.product_id] += item.quantity

    locked_products = {
        product.id: product
        for product in Product.objects.select_for_update().filter(id__in=requested).order_by('id')
    }
    for product_id, quantity in requested.items():
        product = locked_products.get(product_id)
        if not product or not product.is_active:
            raise CheckoutError('One of the products in your cart is no longer available.')
        if product.stock < quantity:
            raise CheckoutError(f'Only {product.stock} unit(s) of {product.name} are available.')

    subtotal = sum((locked_products[item.product_id].price * item.quantity for item in cart_items), Decimal('0.00'))
    order_total = subtotal

    try:
        validate_payment_method(order_total, payment_method)
    except Exception as exc:
        raise CheckoutError(str(exc)) from exc

    order = Order.objects.create(
        user=user,
        subtotal=subtotal,
        payment_method=payment_method,
        recipient_name=address.recipient_name,
        phone=address.phone,
        shipping_address=f"{address.street_address}, {address.area_locality}",
        city=address.city,
        state=address.state,
        postal_code=address.postal_code,
        latitude=address.latitude,
        longitude=address.longitude,
    )
    OrderItem.objects.bulk_create([
        OrderItem(
            order=order,
            product=locked_products[item.product_id],
            product_name=locked_products[item.product_id].name,
            unit_price=locked_products[item.product_id].price,
            quantity=item.quantity,
        )
        for item in cart_items
    ])

    for product_id, quantity in requested.items():
        product = locked_products[product_id]
        product.stock -= quantity
        product.save(update_fields=['stock', 'updated_at'])

    cart.items.all().delete()
    return order


@transaction.atomic
def change_order_status(order, new_status):
    """Update a sale status and return stock if a confirmed order is cancelled."""
    locked_order = Order.objects.select_for_update().get(pk=order.pk)
    if locked_order.status == new_status:
        return locked_order

    items = list(locked_order.items.order_by('product_id'))
    products = {
        product.id: product
        for product in Product.objects.select_for_update().filter(
            id__in=[item.product_id for item in items]
        ).order_by('id')
    }

    if new_status == Order.Status.CANCELLED and locked_order.stock_reduced:
        for item in items:
            product = products[item.product_id]
            product.stock += item.quantity
            product.save(update_fields=['stock', 'updated_at'])
        locked_order.stock_reduced = False

    if locked_order.status == Order.Status.CANCELLED and new_status != Order.Status.CANCELLED:
        for item in items:
            product = products[item.product_id]
            if not product.is_active or product.stock < item.quantity:
                raise CheckoutError(f'Not enough stock to reactivate order {locked_order.number}.')
        for item in items:
            product = products[item.product_id]
            product.stock -= item.quantity
            product.save(update_fields=['stock', 'updated_at'])
        locked_order.stock_reduced = True

    locked_order.status = new_status
    locked_order.save(update_fields=['status', 'stock_reduced', 'updated_at'])
    return locked_order
