from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def order_list(request):
    return render(request, 'orders/order_list.html')