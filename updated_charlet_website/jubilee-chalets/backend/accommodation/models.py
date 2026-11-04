from django.db import models
from django.utils.text import slugify


class RoomCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Room Categories'
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Lucide icon name')

    class Meta:
        verbose_name_plural = 'Amenities'
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(RoomCategory, on_delete=models.PROTECT, related_name='rooms')
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    max_adults = models.PositiveIntegerField(default=2)
    max_children = models.PositiveIntegerField(default=0)
    max_occupancy = models.PositiveIntegerField(default=2)
    bed_configuration = models.CharField(max_length=100, default='1 Double Bed')
    size_sqm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    floor = models.PositiveIntegerField(null=True, blank=True)
    price_per_night = models.DecimalField(max_digits=12, decimal_places=2)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']
        indexes = [models.Index(fields=['slug']), models.Index(fields=['is_active', 'is_available'])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.max_occupancy:
            self.max_occupancy = self.max_adults + self.max_children
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def primary_image(self):
        img = self.images.filter(is_primary=True).first() or self.images.first()
        return img.image.url if img else None


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_primary', 'display_order']

    def save(self, *args, **kwargs):
        # Ensure only one primary image per room
        if self.is_primary:
            RoomImage.objects.filter(room=self.room, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.room.name} - image {self.display_order}'
