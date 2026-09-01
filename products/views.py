from django.db.models import DecimalField, F
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from .models import Brand, PriceRange, Product, Category


def _is_approved_dealer(user):
    return (
        user.is_authenticated
        and hasattr(user, 'profile')
        and user.profile.is_dealer
        and user.profile.is_approved
    )


def products(request):
    queryset = Product.objects.select_related('category', 'brand').filter(is_active=True)

    if _is_approved_dealer(request.user):
        queryset = queryset.annotate(
            effective_price=Coalesce('dealer_price', 'price', output_field=DecimalField())
        )
    else:
        queryset = queryset.annotate(effective_price=F('price'))

    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(name__icontains=query)

    category_id = request.GET.get('category')
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    brand_id = request.GET.get('brand')
    if brand_id:
        queryset = queryset.filter(brand_id=brand_id)

    price_range_id = request.GET.get('price_range')
    selected_range = None
    if price_range_id:
        selected_range = PriceRange.objects.filter(id=price_range_id, is_active=True).first()
        if selected_range:
            queryset = queryset.filter(effective_price__gte=selected_range.min_value)
            if selected_range.max_value is not None:
                queryset = queryset.filter(effective_price__lte=selected_range.max_value)

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        queryset = queryset.order_by('effective_price')
    elif sort == 'price_desc':
        queryset = queryset.order_by('-effective_price')
    else:
        queryset = queryset.order_by('-created_at')

    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    wishlisted_ids = set()
    if request.user.is_authenticated:
        wishlisted_ids = set(request.user.wishlist_items.values_list('product_id', flat=True))

    return render(request, 'products/products.html', {
        'products': page_obj,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'price_ranges': PriceRange.objects.filter(is_active=True),
        'selected_category': category_id,
        'selected_brand': brand_id,
        'selected_price_range': price_range_id,
        'search_query': query or '',
        'wishlisted_ids': wishlisted_ids,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related('category', 'brand').filter(is_active=True), pk=product_id)
    wishlisted_ids = set()
    if request.user.is_authenticated:
        wishlisted_ids = set(request.user.wishlist_items.values_list('product_id', flat=True))
    return render(request, 'products/product_detail.html', {'product': product, 'wishlisted_ids': wishlisted_ids})