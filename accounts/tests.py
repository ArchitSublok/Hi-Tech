from django.contrib.auth.models import User
from django.test import Client, TestCase

from .models import DealerProfile


class AuthenticationApiTests(TestCase):
    def test_login_accepts_csrf_protected_form_data(self):
        User.objects.create_user('admin', 'admin@example.com', 'secure-password-123', is_staff=True)
        client = Client(enforce_csrf_checks=True, HTTP_HOST='localhost')
        client.get('/')
        token = client.cookies['csrftoken'].value

        response = client.post(
            '/accounts/api/login/',
            {
                'email': 'admin@example.com',
                'password': 'secure-password-123',
                'csrfmiddlewaretoken': token,
            },
            HTTP_REFERER='http://localhost/',
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Welcome back!'})

    def test_customer_signup_is_active_and_logged_in(self):
        response = self.client.post('/accounts/api/signup/', {
            'account_type': 'customer',
            'first_name': 'Asha',
            'last_name': 'Sharma',
            'email': 'asha@example.com',
            'phone_number': '9876543210',
            'password1': 'secure-password-123',
            'password2': 'secure-password-123',
        })

        user = User.objects.get(email='asha@example.com')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user.is_active)
        self.assertFalse(user.profile.is_dealer)
        self.assertTrue(user.profile.is_approved)
        self.assertEqual(self.client.session.get('_auth_user_id'), str(user.id))

    def test_dealer_signup_requires_approval_then_can_be_activated(self):
        response = self.client.post('/accounts/api/signup/', {
            'account_type': 'dealer',
            'first_name': 'Dev',
            'last_name': 'Patel',
            'email': 'dev@example.com',
            'phone_number': '9876543210',
            'password1': 'secure-password-123',
            'password2': 'secure-password-123',
            'company_name': 'Dev Components Pvt Ltd',
            'gstin_or_tax_id': '27ABCDE1234F1Z5',
            'business_address': '42 Industrial Estate, Pune',
        })

        user = User.objects.get(email='dev@example.com')
        dealer = DealerProfile.objects.get(user=user)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(user.is_active)
        self.assertFalse(user.profile.is_approved)
        self.assertEqual(dealer.verification_status, DealerProfile.VerificationStatus.PENDING)
        self.assertNotIn('_auth_user_id', self.client.session)

        dealer.approve()
        user.refresh_from_db()
        user.profile.refresh_from_db()
        dealer.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.profile.is_approved)
        self.assertEqual(dealer.verification_status, DealerProfile.VerificationStatus.APPROVED)
