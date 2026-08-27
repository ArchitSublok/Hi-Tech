from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{7,15}$',
    message="Enter a valid phone number."
)


class SignUpForm(forms.Form):
    class AccountType(models.TextChoices):
        CUSTOMER = 'customer', 'Regular Customer'
        DEALER = 'dealer', 'Dealer / B2B Partner'

    account_type = forms.ChoiceField(choices=AccountType.choices, initial=AccountType.CUSTOMER)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    # Kept for API compatibility with clients that used the original field.
    full_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20, validators=[phone_validator])
    password1 = forms.CharField(min_length=8)
    password2 = forms.CharField()
    company_name = forms.CharField(max_length=200, required=False)
    gstin_or_tax_id = forms.CharField(max_length=50, required=False)
    business_address = forms.CharField(widget=forms.Textarea, required=False)

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Passwords do not match.")

        first_name = cleaned_data.get('first_name', '').strip()
        last_name = cleaned_data.get('last_name', '').strip()
        full_name = cleaned_data.get('full_name', '').strip()
        if not first_name and full_name:
            name_parts = full_name.split(maxsplit=1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) == 2 else ''
        if not first_name:
            self.add_error('first_name', "Enter your first name.")
        cleaned_data['first_name'] = first_name
        cleaned_data['last_name'] = last_name
        cleaned_data['full_name'] = ' '.join(part for part in [first_name, last_name] if part)

        if cleaned_data.get('account_type') == self.AccountType.DEALER:
            for field_name in ('company_name', 'gstin_or_tax_id', 'business_address'):
                if not cleaned_data.get(field_name, '').strip():
                    self.add_error(field_name, "This field is required for dealer registration.")
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
