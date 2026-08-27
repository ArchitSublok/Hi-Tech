from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models, transaction

phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{7,15}$',
    message="Enter a valid phone number (7-15 digits, optional leading +)."
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, validators=[phone_validator])
    is_dealer = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.user.email})"


class DealerProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dealer_profile')
    company_name = models.CharField(max_length=200)
    gstin_or_tax_id = models.CharField(max_length=50)
    business_address = models.TextField()
    phone_number = models.CharField(max_length=20, validators=[phone_validator])
    verification_status = models.CharField(
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['verification_status', '-created_at']

    def __str__(self):
        return f"{self.company_name} ({self.get_verification_status_display()})"

    @transaction.atomic
    def approve(self):
        """Activate the dealer and keep the linked profile in sync."""
        self.verification_status = self.VerificationStatus.APPROVED
        self.save(update_fields=['verification_status', 'updated_at'])

        self.user.is_active = True
        self.user.save(update_fields=['is_active'])
        profile, _ = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'full_name': self.user.get_full_name() or self.user.username,
                'phone_number': self.phone_number,
                'is_dealer': True,
                'is_approved': True,
            },
        )
        if not profile.is_dealer or not profile.is_approved:
            profile.is_dealer = True
            profile.is_approved = True
            profile.save(update_fields=['is_dealer', 'is_approved', 'updated_at'])

    @transaction.atomic
    def reject(self):
        """Keep a rejected dealer account inactive and inaccessible."""
        self.verification_status = self.VerificationStatus.REJECTED
        self.save(update_fields=['verification_status', 'updated_at'])

        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
        profile, _ = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'full_name': self.user.get_full_name() or self.user.username,
                'phone_number': self.phone_number,
                'is_dealer': True,
                'is_approved': False,
            },
        )
        if not profile.is_dealer or profile.is_approved:
            profile.is_dealer = True
            profile.is_approved = False
            profile.save(update_fields=['is_dealer', 'is_approved', 'updated_at'])
