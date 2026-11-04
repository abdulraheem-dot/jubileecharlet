from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import FoodCategory, MenuItem, FoodOrder, FoodOrderItem, OrderStatus


@login_required
def dashboard(request):
    orders = FoodOrder.objects.select_related('room', 'guest').order_by('-created_at')
    active = orders.exclude(status__in=[OrderStatus.DELIVERED, OrderStatus.CANCELLED])
    context = {
        'active_orders': active,
        'new_count':      orders.filter(status=OrderStatus.NEW).count(),
        'preparing_count':orders.filter(status=OrderStatus.PREPARING).count(),
        'ready_count':    orders.filter(status=OrderStatus.READY).count(),
    }
    return render(request, 'restaurant/dashboard.html', context)


@login_required
def order_detail(request, pk):
    order = get_object_or_404(FoodOrder.objects.prefetch_related('items__item'), pk=pk)
    return render(request, 'restaurant/order_detail.html', {'order': order})


@login_required
def update_order_status(request, pk):
    order = get_object_or_404(FoodOrder, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(OrderStatus.choices):
            order.status = new_status
            if new_status == OrderStatus.DELIVERED:
                order.delivered_at = timezone.now()
                order.handled_by   = request.user
            order.save()
            messages.success(request, f"Order #{order.pk} updated to {order.get_status_display()}.")
    return redirect('restaurant:order_detail', pk=pk)


# ---- Guest-facing menu & ordering ----
def guest_menu(request):
    room_id = request.session.get('guest_room_id')
    if not room_id:
        return redirect('guests:portal_entry')

    from rooms.models import Room
    room       = get_object_or_404(Room, pk=room_id)
    categories = FoodCategory.objects.prefetch_related('items').all()

    return render(request, 'restaurant/guest_menu.html', {
        'room': room,
        'categories': categories,
    })


def guest_place_order(request):
    room_id = request.session.get('guest_room_id')
    stay_id = request.session.get('guest_stay_id')
    if not room_id:
        return redirect('guests:portal_entry')

    from rooms.models import Room
    from guests.models import GuestStay
    room  = get_object_or_404(Room, pk=room_id)
    stay  = GuestStay.objects.filter(pk=stay_id, is_active=True).select_related('guest').first() if stay_id else None
    guest = stay.guest if stay else None

    if request.method == 'POST':
        instructions = request.POST.get('special_instructions', '')
        order = FoodOrder.objects.create(
            room=room, guest=guest, special_instructions=instructions
        )
        # Parse cart items: item_<id> = quantity
        for key, val in request.POST.items():
            if key.startswith('item_'):
                try:
                    item_id  = int(key.split('_')[1])
                    quantity = int(val)
                    if quantity > 0:
                        menu_item = MenuItem.objects.get(pk=item_id, is_available=True)
                        FoodOrderItem.objects.create(order=order, item=menu_item, quantity=quantity)
                except Exception:
                    pass

        if order.items.exists():
            # Notify restaurant staff
            try:
                from notifications.utils import create_notification
                from django.contrib.auth import get_user_model
                User = get_user_model()
                for staff in User.objects.filter(role='RESTAURANT', is_active=True):
                    create_notification(staff, f"New food order — Room {room.number}",
                                        f"Order #{order.pk} placed.", notification_type='NEW_REQUEST')
            except Exception:
                pass
            messages.success(request, f"Order placed! Your order #{order.pk} is being prepared.")
            return redirect('restaurant:guest_order_status', pk=order.pk)
        else:
            order.delete()
            messages.error(request, "Your cart was empty. Please select at least one item.")

    return redirect('restaurant:guest_menu')


def guest_order_status(request, pk):
    order = get_object_or_404(FoodOrder.objects.prefetch_related('items__item'), pk=pk)
    return render(request, 'restaurant/guest_order_status.html', {'order': order})


@login_required
def menu_management(request):
    categories = FoodCategory.objects.prefetch_related('items').all()
    return render(request, 'restaurant/menu_management.html', {'categories': categories})
