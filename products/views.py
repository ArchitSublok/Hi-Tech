from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Product, Category

def products(request):
    queryset = Product.objects.select_related('category').all()

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

    return render(request, 'products/products.html', {
        'products': page_obj,
        'categories': Category.objects.all(),
        'selected_category': category_id,
        'selected_sort': sort,
        'selected_price_range': price_range,
        'search_query': query or '',
    })