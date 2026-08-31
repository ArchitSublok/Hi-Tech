from django import template

register = template.Library()


@register.filter
def display_price(product, user):
    return product.price_for(user)