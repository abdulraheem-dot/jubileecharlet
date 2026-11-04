"""
reports/views.py

Management analytics dashboard.
Uses Django ORM aggregation functions:
- Count()  → COUNT(*)
- Avg()    → AVG(column)
- Sum()    → SUM(column)
- annotate() → adds computed column to each object in QuerySet
- values() → GROUP BY equivalent
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta

from accounts.decorators import manager_required


@login_required
@manager_required
def dashboard(request):
    from requests_app.models import ServiceRequest, RequestStatus, RequestPriority, RequestDepartment
    from restaurant.models import FoodOrder
    from feedback.models import Feedback, Complaint
    from rooms.models import Room, RoomStatus
    from guests.models import GuestStay

    today     = timezone.now().date()
    this_week = timezone.now() - timedelta(days=7)

    # ---- Requests summary ----
    all_requests   = ServiceRequest.objects.all()
    today_requests = all_requests.filter(created_at__date=today)

    req_summary = {
        'total_today':      today_requests.count(),
        'completed_today':  today_requests.filter(status=RequestStatus.COMPLETED).count(),
        'pending':          all_requests.filter(status__in=[RequestStatus.NEW, RequestStatus.ACKNOWLEDGED, RequestStatus.ASSIGNED]).count(),
        'urgent_open':      all_requests.filter(priority=RequestPriority.URGENT).exclude(status__in=[RequestStatus.COMPLETED, RequestStatus.CANCELLED]).count(),
    }

    # ---- Avg response time (minutes from created to acknowledged) ----
    # We calculate this in Python since SQLite doesn't support date subtraction well
    acknowledged = all_requests.filter(
        acknowledged_at__isnull=False,
        created_at__gte=this_week
    ).values_list('created_at', 'acknowledged_at')

    if acknowledged:
        total_mins = sum(
            (a - c).total_seconds() / 60
            for c, a in acknowledged
        )
        avg_response_mins = round(total_mins / len(acknowledged), 1)
    else:
        avg_response_mins = 0

    # ---- Requests by department ----
    # .values('department') groups by department
    # .annotate(count=Count('id')) adds a count field to each group
    by_dept = list(
        all_requests.filter(created_at__gte=this_week)
        .values('department')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # ---- Requests by status ----
    by_status = list(
        all_requests.values('status')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # ---- Most common categories (this week) ----
    by_category = list(
        all_requests.filter(created_at__gte=this_week)
        .values('category')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    # ---- Room occupancy ----
    room_summary = {
        'total':       Room.objects.count(),
        'occupied':    Room.objects.filter(status=RoomStatus.OCCUPIED).count(),
        'available':   Room.objects.filter(status=RoomStatus.AVAILABLE).count(),
        'maintenance': Room.objects.filter(status=RoomStatus.MAINTENANCE).count(),
    }
    occupancy_pct = round(
        (room_summary['occupied'] / room_summary['total'] * 100) if room_summary['total'] else 0, 1
    )

    # ---- Food orders ----
    food_orders_today = FoodOrder.objects.filter(created_at__date=today).count()

    # ---- Guest satisfaction ----
    avg_rating = Feedback.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    total_feedback = Feedback.objects.count()

    # ---- Open complaints ----
    open_complaints = Complaint.objects.filter(status__in=['OPEN', 'IN_REVIEW']).count()

    # ---- Active guests ----
    active_guests = GuestStay.objects.filter(is_active=True).count()

    # ---- Data for charts (passed as lists for Chart.js) ----
    dept_labels  = [d['department'] for d in by_dept]
    dept_counts  = [d['count'] for d in by_dept]

    status_labels = [s['status'] for s in by_status]
    status_counts = [s['count'] for s in by_status]

    # Daily request count for last 7 days
    daily_data = []
    daily_labels = []
    for i in range(6, -1, -1):
        day   = today - timedelta(days=i)
        count = all_requests.filter(created_at__date=day).count()
        daily_data.append(count)
        daily_labels.append(day.strftime('%a %d'))

    context = {
        'req_summary':       req_summary,
        'avg_response_mins': avg_response_mins,
        'by_dept':           by_dept,
        'by_status':         by_status,
        'by_category':       by_category,
        'room_summary':      room_summary,
        'occupancy_pct':     occupancy_pct,
        'food_orders_today': food_orders_today,
        'avg_rating':        round(avg_rating, 1),
        'total_feedback':    total_feedback,
        'open_complaints':   open_complaints,
        'active_guests':     active_guests,
        # Chart data
        'dept_labels':   dept_labels,
        'dept_counts':   dept_counts,
        'status_labels': status_labels,
        'status_counts': status_counts,
        'daily_labels':  daily_labels,
        'daily_data':    daily_data,
    }
    return render(request, 'reports/dashboard.html', context)
