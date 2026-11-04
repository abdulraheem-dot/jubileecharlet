from django.db import models


class WebsiteSettings(models.Model):
    """
    Singleton model — only one row should exist.
    Manage all editable site-wide settings from Django Admin.
    """
    site_name = models.CharField(max_length=100, default='Jubilee Chalets Epe')
    tagline = models.CharField(max_length=300, blank=True)
    phone_primary = models.CharField(max_length=20, blank=True)
    phone_secondary = models.CharField(max_length=20, blank=True)
    email_primary = models.EmailField(blank=True)
    email_bookings = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, default='Epe')
    state = models.CharField(max_length=100, default='Lagos State')
    country = models.CharField(max_length=100, default='Nigeria')
    whatsapp_number = models.CharField(max_length=20, blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    check_in_time = models.CharField(max_length=10, default='14:00')
    check_out_time = models.CharField(max_length=10, default='12:00')
    google_maps_embed_url = models.URLField(max_length=1000, blank=True)
    cancellation_policy = models.TextField(blank=True)
    privacy_policy = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Website Settings'
        verbose_name_plural = 'Website Settings'

    def __str__(self):
        return f'{self.site_name} — Settings'

    def save(self, *args, **kwargs):
        # Enforce singleton pattern
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
