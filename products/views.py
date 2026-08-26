from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from .models import Product, Category


def products(request):
    queryset = Product.objects.select_related('category').filter(is_active=True)

    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(name__icontains=query)

    category_id = request.GET.get('category')
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    price_range = request.GET.get('price_range')
    if price_range == 'under_1000':
        queryset = queryset.filter(price__lt=1000)
    elif price_range == '1000_5000':
        queryset = queryset.filter(price__gte=1000, price__lte=5000)
    elif price_range == 'over_5000':
        queryset = queryset.filter(price__gt=5000)

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        queryset = queryset.order_by('price')
    elif sort == 'price_desc':
        queryset = queryset.order_by('-price')
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
        'selected_category': category_id,
        'selected_sort': sort,
        'selected_price_range': price_range,
        'search_query': query or '',
        'wishlisted_ids': wishlisted_ids,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related('category').filter(is_active=True), pk=product_id)
    wishlisted_ids = set()
    if request.user.is_authenticated:
        wishlisted_ids = set(request.user.wishlist_items.values_list('product_id', flat=True))
    return render(request, 'products/product_detail.html', {'product': product, 'wishlisted_ids': wishlisted_ids})