from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import InventoryItem
from accounts.decorators import manager_required


@login_required
@manager_required
def item_list(request):
    items    = InventoryItem.objects.all()
    low_stock = items.filter(quantity__lte=models.F('minimum_level')) if False else [
        i for i in items if i.is_low_stock
    ]

    dept_filter = request.GET.get('dept', '')
    if dept_filter:
        items = items.filter(department=dept_filter)

    context = {
        'items':        items,
        'low_stock':    low_stock,
        'dept_filter':  dept_filter,
        'departments':  InventoryItem.ItemDepartment.choices,
    }
    return render(request, 'inventory/list.html', context)


@login_required
@manager_required
def update_quantity(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        try:
            new_qty = int(request.POST.get('quantity', item.quantity))
            item.quantity        = new_qty
            item.last_updated_by = request.user
            item.save()
            messages.success(request, f"{item.name} updated to {new_qty} {item.unit}.")
        except ValueError:
            messages.error(request, "Invalid quantity.")
    return redirect('inventory:list')


@login_required
@manager_required
def create_item(request):
    from .forms import InventoryItemForm
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.last_updated_by = request.user
            item.save()
            messages.success(request, f"Inventory item '{item.name}' created.")
            return redirect('inventory:list')
    else:
        form = InventoryItemForm()
    return render(request, 'inventory/item_form.html', {'form': form})
