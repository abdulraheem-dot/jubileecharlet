"""
rooms/models.py

Room and RoomType models for Jubilee Chalets.

CONCEPTS COVERED:
- ForeignKey: many rooms → one room type (many-to-one relationship)
- ImageField: stores room photos
- Choices on model fields
- QR code generation using the qrcode library
- __str__ and Meta class
- Model methods that do hotel-specific logic
"""

from django.db import models
from django.utils import timezone
import qrcode
import qrcode.image.svg
from io import BytesIO
from django.core.files import File
import os


# ---------------------------------------------------------------------------
# ROOM TYPE
# ---------------------------------------------------------------------------
class RoomType(models.Model):
    """
    Defines types of rooms: Standard, Deluxe, Suite, Conference, etc.

    WHY A SEPARATE MODEL?
    Because many rooms share the same type.
    Instead of storing 'Standard Room, ₦45,000/night, 1 king bed'
    on every single room record, we store it once in RoomType
    and link each room to it.

    This is the "Don't Repeat Yourself" (DRY) principle in databases.
    """
    name         = models.CharField(max_length=100, unique=True)
    description  = models.TextField(blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_occupancy   = models.PositiveIntegerField(default=2)
    bed_type        = models.CharField(max_length=50, blank=True, help_text="e.g. King, Twin, Double")
    has_ac          = models.BooleanField(default=True)
    has_tv          = models.BooleanField(default=True)
    has_wifi        = models.BooleanField(default=True)
    has_minibar     = models.BooleanField(default=False)
    photo           = models.ImageField(upload_to='room_types/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — ₦{self.price_per_night:,.0f}/night"

    class Meta:
        ordering = ['name']
        verbose_name = 'Room Type'
        verbose_name_plural = 'Room Types'


# ---------------------------------------------------------------------------
# ROOM STATUS CHOICES
# ---------------------------------------------------------------------------
class RoomStatus(models.TextChoices):
    AVAILABLE     = 'AVAILABLE',     'Available'
    OCCUPIED      = 'OCCUPIED',      'Occupied'
    RESERVED      = 'RESERVED',      'Reserved'
    CLEANING      = 'CLEANING',      'Cleaning'
    MAINTENANCE   = 'MAINTENANCE',   'Under Maintenance'
    OUT_OF_SERVICE = 'OUT_OF_SERVICE','Out of Service'


# ---------------------------------------------------------------------------
# HOUSEKEEPING STATUS CHOICES
# ---------------------------------------------------------------------------
class HousekeepingStatus(models.TextChoices):
    DIRTY      = 'DIRTY',      'Dirty'
    CLEANING   = 'CLEANING',   'Being Cleaned'
    CLEANED    = 'CLEANED',    'Cleaned'
    INSPECTION = 'INSPECTION', 'Awaiting Inspection'
    READY      = 'READY',      'Ready'


# ---------------------------------------------------------------------------
# ROOM
# ---------------------------------------------------------------------------
class Room(models.Model):
    """
    Represents a single physical hotel room.

    ForeignKey to RoomType:
    - 'on_delete=models.PROTECT' means Django will NOT allow you to delete
      a RoomType if any rooms are still using it.
      This protects your data from accidental deletion.
    - 'related_name='rooms'' means from a RoomType instance you can do:
        room_type.rooms.all()   → all rooms of this type
        room_type.rooms.count() → how many rooms of this type exist

    UNIQUE TOGETHER:
    We could have Room 101, 201, 301 etc.
    room_number alone must be unique across all floors.
    """
    number      = models.CharField(max_length=10, unique=True, help_text="e.g. 101, 202, Suite-A")
    floor       = models.PositiveIntegerField(default=1)
    room_type   = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        related_name='rooms'
    )
    status      = models.CharField(
        max_length=20,
        choices=RoomStatus.choices,
        default=RoomStatus.AVAILABLE
    )
    housekeeping_status = models.CharField(
        max_length=20,
        choices=HousekeepingStatus.choices,
        default=HousekeepingStatus.READY
    )

    # notes visible only to staff (e.g. 'AC unit needs attention')
    internal_notes = models.TextField(blank=True)

    # QR code image generated automatically
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    # Unique token used in the QR code URL — harder to guess than room number
    access_token = models.CharField(max_length=64, unique=True, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Room {self.number} ({self.room_type.name})"

    def get_status_badge_class(self):
        """Returns a Bootstrap colour class for the room's current status."""
        badge_map = {
            RoomStatus.AVAILABLE:      'bg-success',
            RoomStatus.OCCUPIED:       'bg-primary',
            RoomStatus.RESERVED:       'bg-info text-dark',
            RoomStatus.CLEANING:       'bg-warning text-dark',
            RoomStatus.MAINTENANCE:    'bg-danger',
            RoomStatus.OUT_OF_SERVICE: 'bg-secondary',
        }
        return badge_map.get(self.status, 'bg-secondary')

    def get_hk_badge_class(self):
        badge_map = {
            HousekeepingStatus.DIRTY:      'bg-danger',
            HousekeepingStatus.CLEANING:   'bg-warning text-dark',
            HousekeepingStatus.CLEANED:    'bg-info text-dark',
            HousekeepingStatus.INSPECTION: 'bg-primary',
            HousekeepingStatus.READY:      'bg-success',
        }
        return badge_map.get(self.housekeeping_status, 'bg-secondary')

    @property
    def is_available(self):
        return self.status == RoomStatus.AVAILABLE

    @property
    def current_guest(self):
        """Returns the active guest checked into this room, or None."""
        from guests.models import GuestStay
        stay = GuestStay.objects.filter(room=self, is_active=True).select_related('guest').first()
        return stay.guest if stay else None

    def generate_qr_code(self, base_url='http://localhost:8000'):
        """
        Generates a QR code PNG image for this room and saves it to media/qrcodes/.

        The QR code URL points to the guest portal for this specific room,
        using the room's access_token (not the room number) for security.
        Guests scanning the QR code can only see THEIR room's services.
        """
        url = f"{base_url}/guests/room/{self.access_token}/"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#1a2332", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f"room_{self.number}_qr.png"
        self.qr_code.save(filename, File(buffer), save=False)

    def save(self, *args, **kwargs):
        """
        Override save() to:
        1. Auto-generate an access_token if this is a new room
        2. Auto-generate a QR code if one doesn't exist yet

        super().save() calls Django's default save behaviour.
        We add our logic BEFORE or AFTER calling super().
        """
        import secrets
        if not self.access_token:
            # Generate a secure random 32-character hex token
            # This is what appears in the QR code URL
            self.access_token = secrets.token_hex(16)

        # Save the record first (so we have a PK and can save the image)
        super().save(*args, **kwargs)

        # Generate QR code if it doesn't exist yet
        if not self.qr_code:
            self.generate_qr_code()
            # Save again to write the qr_code field
            Room.objects.filter(pk=self.pk).update(qr_code=self.qr_code)

    class Meta:
        ordering = ['floor', 'number']
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
