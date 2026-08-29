from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('upi/<str:order_number>/', views.upi_payment, name='upi_payment'),
]