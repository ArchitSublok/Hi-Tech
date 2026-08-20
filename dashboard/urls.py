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
    path('users/', views.user_list, name='users'),
]
