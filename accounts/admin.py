from django.contrib import admin, messages
from django.core.mail import send_mail

from .models import DealerProfile, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'is_dealer', 'is_approved', 'user_email', 'created_at')
    search_fields = ('full_name', 'phone_number', 'user__email')
    list_filter = ('is_dealer', 'is_approved')

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'


@admin.register(DealerProfile)
class DealerProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'verification_status', 'created_at')
    list_filter = ('verification_status',)
    search_fields = ('company_name', 'gstin_or_tax_id', 'user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    actions = ('approve_dealers', 'reject_dealers')

    @admin.action(description='Approve selected dealer applications')
    def approve_dealers(self, request, queryset):
        approved = 0
        for dealer in queryset.exclude(
            verification_status=DealerProfile.VerificationStatus.APPROVED
        ).select_related('user'):
            dealer.approve()
            send_mail(
                'Your Hi-Tech dealer account is approved',
                'Your dealer account has been approved and is now active. You can log in to continue.',
                None,
                [dealer.user.email],
                fail_silently=True,
            )
            approved += 1
        self.message_user(request, f"Approved {approved} dealer account(s).", level=messages.SUCCESS)

    @admin.action(description='Reject selected dealer applications')
    def reject_dealers(self, request, queryset):
        rejected = 0
        for dealer in queryset.exclude(
            verification_status=DealerProfile.VerificationStatus.REJECTED
        ).select_related('user'):
            dealer.reject()
            rejected += 1
        self.message_user(request, f"Rejected {rejected} dealer account(s).", level=messages.WARNING)
