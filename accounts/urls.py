from django.urls import path
from . import views

urlpatterns = [
    path('api/signup/', views.signup_api, name='signup_api'),
    path('api/login/', views.login_api, name='login_api'),
    path('logout/', views.logout_view, name='logout'),
]