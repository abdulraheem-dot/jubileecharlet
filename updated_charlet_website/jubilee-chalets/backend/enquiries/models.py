from django.db import models


class ContactEnquiry(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Contact Enquiries'

    def __str__(self):
        return f'{self.subject} — {self.full_name}'


class Testimonial(models.Model):
    guest_name = models.CharField(max_length=200)
    review_text = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    visit_date = models.DateField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.guest_name} — {self.rating}★'


class FAQ(models.Model):
    CATEGORIES = [
        ('booking', 'Booking'),
        ('accommodation', 'Accommodation'),
        ('payment', 'Payment'),
        ('facilities', 'Facilities'),
        ('general', 'General'),
    ]

    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORIES, default='general')
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'display_order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    consent = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email
