from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import MaintenanceRecord


@login_required
def dashboard(request):
    records = MaintenanceRecord.objects.select_related('room', 'assigned_to')

    if request.user.role == 'MAINTENANCE':
        records = records.filter(assigned_to=request.user)

    open_records = records.exclude(status__in=['COMPLETED', 'CANCELLED']).order_by('-created_at')

    context = {
        'open_records':   open_records,
        'open_count':     records.filter(status='OPEN').count(),
        'inprogress_count': records.filter(status='IN_PROGRESS').count(),
        'completed_today':  records.filter(
            status='COMPLETED',
            completed_at__date=timezone.now().date()
        ).count(),
    }
    return render(request, 'maintenance/dashboard.html', context)


@login_required
def record_detail(request, pk):
    record = get_object_or_404(MaintenanceRecord, pk=pk)
    return render(request, 'maintenance/record_detail.html', {'record': record})


@login_required
def create_record(request):
    from .forms import MaintenanceForm
    if request.method == 'POST':
        form = MaintenanceForm(request.POST, request.FILES)
        if form.is_valid():
            rec = form.save(commit=False)
            rec.reported_by = request.user
            rec.save()
            messages.success(request, "Maintenance record created.")
            return redirect('maintenance:record_detail', pk=rec.pk)
    else:
        room_pk = request.GET.get('room')
        initial = {}
        if room_pk:
            from rooms.models import Room
            try:
                initial['room'] = Room.objects.get(pk=room_pk)
            except Exception:
                pass
        form = MaintenanceForm(initial=initial)
    return render(request, 'maintenance/record_form.html', {'form': form, 'title': 'New Maintenance Record'})


@login_required
def update_record(request, pk):
    record = get_object_or_404(MaintenanceRecord, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes      = request.POST.get('notes', '')
        if new_status:
            record.status = new_status
            if new_status == 'COMPLETED':
                record.completed_at = timezone.now()
                # Revert room from MAINTENANCE if this was the reason
                if record.room.status == 'MAINTENANCE':
                    record.room.status = 'AVAILABLE'
                    record.room.save()
        if notes:
            record.notes += f"\n{notes}"
        if 'photo_after' in request.FILES:
            record.photo_after = request.FILES['photo_after']
        record.save()
        messages.success(request, "Record updated.")
    return redirect('maintenance:record_detail', pk=pk)
