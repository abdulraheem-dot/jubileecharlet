"""
requests_app/views.py

All views for the service request system:
- Reception dashboard
- Department dashboards
- Guest request submission
- Request management (assign, update, complete)
- Messaging
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.views.decorators.http import require_POST

from .models import (
    ServiceRequest, RequestStatus, RequestPriority, RequestCategory,
    RequestDepartment, AuditLog, Message, QUICK_SERVICE_PRESETS
)
from .forms import ServiceRequestForm, AssignRequestForm, StaffResponseForm, MessageForm
from accounts.decorators import receptionist_or_above, staff_required
from notifications.utils import notify_staff_new_request, notify_guest_status_change


# ===========================================================================
# RECEPTION DASHBOARD
# ===========================================================================
@login_required
@receptionist_or_above
def reception_dashboard(request):
    """
    The main dashboard receptionists use all day.

    QUERYSET BREAKDOWN:
    ServiceRequest.objects.filter(status='NEW')
    → SELECT * FROM requests_app_servicerequest WHERE status = 'NEW'

    .select_related('room', 'guest', 'assigned_to')
    → Uses SQL JOIN to fetch linked room, guest, and assigned_to in ONE query
      instead of making separate queries for each request (avoids N+1 problem)

    .order_by('-created_at')
    → ORDER BY created_at DESC (newest first; '-' means descending)
    """
    base_qs = ServiceRequest.objects.select_related(
        'room', 'room__room_type', 'guest', 'assigned_to'
    )

    new_requests      = base_qs.filter(status=RequestStatus.NEW).order_by('-created_at')
    pending_requests  = base_qs.filter(
        status__in=[RequestStatus.ACKNOWLEDGED, RequestStatus.ASSIGNED]
    ).order_by('-created_at')
    inprogress        = base_qs.filter(status=RequestStatus.IN_PROGRESS).order_by('-created_at')
    urgent_requests   = base_qs.filter(
        priority=RequestPriority.URGENT,
        status__in=[RequestStatus.NEW, RequestStatus.ACKNOWLEDGED,
                    RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS]
    ).order_by('-created_at')

    from django.utils import timezone as tz
    today = tz.now().date()
    completed_today   = base_qs.filter(
        status=RequestStatus.COMPLETED,
        completed_at__date=today
    ).count()

    # Unread messages — messages sent by guests not yet read by staff
    unread_messages = Message.objects.filter(is_from_guest=True, is_read=False).count()

    context = {
        'new_requests':     new_requests,
        'pending_requests': pending_requests,
        'inprogress':       inprogress,
        'urgent_requests':  urgent_requests,
        'completed_today':  completed_today,
        'unread_messages':  unread_messages,
        'new_count':        new_requests.count(),
        'pending_count':    pending_requests.count(),
        'inprogress_count': inprogress.count(),
        'urgent_count':     urgent_requests.count(),
    }
    return render(request, 'requests_app/reception_dashboard.html', context)


# ===========================================================================
# DEPARTMENT DASHBOARD
# ===========================================================================
@login_required
def department_dashboard(request):
    """
    Dashboard for non-reception departments: Maintenance, Housekeeping, etc.
    Shows only requests assigned to this staff member's department.
    """
    user = request.user
    dept = getattr(user, 'staffprofile', None)
    dept_name = dept.department if dept else user.role

    # Map role to department string
    role_dept_map = {
        'MAINTENANCE':    RequestDepartment.MAINTENANCE,
        'HOUSEKEEPING':   RequestDepartment.HOUSEKEEPING,
        'RESTAURANT':     RequestDepartment.RESTAURANT,
        'LAUNDRY':        RequestDepartment.LAUNDRY,
        'SECURITY':       RequestDepartment.SECURITY,
        'TRANSPORTATION': RequestDepartment.TRANSPORTATION,
    }
    dept_code = role_dept_map.get(user.role, RequestDepartment.RECEPTION)

    # Requests assigned to this department
    my_requests = ServiceRequest.objects.filter(
        department=dept_code
    ).select_related('room', 'guest', 'assigned_to').order_by('-created_at')

    # Requests specifically assigned to this user
    assigned_to_me = my_requests.filter(
        assigned_to=user,
        status__in=[RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS]
    )

    context = {
        'dept_code':      dept_code,
        'my_requests':    my_requests,
        'assigned_to_me': assigned_to_me,
        'new_dept_requests': my_requests.filter(status=RequestStatus.NEW).count(),
        'in_progress':    my_requests.filter(status=RequestStatus.IN_PROGRESS).count(),
    }
    return render(request, 'requests_app/department_dashboard.html', context)


# ===========================================================================
# REQUEST DETAIL
# ===========================================================================
@login_required
def request_detail(request, pk):
    """Full detail view for a single service request."""
    req = get_object_or_404(
        ServiceRequest.objects.select_related(
            'room', 'guest', 'assigned_to', 'created_by'
        ).prefetch_related('messages__sender_staff', 'audit_logs__user'),
        pk=pk
    )

    assign_form   = AssignRequestForm(instance=req)
    response_form = StaffResponseForm(instance=req)
    message_form  = MessageForm()

    # Mark guest messages as read when staff views this request
    Message.objects.filter(request=req, is_from_guest=True, is_read=False).update(is_read=True)

    context = {
        'req':           req,
        'assign_form':   assign_form,
        'response_form': response_form,
        'message_form':  message_form,
        'audit_logs':    req.audit_logs.all()[:20],
        'messages_list': req.messages.all(),
    }
    return render(request, 'requests_app/request_detail.html', context)


# ===========================================================================
# ASSIGN REQUEST
# ===========================================================================
@login_required
@receptionist_or_above
def assign_request(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        form = AssignRequestForm(request.POST, instance=req)
        if form.is_valid():
            assigned_staff = form.cleaned_data['assigned_to']
            dept           = form.cleaned_data.get('department', req.department)
            priority       = form.cleaned_data.get('priority', req.priority)

            req.department = dept
            req.priority   = priority
            req.assign(request.user, assigned_staff)

            # Notify assigned staff
            try:
                from notifications.utils import create_notification
                create_notification(
                    recipient=assigned_staff,
                    title=f"New assignment: {req.title}",
                    message=f"Request #{req.request_number} in Room {req.room.number} has been assigned to you.",
                    request_obj=req,
                    notification_type='ASSIGNMENT'
                )
            except Exception:
                pass

            messages.success(request, f"Request assigned to {assigned_staff.get_full_name()}.")
    return redirect('requests_app:request_detail', pk=pk)


# ===========================================================================
# UPDATE STATUS
# ===========================================================================
@login_required
def update_request_status(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        response_text = request.POST.get('staff_response', '')

        if new_status == RequestStatus.COMPLETED:
            req.complete(request.user, response=response_text)
            # Notify guest
            try:
                from notifications.utils import create_notification
                if req.guest and req.guest.user:
                    create_notification(
                        recipient=req.guest.user,
                        title="Your request is complete",
                        message=f"Request #{req.request_number}: {req.title} has been completed.",
                        request_obj=req,
                        notification_type='COMPLETION'
                    )
            except Exception:
                pass
        elif new_status == RequestStatus.IN_PROGRESS:
            req.start_progress(request.user)
        elif new_status == RequestStatus.CANCELLED:
            reason = request.POST.get('cancel_reason', '')
            req.cancel(request.user, reason)
        elif new_status and new_status in dict(RequestStatus.choices):
            req.status = new_status
            req.save()
            AuditLog.log(request.user, 'UPDATED', req, f"Status changed to {new_status}")

        messages.success(request, "Request status updated.")
    return redirect('requests_app:request_detail', pk=pk)


# ===========================================================================
# MESSAGES JSON (for real-time polling)
# ===========================================================================
def request_messages_json(request, pk):
    """
    Returns messages for a request as JSON.
    Used by the JavaScript polling on both staff and guest sides.

    Access control:
    - Staff: must be authenticated (non-guest user)
    - Guest: must have a matching guest_room_id in their session
    """
    req = get_object_or_404(ServiceRequest, pk=pk)

    # Determine who is asking
    is_staff = request.user.is_authenticated and not request.user.is_guest_user
    room_id  = request.session.get('guest_room_id')
    is_guest = bool(room_id and req.room.pk == room_id)

    if not is_staff and not is_guest:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Only return messages newer than after_id (client tracks last seen ID)
    after_id = int(request.GET.get('after_id', 0))
    msgs = req.messages.filter(id__gt=after_id).order_by('created_at')

    data = []
    for msg in msgs:
        if msg.sender_staff:
            sender_name = msg.sender_staff.get_full_name() or msg.sender_staff.username
        else:
            sender_name = 'Guest'
        data.append({
            'id':            msg.id,
            'content':       msg.content,
            'is_from_guest': msg.is_from_guest,
            'sender_name':   sender_name,
            'created_at':    msg.created_at.strftime('%H:%M'),
        })

    # Mark guest messages as read when staff polls
    if is_staff:
        Message.objects.filter(request=req, is_from_guest=True, is_read=False).update(is_read=True)

    return JsonResponse({
        'messages': data,
        'is_open':  req.is_open,
    })


# ===========================================================================
# SEND MESSAGE
# ===========================================================================
@login_required
def send_message(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            msg = Message.objects.create(
                request=req,
                sender_staff=request.user,
                is_from_guest=False,
                content=content
            )
            AuditLog.log(request.user, 'MESSAGE_SENT', req, content[:100])
            # Acknowledge if still NEW
            if req.status == RequestStatus.NEW:
                req.acknowledge(request.user)

            # Return JSON for AJAX requests (real-time chat)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'id':            msg.id,
                    'content':       msg.content,
                    'is_from_guest': False,
                    'sender_name':   request.user.get_full_name() or request.user.username,
                    'created_at':    msg.created_at.strftime('%H:%M'),
                })
    return redirect('requests_app:request_detail', pk=pk)


# ===========================================================================
# ALL REQUESTS (search + filter)
# ===========================================================================
@login_required
@receptionist_or_above
def request_list(request):
    """
    Full searchable, filterable list of all service requests.

    Django ORM chaining:
    Each .filter() call NARROWS the QuerySet.
    The actual SQL query is NOT run until the template iterates over the results.
    This is called LAZY EVALUATION — Django builds the query, then executes it.
    """
    qs = ServiceRequest.objects.select_related('room', 'guest', 'assigned_to').order_by('-created_at')

    # Search by room number, guest name, or request title
    search = request.GET.get('q', '')
    if search:
        qs = qs.filter(
            Q(room__number__icontains=search) |
            Q(guest__first_name__icontains=search) |
            Q(guest__last_name__icontains=search) |
            Q(title__icontains=search) |
            Q(request_number__icontains=search)
        )

    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)

    dept_filter = request.GET.get('department', '')
    if dept_filter:
        qs = qs.filter(department=dept_filter)

    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        qs = qs.filter(priority=priority_filter)

    date_filter = request.GET.get('date', '')
    if date_filter == 'today':
        from django.utils import timezone as tz
        qs = qs.filter(created_at__date=tz.now().date())

    context = {
        'requests':        qs,
        'search':          search,
        'status_filter':   status_filter,
        'dept_filter':     dept_filter,
        'priority_filter': priority_filter,
        'date_filter':     date_filter,
        'status_choices':  RequestStatus.choices,
        'dept_choices':    RequestDepartment.choices,
        'priority_choices':RequestPriority.choices,
        'total':           qs.count(),
    }
    return render(request, 'requests_app/request_list.html', context)


# ===========================================================================
# GUEST — SUBMIT REQUEST
# ===========================================================================
def guest_submit_request(request):
    """
    The guest-facing request submission form.
    Called from the portal when a guest taps a service button or fills the form.
    """
    from rooms.models import Room
    from guests.models import Guest, GuestStay

    # Get room from session (set when QR code was scanned)
    room_id  = request.session.get('guest_room_id')
    stay_id  = request.session.get('guest_stay_id')

    if not room_id:
        return redirect('guests:portal_entry')

    room  = get_object_or_404(Room, pk=room_id)
    stay  = GuestStay.objects.filter(pk=stay_id, is_active=True).select_related('guest').first() if stay_id else None
    guest = stay.guest if stay else None

    # Handle quick-service presets from buttons
    preset_key = request.GET.get('preset', '')
    initial = {}
    if preset_key and preset_key in QUICK_SERVICE_PRESETS:
        cat, pri, title = QUICK_SERVICE_PRESETS[preset_key]
        initial = {'category': cat, 'priority': pri, 'title': title}

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            req          = form.save(commit=False)
            req.room     = room
            req.guest    = guest
            req.save()

            # Create audit log entry
            AuditLog.objects.create(
                user=None,
                action='CREATED',
                request=req,
                notes=f"Submitted by guest from Room {room.number}"
            )

            # Notify reception
            try:
                from notifications.utils import create_notification
                from django.contrib.auth import get_user_model
                User = get_user_model()
                receptionists = User.objects.filter(role__in=['RECEPTIONIST', 'MANAGER', 'SUPER_ADMIN'], is_active=True)
                for receptionist in receptionists:
                    create_notification(
                        recipient=receptionist,
                        title=f"New request from Room {room.number}",
                        message=f"{req.title} — Priority: {req.get_priority_display()}",
                        request_obj=req,
                        notification_type='NEW_REQUEST'
                    )
            except Exception:
                pass

            request.session['last_request_id'] = req.pk
            return redirect('requests_app:guest_request_status', pk=req.pk)
    else:
        form = ServiceRequestForm(initial=initial)

    context = {
        'form':       form,
        'room':       room,
        'guest':      guest,
        'preset_key': preset_key,
    }
    return render(request, 'requests_app/guest_submit_request.html', context)


def guest_request_status(request, pk):
    """Shows a guest the current status of their request with a visual timeline."""
    req = get_object_or_404(ServiceRequest, pk=pk)

    # Verify this request belongs to the session's room
    room_id = request.session.get('guest_room_id')
    if room_id and req.room.pk != room_id:
        return redirect('guests:portal_home')

    timeline = [
        {'label': 'Request Received',    'done': True},
        {'label': 'Reception Notified',  'done': req.status != RequestStatus.NEW},
        {'label': 'Staff Assigned',      'done': req.status in [RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS, RequestStatus.COMPLETED]},
        {'label': 'In Progress',         'done': req.status in [RequestStatus.IN_PROGRESS, RequestStatus.COMPLETED]},
        {'label': 'Completed',           'done': req.status == RequestStatus.COMPLETED},
    ]

    context = {
        'req':      req,
        'timeline': timeline,
        'messages_list': req.messages.all(),
    }
    return render(request, 'requests_app/guest_request_status.html', context)


def guest_send_message(request, pk):
    """Guest sends a message about their request."""
    req = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            msg = Message.objects.create(
                request=req,
                is_from_guest=True,
                content=content
            )
            # Notify reception
            try:
                from notifications.utils import create_notification
                from django.contrib.auth import get_user_model
                User = get_user_model()
                receptionists = User.objects.filter(role__in=['RECEPTIONIST', 'MANAGER'], is_active=True)
                for r in receptionists:
                    create_notification(
                        recipient=r,
                        title=f"Guest message — Room {req.room.number}",
                        message=content[:100],
                        request_obj=req,
                        notification_type='GUEST_MESSAGE'
                    )
            except Exception:
                pass

            # Return JSON for AJAX requests (real-time chat)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'id':            msg.id,
                    'content':       msg.content,
                    'is_from_guest': True,
                    'sender_name':   'Guest',
                    'created_at':    msg.created_at.strftime('%H:%M'),
                })

    return redirect('requests_app:guest_request_status', pk=req.pk)
