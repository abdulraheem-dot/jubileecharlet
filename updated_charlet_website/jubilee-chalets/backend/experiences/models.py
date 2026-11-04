from django.db import models
from django.utils.text import slugify


class Experience(models.Model):
    CATEGORIES = [
        ('recreation', 'Recreation'),
        ('swimming', 'Swimming'),
        ('dining', 'Dining'),
        ('family', 'Family'),
        ('corporate', 'Corporate Retreats'),
        ('events', 'Events'),
        ('outdoor', 'Outdoor'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='experiences/', null=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORIES, default='other')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_free = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
