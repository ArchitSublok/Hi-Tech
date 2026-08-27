import json

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .forms import LoginForm, SignUpForm
from .models import DealerProfile, UserProfile


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
        is_dealer = form.cleaned_data['account_type'] == SignUpForm.AccountType.DEALER

        base_username = email.split('@')[0][:140]
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{suffix}"
            suffix += 1

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                is_active=not is_dealer,
            )
            UserProfile.objects.create(
                user=user,
                full_name=full_name,
                phone_number=phone_number,
                is_dealer=is_dealer,
                is_approved=not is_dealer,
            )
            if is_dealer:
                dealer_profile = DealerProfile.objects.create(
                    user=user,
                    company_name=form.cleaned_data['company_name'].strip(),
                    gstin_or_tax_id=form.cleaned_data['gstin_or_tax_id'].strip(),
                    business_address=form.cleaned_data['business_address'].strip(),
                    phone_number=phone_number,
                )

        if is_dealer:
            mail_admins(
                subject=f"Dealer approval requested: {dealer_profile.company_name}",
                message=(
                    f"{full_name} ({email}) submitted a dealer application for "
                    f"{dealer_profile.company_name}. Review it in Django admin."
                ),
                fail_silently=True,
            )
            return JsonResponse({
                'success': True,
                'pending_approval': True,
                'message': 'Your dealer application was submitted for approval.',
            })

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
