import json
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from .forms import SignUpForm, LoginForm
from .models import UserProfile


def _request_data(request):
    """Accept the existing JSON clients as well as normal CSRF-protected forms."""
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body), None
        except json.JSONDecodeError:
            return None, JsonResponse(
                {'success': False, 'errors': {'__all__': ['Invalid request.']}},
                status=400,
            )
    return request.POST, None


@require_POST
def signup_api(request):
    data, error_response = _request_data(request)
    if error_response:
        return error_response

    form = SignUpForm(data)
    if form.is_valid():
        email = form.cleaned_data['email']
        full_name = form.cleaned_data['full_name']
        phone_number = form.cleaned_data['phone_number']
        password = form.cleaned_data['password1']

        base_username = email.split('@')[0][:140]
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{suffix}"
            suffix += 1

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, full_name=full_name, phone_number=phone_number)

        auth_login(request, user, backend='accounts.backends.EmailBackend')
        return JsonResponse({'success': True, 'message': f"Welcome, {full_name}!"})

    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def login_api(request):
    data, error_response = _request_data(request)
    if error_response:
        return error_response

    form = LoginForm(data)
    if form.is_valid():
        user = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data['password'])
        if user is not None:
            auth_login(request, user, backend='accounts.backends.EmailBackend')
            return JsonResponse({'success': True, 'message': "Welcome back!"})
        return JsonResponse({'success': False, 'errors': {'__all__': ['Incorrect email or password.']}}, status=400)

    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


def logout_view(request):
    auth_logout(request)
    return redirect('home')
