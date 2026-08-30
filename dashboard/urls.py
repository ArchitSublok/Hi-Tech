from django.urls import path

from . import views

app_name = 'management'

urlpatterns = [
    path('login/', views.staff_login, name='login'),
    path('logout/', views.staff_logout, name='logout'),
    path('', views.dashboard_home, name='home'),
    path('products/', views.product_list, name='products'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('categories/', views.category_list, name='categories'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    path('inventory/', views.inventory_list, name='inventory'),
    path('inventory/<int:product_id>/', views.inventory_update, name='inventory_update'),
    path('orders/', views.order_list, name='orders'),
    path('orders/<str:number>/', views.order_detail, name='order_detail'),
    path('coupons/', views.coupon_list, name='coupons'),
    path('coupons/new/', views.coupon_create, name='coupon_create'),
    path('coupons/<int:coupon_id>/edit/', views.coupon_edit, name='coupon_edit'),
    path('coupons/<int:coupon_id>/delete/', views.coupon_delete, name='coupon_delete'),
    path('coupons/<int:coupon_id>/toggle/', views.coupon_toggle, name='coupon_toggle'),
    path('users/', views.user_list, name='users'),
]