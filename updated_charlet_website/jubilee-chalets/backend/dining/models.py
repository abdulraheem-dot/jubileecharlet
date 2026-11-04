from django.db import models


class MenuCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Menu Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, on_delete=models.PROTECT, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    allergens = models.CharField(max_length=300, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'display_order', 'name']

    def __str__(self):
        return f'{self.category.name} — {self.name}'
