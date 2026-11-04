"""
requests_app/models.py

The core of the hotel management system — Service Requests.

CONCEPTS COVERED:
- Multiple choice fields on a single model
- ForeignKey with null=True (optional relationships)
- auto_now_add vs auto_now
- Model methods and properties
- __str__, Meta class, ordering
- The AuditLog model for tracking staff actions

QUERYSETS (explained as used):
ServiceRequest.objects.all()               → all requests
ServiceRequest.objects.filter(status='NEW')→ only new requests
ServiceRequest.objects.filter(            → multiple filters (AND logic)
    room__number='204',
    priority='URGENT'
)
ServiceRequest.objects.select_related(     → fetch linked records in one query
    'room', 'guest', 'assigned_to'
)
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


# ---------------------------------------------------------------------------
# CHOICES
# ---------------------------------------------------------------------------

class RequestStatus(models.TextChoices):
    NEW               = 'NEW',              'New'
    ACKNOWLEDGED      = 'ACKNOWLEDGED',     'Acknowledged'
    ASSIGNED          = 'ASSIGNED',         'Assigned'
    IN_PROGRESS       = 'IN_PROGRESS',      'In Progress'
    WAITING_FOR_GUEST = 'WAITING_FOR_GUEST','Waiting for Guest'
    COMPLETED         = 'COMPLETED',        'Completed'
    CANCELLED         = 'CANCELLED',        'Cancelled'


class RequestPriority(models.TextChoices):
    LOW    = 'LOW',    'Low'
    NORMAL = 'NORMAL', 'Normal'
    HIGH   = 'HIGH',   'High'
    URGENT = 'URGENT', 'Urgent'


class RequestCategory(models.TextChoices):
    MAINTENANCE        = 'MAINTENANCE',        'Maintenance'
    HOUSEKEEPING       = 'HOUSEKEEPING',       'Housekeeping'
    FOOD_BEVERAGE      = 'FOOD_BEVERAGE',      'Food & Beverage'
    RECEPTION          = 'RECEPTION',          'Reception'
    LAUNDRY            = 'LAUNDRY',            'Laundry'
    TRANSPORTATION     = 'TRANSPORTATION',     'Transportation'
    ROOM_SUPPLIES      = 'ROOM_SUPPLIES',      'Room Supplies'
    TECHNICAL_SUPPORT  = 'TECHNICAL_SUPPORT',  'Technical Support'
    SECURITY           = 'SECURITY',           'Security'
    EMERGENCY          = 'EMERGENCY',          'Emergency'
    OTHER              = 'OTHER',              'Other'


class RequestDepartment(models.TextChoices):
    RECEPTION      = 'RECEPTION',      'Reception'
    HOUSEKEEPING   = 'HOUSEKEEPING',   'Housekeeping'
    MAINTENANCE    = 'MAINTENANCE',    'Maintenance'
    RESTAURANT     = 'RESTAURANT',     'Restaurant'
    LAUNDRY        = 'LAUNDRY',        'Laundry'
    SECURITY       = 'SECURITY',       'Security'
    MANAGEMENT     = 'MANAGEMENT',     'Management'
    TRANSPORTATION = 'TRANSPORTATION', 'Transportation'


# Mapping from category → department (used for auto-routing)
CATEGORY_DEPARTMENT_MAP = {
    RequestCategory.MAINTENANCE:       RequestDepartment.MAINTENANCE,
    RequestCategory.HOUSEKEEPING:      RequestDepartment.HOUSEKEEPING,
    RequestCategory.FOOD_BEVERAGE:     RequestDepartment.RESTAURANT,
    RequestCategory.RECEPTION:         RequestDepartment.RECEPTION,
    RequestCategory.LAUNDRY:           RequestDepartment.LAUNDRY,
    RequestCategory.TRANSPORTATION:    RequestDepartment.TRANSPORTATION,
    RequestCategory.ROOM_SUPPLIES:     RequestDepartment.HOUSEKEEPING,
    RequestCategory.TECHNICAL_SUPPORT: RequestDepartment.MAINTENANCE,
    RequestCategory.SECURITY:          RequestDepartment.SECURITY,
    RequestCategory.EMERGENCY:         RequestDepartment.SECURITY,
    RequestCategory.OTHER:             RequestDepartment.RECEPTION,
}

# Quick-service button presets (category, priority, default title)
QUICK_SERVICE_PRESETS = {
    'call_reception':    (RequestCategory.RECEPTION,      RequestPriority.NORMAL, 'Call Reception'),
    'ac_problem':        (RequestCategory.MAINTENANCE,    RequestPriority.HIGH,   'Air Conditioning Problem'),
    'maintenance':       (RequestCategory.MAINTENANCE,    RequestPriority.NORMAL, 'Maintenance Request'),
    'request_blanket':   (RequestCategory.ROOM_SUPPLIES,  RequestPriority.LOW,    'Request Blanket'),
    'request_toiletries':(RequestCategory.ROOM_SUPPLIES,  RequestPriority.LOW,    'Request Toiletries'),
    'room_cleaning':     (RequestCategory.HOUSEKEEPING,   RequestPriority.NORMAL, 'Request Room Cleaning'),
    'request_water':     (RequestCategory.ROOM_SUPPLIES,  RequestPriority.LOW,    'Request Water'),
    'order_food':        (RequestCategory.FOOD_BEVERAGE,  RequestPriority.NORMAL, 'Food Order'),
    'room_service':      (RequestCategory.FOOD_BEVERAGE,  RequestPriority.NORMAL, 'Room Service'),
    'laundry':           (RequestCategory.LAUNDRY,        RequestPriority.NORMAL, 'Laundry Request'),
    'transportation':    (RequestCategory.TRANSPORTATION, RequestPriority.NORMAL, 'Transport Request'),
    'general_assistance':(RequestCategory.RECEPTION,      RequestPriority.NORMAL, 'General Assistance'),
    'contact_reception': (RequestCategory.RECEPTION,      RequestPriority.NORMAL, 'Contact Reception'),
    'emergency':         (RequestCategory.EMERGENCY,      RequestPriority.URGENT, 'EMERGENCY'),
}


# ---------------------------------------------------------------------------
# SERVICE REQUEST
# ---------------------------------------------------------------------------
class ServiceRequest(models.Model):
    """
    The central model of the system.
    Tracks everything about a guest's service request from creation to completion.

    RELATIONSHIPS:
    - room:        ForeignKey → which room the request comes from
    - guest:       ForeignKey (nullable) → who made the request
    - assigned_to: ForeignKey (nullable) → which staff member is handling it
    - created_by:  ForeignKey (nullable) → staff who created it on guest's behalf

    NULLABLE FOREIGNKEYS (null=True, blank=True):
    A request might come from an anonymous QR scan (no guest login),
    so guest can be null. assigned_to starts null until staff accepts.
    """

    # Auto-incrementing request number (separate from Django's pk for display)
    request_number = models.CharField(max_length=20, unique=True, blank=True)

    room    = models.ForeignKey(
        'rooms.Room',
        on_delete=models.CASCADE,
        related_name='service_requests'
    )
    guest   = models.ForeignKey(
        'guests.Guest',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='requests'
    )

    # Category and department
    category   = models.CharField(max_length=30, choices=RequestCategory.choices)
    department = models.CharField(
        max_length=20,
        choices=RequestDepartment.choices,
        blank=True,
        help_text="Auto-set based on category; can be overridden"
    )

    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Priority
    priority = models.CharField(
        max_length=10,
        choices=RequestPriority.choices,
        default=RequestPriority.NORMAL
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.NEW
    )

    # Staff handling this request
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_requests'
    )

    # Who created this request (could be reception creating on guest's behalf)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_requests'
    )

    # Staff response / notes
    staff_response = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True, help_text="Not visible to guest")

    # Timestamps
    created_at    = models.DateTimeField(auto_now_add=True)  # Set once on creation
    updated_at    = models.DateTimeField(auto_now=True)       # Updated every save
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    assigned_at   = models.DateTimeField(null=True, blank=True)
    completed_at  = models.DateTimeField(null=True, blank=True)

    # Has the guest been notified of completion?
    guest_notified = models.BooleanField(default=False)

    # Escalation tracking
    reminder_sent     = models.BooleanField(default=False)
    escalated         = models.BooleanField(default=False)

    def __str__(self):
        return f"#{self.request_number} — {self.title} (Room {self.room.number})"

    # -----------------------------------------------------------------------
    # SAVE OVERRIDE — auto-set request_number and department
    # -----------------------------------------------------------------------
    def save(self, *args, **kwargs):
        # Auto-set department from category if not already set
        if not self.department and self.category:
            self.department = CATEGORY_DEPARTMENT_MAP.get(self.category, RequestDepartment.RECEPTION)

        # Auto-generate request number AFTER first save (when we have a pk)
        is_new = not self.pk
        super().save(*args, **kwargs)

        if is_new and not self.request_number:
            # Format: JC-2024-00042
            year = timezone.now().year
            self.request_number = f"JC-{year}-{self.pk:05d}"
            ServiceRequest.objects.filter(pk=self.pk).update(request_number=self.request_number)

    # -----------------------------------------------------------------------
    # STATUS TRANSITION METHODS
    # -----------------------------------------------------------------------
    def acknowledge(self, staff_user):
        """Reception acknowledges the request."""
        self.status = RequestStatus.ACKNOWLEDGED
        self.acknowledged_at = timezone.now()
        self.save()
        AuditLog.log(staff_user, 'ACKNOWLEDGED', self, f"Request acknowledged")

    def assign(self, staff_user, assigned_staff):
        """Assign the request to a specific staff member."""
        self.assigned_to = assigned_staff
        self.status      = RequestStatus.ASSIGNED
        self.assigned_at = timezone.now()
        self.save()
        AuditLog.log(
            staff_user, 'ASSIGNED', self,
            f"Assigned to {assigned_staff.get_full_name()}"
        )

    def start_progress(self, staff_user):
        self.status = RequestStatus.IN_PROGRESS
        self.save()
        AuditLog.log(staff_user, 'STARTED', self, "Work started")

    def complete(self, staff_user, response=''):
        self.status       = RequestStatus.COMPLETED
        self.completed_at = timezone.now()
        if response:
            self.staff_response = response
        self.save()
        AuditLog.log(staff_user, 'COMPLETED', self, f"Completed. Response: {response}")

    def cancel(self, staff_user, reason=''):
        self.status = RequestStatus.CANCELLED
        if reason:
            self.internal_notes += f"\nCancelled: {reason}"
        self.save()
        AuditLog.log(staff_user, 'CANCELLED', self, f"Cancelled. Reason: {reason}")

    # -----------------------------------------------------------------------
    # PROPERTIES
    # -----------------------------------------------------------------------
    @property
    def is_urgent(self):
        return self.priority == RequestPriority.URGENT

    @property
    def is_open(self):
        return self.status not in [RequestStatus.COMPLETED, RequestStatus.CANCELLED]

    @property
    def minutes_open(self):
        """How many minutes since this request was created."""
        delta = timezone.now() - self.created_at
        return int(delta.total_seconds() / 60)

    @property
    def status_css_class(self):
        css_map = {
            'NEW':               'status-new',
            'ACKNOWLEDGED':      'status-acknowledged',
            'ASSIGNED':          'status-assigned',
            'IN_PROGRESS':       'status-in_progress',
            'WAITING_FOR_GUEST': 'status-waiting',
            'COMPLETED':         'status-completed',
            'CANCELLED':         'status-cancelled',
        }
        return css_map.get(self.status, '')

    @property
    def priority_css_class(self):
        css_map = {
            'LOW':    'priority-low',
            'NORMAL': 'priority-normal',
            'HIGH':   'priority-high',
            'URGENT': 'priority-urgent',
        }
        return css_map.get(self.priority, '')

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['status']),
            models.Index(fields=['room']),
            models.Index(fields=['priority']),
            models.Index(fields=['department']),
        ]


# ---------------------------------------------------------------------------
# AUDIT LOG
# ---------------------------------------------------------------------------
class AuditLog(models.Model):
    """
    Records every important action taken on a ServiceRequest.
    This creates full accountability — management can see who did what and when.

    USAGE:
        AuditLog.log(staff_user, 'COMPLETED', request_obj, "Notes")

    This is called from ServiceRequest methods so logging is automatic.
    """
    ACTION_CHOICES = [
        ('CREATED',      'Created'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('ASSIGNED',     'Assigned'),
        ('STARTED',      'Started'),
        ('UPDATED',      'Updated'),
        ('COMPLETED',    'Completed'),
        ('CANCELLED',    'Cancelled'),
        ('ESCALATED',    'Escalated'),
        ('MESSAGE_SENT', 'Message Sent'),
    ]

    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    request    = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    action     = models.CharField(max_length=20, choices=ACTION_CHOICES)
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def log(cls, user, action, request_obj, notes=''):
        """
        Class method to create an audit log entry.
        @classmethod means we call it on the class, not an instance:
            AuditLog.log(user, action, request)
        instead of:
            AuditLog().log(user, action, request)
        """
        cls.objects.create(
            user=user,
            action=action,
            request=request_obj,
            notes=notes
        )

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'System'
        return f"{user_name} — {self.action} — Request #{self.request.request_number}"

    class Meta:
        ordering = ['-created_at']


# ---------------------------------------------------------------------------
# MESSAGE (Guest ↔ Reception Chat)
# ---------------------------------------------------------------------------
class Message(models.Model):
    """
    A single chat message between a guest and reception.
    Messages are linked to a ServiceRequest for context.
    """
    request    = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sent_messages'
    )
    # If sender_staff is null, it was sent by the guest
    is_from_guest = models.BooleanField(default=False)
    content       = models.TextField()
    is_read       = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = "Guest" if self.is_from_guest else (
            self.sender_staff.get_full_name() if self.sender_staff else "Staff"
        )
        return f"[{sender}] {self.content[:50]}"

    class Meta:
        ordering = ['created_at']
