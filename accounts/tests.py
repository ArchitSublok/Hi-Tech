from django.contrib.auth.models import User
from django.test import Client, TestCase


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
