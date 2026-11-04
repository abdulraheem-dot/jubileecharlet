from django.db import models


class GalleryImage(models.Model):
    CATEGORIES = [
        ('rooms', 'Rooms'),
        ('dining', 'Dining'),
        ('outdoor', 'Outdoor'),
        ('recreation', 'Recreation'),
        ('events', 'Events'),
        ('general', 'General'),
    ]

    image = models.ImageField(upload_to='gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=300, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORIES, default='general')
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'display_order']

    def __str__(self):
        return self.alt_text or f'Gallery Image #{self.pk}'
