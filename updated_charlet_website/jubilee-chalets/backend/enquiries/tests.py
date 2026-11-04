from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import ContactEnquiry, NewsletterSubscription, FAQ


class ContactEnquiryTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_submit_contact_form(self):
        """Valid contact form submission creates an enquiry."""
        url = reverse('contact')
        resp = self.client.post(url, {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Booking question',
            'message': 'I would like to know more about your rooms.',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ContactEnquiry.objects.filter(email='john@example.com').exists())

    def test_contact_form_validation(self):
        """Missing required fields return 400."""
        url = reverse('contact')
        resp = self.client.post(url, {
            'full_name': 'John',
            'email': 'invalid-email',
            'subject': 'Hi',
            'message': 'short',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class NewsletterTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_subscribe(self):
        """Valid subscription creates a record."""
        url = reverse('newsletter-subscribe')
        resp = self.client.post(url, {
            'email': 'subscriber@example.com',
            'consent': True,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(NewsletterSubscription.objects.filter(email='subscriber@example.com').exists())

    def test_subscribe_requires_consent(self):
        """Subscription without consent fails."""
        url = reverse('newsletter-subscribe')
        resp = self.client.post(url, {
            'email': 'noconsent@example.com',
            'consent': False,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_idempotent(self):
        """Subscribing same email twice doesn't create duplicates."""
        url = reverse('newsletter-subscribe')
        self.client.post(url, {'email': 'dup@example.com', 'consent': True}, format='json')
        self.client.post(url, {'email': 'dup@example.com', 'consent': True}, format='json')
        self.assertEqual(NewsletterSubscription.objects.filter(email='dup@example.com').count(), 1)


class FAQTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        FAQ.objects.create(question='What time is check-in?', answer='2 PM', category='booking')

    def test_list_faqs(self):
        """FAQ list returns active FAQs."""
        url = reverse('faqs')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['question'], 'What time is check-in?')
