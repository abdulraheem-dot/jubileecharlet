import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'jubilee_chalets.settings'
django.setup()

from django.template.loader import get_template

templates_to_check = [
    'base/staff_base.html',
    'accounts/login.html',
    'accounts/staff_list.html',
    'accounts/staff_form.html',
    'accounts/staff_edit.html',
    'accounts/staff_detail.html',
    'accounts/my_profile.html',
    'core/home.html',
    'rooms/room_list.html',
    'rooms/room_detail.html',
    'rooms/room_form.html',
    'rooms/room_qr.html',
    'guests/guest_list.html',
    'guests/guest_detail.html',
    'guests/guest_checkin.html',
    'guests/guest_checkout_confirm.html',
    'guests/portal_entry.html',
    'guests/portal_home.html',
    'guests/portal_no_checkin.html',
    'requests_app/reception_dashboard.html',
    'requests_app/request_list.html',
    'requests_app/request_detail.html',
    'requests_app/department_dashboard.html',
    'requests_app/guest_submit_request.html',
    'requests_app/guest_request_status.html',
    'notifications/list.html',
    'restaurant/dashboard.html',
    'restaurant/order_detail.html',
    'restaurant/guest_menu.html',
    'restaurant/guest_order_status.html',
    'restaurant/menu_management.html',
    'housekeeping/dashboard.html',
    'housekeeping/room_status.html',
    'maintenance/dashboard.html',
    'maintenance/record_detail.html',
    'maintenance/record_form.html',
    'inventory/list.html',
    'inventory/item_form.html',
    'feedback/list.html',
    'feedback/guest_feedback.html',
    'feedback/guest_complaint.html',
    'reports/dashboard.html',
]

passed = 0
failed = 0
for t in templates_to_check:
    try:
        get_template(t)
        print(f"  OK  {t}")
        passed += 1
    except Exception as e:
        print(f"  FAIL {t}")
        print(f"       --> {e}")
        failed += 1

print(f"\nResults: {passed} passed, {failed} failed out of {len(templates_to_check)}")
