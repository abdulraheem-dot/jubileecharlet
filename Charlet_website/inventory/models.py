from django.db import models
from django.conf import settings


class InventoryItem(models.Model):
    class ItemDepartment(models.TextChoices):
        HOUSEKEEPING = 'HOUSEKEEPING', 'Housekeeping'
        RESTAURANT   = 'RESTAURANT',   'Restaurant'
        MAINTENANCE  = 'MAINTENANCE',  'Maintenance'
        LAUNDRY      = 'LAUNDRY',      'Laundry'
        RECEPTION    = 'RECEPTION',    'Reception'
        GENERAL      = 'GENERAL',      'General'

    name            = models.CharField(max_length=200)
    department      = models.CharField(max_length=20, choices=ItemDepartment.choices)
    quantity        = models.PositiveIntegerField(default=0)
    unit            = models.CharField(max_length=30, default='units', help_text="e.g. pieces, kg, litres")
    minimum_level   = models.PositiveIntegerField(default=10)
    description     = models.TextField(blank=True)
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    updated_at      = models.DateTimeField(auto_now=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_level

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

    class Meta:
        ordering = ['department', 'name']
