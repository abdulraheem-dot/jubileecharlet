from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )

    def test_register(self):
        """New user can register."""
        url = reverse('auth-register')
        resp = self.client.post(url, {
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass12345',
            'password_confirm': 'newpass12345',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', resp.data)
        self.assertIn('access', resp.data['tokens'])

    def test_login_valid(self):
        """Login with valid credentials returns tokens."""
        url = reverse('auth-login')
        resp = self.client.post(url, {
            'email': 'test@example.com',
            'password': 'testpass123',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', resp.data)

    def test_login_invalid(self):
        """Login with wrong password fails."""
        url = reverse('auth-login')
        resp = self.client.post(url, {
            'email': 'test@example.com',
            'password': 'wrongpassword',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_rejected(self):
        """Registration with existing email fails."""
        url = reverse('auth-register')
        resp = self.client.post(url, {
            'email': 'test@example.com',
            'first_name': 'Dup',
            'last_name': 'User',
            'password': 'newpass12345',
            'password_confirm': 'newpass12345',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_mismatch(self):
        """Registration with mismatched passwords fails."""
        url = reverse('auth-register')
        resp = self.client.post(url, {
            'email': 'mismatch@example.com',
            'first_name': 'Mis',
            'last_name': 'User',
            'password': 'newpass12345',
            'password_confirm': 'different12345',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_requires_auth(self):
        """Profile endpoint requires authentication."""
        url = reverse('auth-profile')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_with_auth(self):
        """Authenticated user can get their profile."""
        self.client.force_authenticate(user=self.user)
        url = reverse('auth-profile')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['email'], 'test@example.com')

    def test_change_password(self):
        """User can change their password."""
        self.client.force_authenticate(user=self.user)
        url = reverse('auth-change-password')
        resp = self.client.post(url, {
            'current_password': 'testpass123',
            'new_password': 'newpass12345',
            'new_password_confirm': 'newpass12345',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass12345'))
