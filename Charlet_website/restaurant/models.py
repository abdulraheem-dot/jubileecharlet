from django.db import models
from django.conf import settings


class FoodCategory(models.Model):
    name  = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)
    def __str__(self): return self.name
    class Meta: ordering = ['order', 'name']


class MenuItem(models.Model):
    category    = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='items')
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    photo       = models.ImageField(upload_to='menu/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_vegetarian = models.BooleanField(default=False)

    def __str__(self): return f"{self.name} — ₦{self.price:,.0f}"
    class Meta: ordering = ['category', 'name']


class OrderStatus(models.TextChoices):
    NEW       = 'NEW',       'New'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    PREPARING = 'PREPARING', 'Preparing'
    READY     = 'READY',     'Ready'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'


class FoodOrder(models.Model):
    room        = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, related_name='food_orders')
    guest       = models.ForeignKey('guests.Guest', on_delete=models.SET_NULL, null=True, blank=True)
    status      = models.CharField(max_length=15, choices=OrderStatus.choices, default=OrderStatus.NEW)
    special_instructions = models.TextField(blank=True)
    handled_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    def __str__(self): return f"Order #{self.pk} — Room {self.room.number}"
    class Meta: ordering = ['-created_at']


class FoodOrderItem(models.Model):
    order    = models.ForeignKey(FoodOrder, on_delete=models.CASCADE, related_name='items')
    item     = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    notes    = models.CharField(max_length=200, blank=True)

    @property
    def subtotal(self): return self.item.price * self.quantity

    def __str__(self): return f"{self.quantity}x {self.item.name}"
