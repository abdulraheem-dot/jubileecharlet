"""
seed_data.py

Run this script to populate the database with realistic sample data:
    python seed_data.py

This creates:
- A super admin account
- Staff accounts for each role
- Room types and rooms
- Sample menu items
- Sample inventory items

NEVER run this in production with real guest data.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jubilee_chalets.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import StaffProfile, Role
from rooms.models import RoomType, Room
from restaurant.models import FoodCategory, MenuItem
from inventory.models import InventoryItem

User = get_user_model()

print("🏨 Seeding Jubilee Chalets database...")

# ---- SUPER ADMIN ----
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@jubileechalets.com',
        password='admin123',
        first_name='System',
        last_name='Administrator',
        role=Role.SUPER_ADMIN
    )
    StaffProfile.objects.create(user=admin, department='MANAGEMENT', employee_number='JC-000')
    print("  ✓ Super admin created (username: admin, password: admin123)")

# ---- STAFF ACCOUNTS ----
staff_data = [
    ('manager1',    'Adebayo',  'Okafor',    'MANAGER',        'MANAGEMENT',    'JC-001', 'MORNING'),
    ('reception1',  'Funmi',    'Adeyemi',   'RECEPTIONIST',   'RECEPTION',     'JC-002', 'MORNING'),
    ('reception2',  'Chidi',    'Nwachukwu', 'RECEPTIONIST',   'RECEPTION',     'JC-003', 'AFTERNOON'),
    ('maintenance1','Emeka',    'Obi',       'MAINTENANCE',    'MAINTENANCE',   'JC-004', 'MORNING'),
    ('maintenance2','Tunde',    'Bello',     'MAINTENANCE',    'MAINTENANCE',   'JC-005', 'AFTERNOON'),
    ('housekeeping1','Ngozi',   'Eze',       'HOUSEKEEPING',   'HOUSEKEEPING',  'JC-006', 'MORNING'),
    ('housekeeping2','Amina',   'Ibrahim',   'HOUSEKEEPING',   'HOUSEKEEPING',  'JC-007', 'AFTERNOON'),
    ('restaurant1', 'Kemi',     'Adebisi',   'RESTAURANT',     'RESTAURANT',    'JC-008', 'MORNING'),
    ('restaurant2', 'Seun',     'Taiwo',     'RESTAURANT',     'RESTAURANT',    'JC-009', 'AFTERNOON'),
    ('security1',   'John',     'Adesanya',  'SECURITY',       'SECURITY',      'JC-010', 'NIGHT'),
]

for username, first, last, role, dept, emp_no, shift in staff_data:
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username, password='staff123',
            first_name=first, last_name=last,
            email=f'{username}@jubileechalets.com',
            role=role, is_guest_user=False
        )
        StaffProfile.objects.create(
            user=user, department=dept,
            employee_number=emp_no, shift=shift
        )
        print(f"  ✓ {role}: {first} {last} (username: {username}, password: staff123)")

# ---- ROOM TYPES ----
room_types = [
    ('Standard Room',    'Comfortable standard room with modern amenities.',   45000, 2, 'Queen'),
    ('Deluxe Room',      'Spacious deluxe room with lagoon view.',              65000, 2, 'King'),
    ('Executive Suite',  'Premium suite with sitting area and extra amenities.',95000, 3, 'King'),
    ('Conference Room',  'Fully equipped conference and meeting room.',          0,    20, 'N/A'),
    ('Family Room',      'Large room suitable for families.',                   75000, 4, 'Twin+Double'),
]

for name, desc, price, occ, bed in room_types:
    rt, created = RoomType.objects.get_or_create(name=name, defaults={
        'description': desc, 'price_per_night': price,
        'max_occupancy': occ, 'bed_type': bed
    })
    if created:
        print(f"  ✓ Room type: {name}")

# ---- ROOMS ----
std_rt  = RoomType.objects.get(name='Standard Room')
dlx_rt  = RoomType.objects.get(name='Deluxe Room')
exe_rt  = RoomType.objects.get(name='Executive Suite')
fam_rt  = RoomType.objects.get(name='Family Room')

rooms_data = [
    # (number, floor, type, status)
    ('101', 1, std_rt, 'AVAILABLE'),
    ('102', 1, std_rt, 'OCCUPIED'),
    ('103', 1, std_rt, 'AVAILABLE'),
    ('104', 1, std_rt, 'CLEANING'),
    ('105', 1, fam_rt, 'AVAILABLE'),
    ('201', 2, dlx_rt, 'OCCUPIED'),
    ('202', 2, dlx_rt, 'AVAILABLE'),
    ('203', 2, dlx_rt, 'OCCUPIED'),
    ('204', 2, dlx_rt, 'MAINTENANCE'),
    ('205', 2, fam_rt, 'AVAILABLE'),
    ('301', 3, exe_rt, 'OCCUPIED'),
    ('302', 3, exe_rt, 'AVAILABLE'),
    ('303', 3, exe_rt, 'RESERVED'),
]

for number, floor, rt, status in rooms_data:
    if not Room.objects.filter(number=number).exists():
        Room.objects.create(number=number, floor=floor, room_type=rt, status=status)
        print(f"  ✓ Room {number} created")

# ---- FOOD MENU ----
menu_data = [
    ('Nigerian Dishes', [
        ('Jollof Rice',       'Smoky Nigerian party jollof with chicken',  5000),
        ('Fried Rice',        'Nigerian fried rice with mixed vegetables',  5000),
        ('Egusi Soup + Eba',  'Ground melon seed soup with garri',         6000),
        ('Pepper Soup',       'Spicy broth with assorted meat',            4500),
        ('Suya',              'Grilled spiced beef skewers',               3500),
    ]),
    ('Grills & Proteins', [
        ('Grilled Chicken',   'Half chicken, lemon herb marinade',         4000),
        ('Grilled Fish',      'Fresh tilapia or catfish, grilled',         5500),
        ('Beef Steak',        '200g beef steak with chips',                7500),
    ]),
    ('Sides & Snacks', [
        ('French Fries',      'Crispy golden fries',                       1500),
        ('Plantain (Dodo)',   'Fried sweet plantain',                      1200),
        ('Spring Rolls',      '4 pieces vegetable spring rolls',           2000),
        ('Moi Moi',           'Steamed bean pudding',                      1500),
    ]),
    ('Drinks', [
        ('Soft Drink (Can)',  'Coke, Fanta, Sprite, 7-Up',                 800),
        ('Fresh Juice',       'Orange, pineapple, or watermelon',          1500),
        ('Water (500ml)',     'Chilled bottled water',                     400),
        ('Maltina',           'Nigerian malt drink',                       900),
        ('Chapman',           'Nigerian cocktail mocktail',                1800),
    ]),
    ('Breakfast', [
        ('Full Nigerian Breakfast', 'Fried eggs, sausage, bread, tea',    3500),
        ('Continental Breakfast',  'Bread, butter, jam, fruits, coffee',  2500),
        ('Akara & Pap',           'Bean cakes with ogi porridge',         2000),
    ]),
]

for cat_name, items in menu_data:
    cat, _ = FoodCategory.objects.get_or_create(name=cat_name)
    for item_name, desc, price in items:
        MenuItem.objects.get_or_create(
            name=item_name, category=cat,
            defaults={'description': desc, 'price': price}
        )
print("  ✓ Menu items created")

# ---- INVENTORY ----
inventory_data = [
    ('Bath Towels',       'HOUSEKEEPING', 45, 'pieces',  20),
    ('Hand Towels',       'HOUSEKEEPING', 60, 'pieces',  30),
    ('Bed Sheets',        'HOUSEKEEPING', 30, 'sets',    15),
    ('Pillowcases',       'HOUSEKEEPING', 50, 'pieces',  25),
    ('Shampoo (bottles)', 'HOUSEKEEPING', 80, 'bottles', 30),
    ('Soap Bars',         'HOUSEKEEPING', 100,'pieces',  40),
    ('Toilet Paper',      'HOUSEKEEPING', 200,'rolls',   80),
    ('Bottled Water',     'HOUSEKEEPING', 150,'bottles', 50),
    ('Floor Cleaner',     'HOUSEKEEPING', 12, 'litres',  5),
    ('Rice (kg)',         'RESTAURANT',   30, 'kg',      10),
    ('Cooking Oil',       'RESTAURANT',   15, 'litres',  5),
    ('Chicken (frozen)',  'RESTAURANT',   20, 'kg',      8),
    ('Soft Drinks (crate)','RESTAURANT',  8, 'crates',   3),
    ('Light Bulbs',       'MAINTENANCE',  25, 'pieces',  10),
    ('Extension Cables',  'MAINTENANCE',  8,  'pieces',  3),
    ('Detergent',         'LAUNDRY',      20, 'kg',      8),
]

for name, dept, qty, unit, minimum in inventory_data:
    InventoryItem.objects.get_or_create(name=name, defaults={
        'department': dept, 'quantity': qty,
        'unit': unit, 'minimum_level': minimum
    })
print("  ✓ Inventory items created")

print("\n✅ Seed complete!")
print("\n📋 Login credentials:")
print("   Super Admin:  admin / admin123")
print("   Manager:      manager1 / staff123")
print("   Reception:    reception1 / staff123")
print("   Maintenance:  maintenance1 / staff123")
print("   Housekeeping: housekeeping1 / staff123")
print("   Restaurant:   restaurant1 / staff123")
print("\n🌐 Start the server: python manage.py runserver")
