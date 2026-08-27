from django import forms

from .models import Address


class AddressForm(forms.ModelForm):
    """Validate a new delivery address before it is stored or used for an order."""

    class Meta:
        model = Address
        fields = (
            'recipient_name',
            'phone',
            'street_address',
            'area_locality',
            'city',
            'state',
            'postal_code',
            'latitude',
            'longitude',
        )

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if len(phone) < 7:
            raise forms.ValidationError('Enter a valid phone number.')
        return phone
