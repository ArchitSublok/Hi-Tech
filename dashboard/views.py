from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.deletion import ProtectedError
from django.db.models.functions import Coalesce
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from orders.models import Order
from orders.services import CheckoutError, change_order_status
from products.models import Category, Product

from .forms import CategoryForm, InventoryForm, OrderStatusForm, ProductForm, StaffLoginForm


def _is_staff(user):
    return user.is_authenticated and user.is_active and user.is_staff


staff_required = user_passes_test(_is_staff, login_url='management:login')


@never_cache
def staff_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('management:home')
        return HttpResponseForbidden('Your account does not have management access.')

    form = StaffLoginForm(request, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect(request.POST.get('next') or 'management:home')
    return render(request, 'dashboard/login.html', {'form': form})


@staff_required
@require_POST
def staff_logout(request):
    logout(request)
    messages.info(request, 'You have been signed out of management.')
    return redirect('management:login')


@staff_required
@never_cache
def dashboard_home(request):
    sales_orders = Order.objects.exclude(status=Order.Status.CANCELLED)
    context = {
        'product_count': Product.objects.count(),
        'user_count': User.objects.count(),
        'order_count': Order.objects.count(),
        'total_sales': sales_orders.aggregate(
            total=Coalesce(
                Sum('subtotal'),
                Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)),
            )
        )['total'],
        'low_stock': Product.objects.filter(is_active=True, stock__lte=5).order_by('stock', 'name')[:6],
        'recent_orders': Order.objects.select_related('user').prefetch_related('items').all()[:6],
        'recent_users': User.objects.select_related('profile').order_by('-date_joined')[:6],
    }
    return render(request, 'dashboard/home.html', context)


@staff_required
def product_list(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.select_related('category').order_by('-created_at')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
    return render(request, 'dashboard/products.html', {'products': products, 'query': query})


@staff_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        product = form.save()
        messages.success(request, f'{product.name} was added to the catalogue.')
        return redirect('management:products')
    return render(request, 'dashboard/product_form.html', {'form': form, 'page_title': 'Add product', 'submit_label': 'Add product'})


@staff_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{product.name} was updated.')
        return redirect('management:products')
    return render(request, 'dashboard/product_form.html', {'form': form, 'product': product, 'page_title': 'Edit product', 'submit_label': 'Save changes'})


@staff_required
@require_POST
def product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    try:
        product.delete()
    except ProtectedError:
        messages.error(request, 'This product is part of an order and cannot be deleted. Mark it unavailable instead.')
    else:
        messages.success(request, f'{product.name} was deleted.')
    return redirect('management:products')


@staff_required
def category_list(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        category = form.save()
        messages.success(request, f'{category.name} was added.')
        return redirect('management:categories')
    categories = Category.objects.annotate(product_count=Count('products')).order_by('name')
    return render(request, 'dashboard/categories.html', {'form': form, 'categories': categories})


@staff_required
@require_POST
def category_delete(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    try:
        category.delete()
    except ProtectedError:
        messages.error(request, 'A category with products cannot be removed. Move or delete its products first.')
    else:
        messages.success(request, f'{category.name} was deleted.')
    return redirect('management:categories')


@staff_required
def inventory_list(request):
    completed_statuses = [Order.Status.CONFIRMED, Order.Status.PROCESSING, Order.Status.SHIPPED, Order.Status.COMPLETED]
    products = Product.objects.select_related('category').annotate(
        sold=Coalesce(Sum('order_items__quantity', filter=Q(order_items__order__status__in=completed_statuses)), 0)
    ).order_by('stock', 'name')
    return render(request, 'dashboard/inventory.html', {'products': products})


@staff_required
@require_POST
@transaction.atomic
def inventory_update(request, product_id):
    product = get_object_or_404(Product.objects.select_for_update(), pk=product_id)
    form = InventoryForm(request.POST, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, f'Inventory for {product.name} was updated.')
    else:
        messages.error(request, 'Enter a valid, non-negative stock quantity.')
    return redirect('management:inventory')


@staff_required
def order_list(request):
    query = request.GET.get('q', '').strip()
    selected_status = request.GET.get('status', '').strip()
    orders = Order.objects.select_related('user', 'user__profile').prefetch_related('items').all()
    if query:
        orders = orders.filter(Q(number__icontains=query) | Q(user__email__icontains=query) | Q(user__profile__full_name__icontains=query))
    if selected_status in Order.Status.values:
        orders = orders.filter(status=selected_status)
    return render(request, 'dashboard/orders.html', {
        'orders': orders,
        'query': query,
        'selected_status': selected_status,
        'statuses': Order.Status.choices,
    })


@staff_required
def order_detail(request, number):
    order = get_object_or_404(
        Order.objects.select_related('user', 'user__profile').prefetch_related('items__product'),
        number=number,
    )
    form = OrderStatusForm(request.POST or None, instance=order)
    if request.method == 'POST' and form.is_valid():
        try:
            change_order_status(order, form.cleaned_data['status'])
        except CheckoutError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, f'Order {order.number} status was updated.')
        return redirect('management:order_detail', number=order.number)
    return render(request, 'dashboard/order_detail.html', {'order': order, 'form': form})


@staff_required
def user_list(request):
    query = request.GET.get('q', '').strip()
    users = User.objects.select_related('profile').annotate(order_count=Count('orders')).order_by('-date_joined')
    if query:
        users = users.filter(
            Q(email__icontains=query)
            | Q(username__icontains=query)
            | Q(profile__full_name__icontains=query)
            | Q(profile__phone_number__icontains=query)
        )
    return render(request, 'dashboard/users.html', {'users': users, 'query': query})
