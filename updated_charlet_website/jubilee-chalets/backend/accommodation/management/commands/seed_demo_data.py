"""
Seed demonstration data for development.
Clearly marked as demo data — never used in production.
"""
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accommodation.models import Room, RoomCategory, Amenity
from experiences.models import Experience
from dining.models import MenuCategory, MenuItem
from gallery.models import GalleryImage
from enquiries.models import FAQ, Testimonial
from website.models import WebsiteSettings

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demonstration data for local development (clearly labelled as demo)'

    def handle(self, *args, **options):
        if not os.environ.get('ALLOW_SEED_DEMO') and not os.environ.get('DEBUG'):
            self.stdout.write(self.style.ERROR('Refusing to seed demo data outside DEBUG mode unless ALLOW_SEED_DEMO=1'))
            return

        self.stdout.write(self.style.WARNING('=== SEEDING DEMO DATA (clearly labelled) ==='))

        # Admin user
        admin, created = User.objects.get_or_create(
            email='admin@jubileechalets.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            admin.set_password('demo12345')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created admin user: admin@jubileechalets.com / demo12345'))

        # Demo guest
        guest, created = User.objects.get_or_create(
            email='guest@example.com',
            defaults={'first_name': 'Demo', 'last_name': 'Guest'},
        )
        if created:
            guest.set_password('demo12345')
            guest.save()
            self.stdout.write(self.style.SUCCESS('Created demo guest: guest@example.com / demo12345'))

        # Website settings
        WebsiteSettings.objects.update_or_create(pk=1, defaults={
            'site_name': 'Jubilee Chalets Epe',
            'tagline': 'Escape the Ordinary. Experience Serenity.',
            'phone_primary': '+234 800 000 0000',
            'email_primary': 'info@jubileechalets.com',
            'address': 'Epe, Lagos State, Nigeria',
            'whatsapp_number': '+2348000000000',
            'cancellation_policy': 'Demo cancellation policy. To be replaced with official policy.',
            'privacy_policy': 'Demo privacy policy. To be replaced with official policy.',
            'terms_conditions': 'Demo terms. To be replaced with official terms.',
        })

        # Room categories
        categories_data = [
            {'name': 'Standard Chalet', 'description': 'Comfortable chalet with essential amenities.', 'display_order': 1},
            {'name': 'Deluxe Chalet', 'description': 'Spacious chalet with enhanced comfort features.', 'display_order': 2},
            {'name': 'Family Suite', 'description': 'Larger suite accommodating families.', 'display_order': 3},
        ]
        cats = {}
        for cd in categories_data:
            cat, _ = RoomCategory.objects.get_or_create(name=cd['name'], defaults=cd)
            cats[cd['name']] = cat

        # Amenities
        amenities_data = ['Air Conditioning', 'Free WiFi', 'TV', 'Hot Shower', 'Mini Fridge', 'Breakfast Included', 'Pool Access', 'Garden View', 'Private Balcony', 'Work Desk']
        amenity_objs = []
        for a in amenities_data:
            obj, _ = Amenity.objects.get_or_create(name=a)
            amenity_objs.append(obj)

        # Rooms (clearly demo data)
        rooms_data = [
            {'name': 'Standard Chalet A1', 'category': 'Standard Chalet', 'price': '15000', 'max_adults': 2, 'max_children': 1, 'bed': '1 Double Bed', 'size': '25.00'},
            {'name': 'Standard Chalet A2', 'category': 'Standard Chalet', 'price': '15000', 'max_adults': 2, 'max_children': 1, 'bed': '2 Single Beds', 'size': '25.00'},
            {'name': 'Deluxe Chalet B1', 'category': 'Deluxe Chalet', 'price': '25000', 'max_adults': 2, 'max_children': 2, 'bed': '1 King Bed', 'size': '40.00'},
            {'name': 'Deluxe Chalet B2', 'category': 'Deluxe Chalet', 'price': '28000', 'max_adults': 2, 'max_children': 2, 'bed': '1 King Bed + 1 Sofa Bed', 'size': '45.00'},
            {'name': 'Family Suite C1', 'category': 'Family Suite', 'price': '40000', 'max_adults': 4, 'max_children': 3, 'bed': '2 Double Beds', 'size': '60.00'},
            {'name': 'Family Suite C2', 'category': 'Family Suite', 'price': '45000', 'max_adults': 4, 'max_children': 3, 'bed': '1 King + 2 Single Beds', 'size': '70.00'},
        ]
        for i, rd in enumerate(rooms_data):
            room, created = Room.objects.get_or_create(
                name=rd['name'],
                defaults={
                    'category': cats[rd['category']],
                    'description': f'[DEMO DATA] {rd["name"]} — a comfortable room at Jubilee Chalets. Replace with official description.',
                    'short_description': f'[DEMO] {rd["name"]} in Epe, Lagos.',
                    'price_per_night': Decimal(rd['price']),
                    'max_adults': rd['max_adults'],
                    'max_children': rd['max_children'],
                    'max_occupancy': rd['max_adults'] + rd['max_children'],
                    'bed_configuration': rd['bed'],
                    'size_sqm': Decimal(rd['size']),
                    'is_available': True,
                    'is_active': True,
                },
            )
            if created:
                for am in amenity_objs[:5 + (i % 5)]:
                    room.amenities.add(am)

        self.stdout.write(self.style.SUCCESS(f'Seeded {Room.objects.count()} demo rooms'))

        # Experiences (demo)
        experiences_data = [
            {'title': 'Swimming Pool', 'category': 'swimming', 'desc': '[DEMO] Relax in our swimming facilities.', 'free': True},
            {'title': 'Outdoor Recreation', 'category': 'outdoor', 'desc': '[DEMO] Enjoy outdoor activities in our grounds.', 'free': True},
            {'title': 'Restaurant Dining', 'category': 'dining', 'desc': '[DEMO] Local and continental cuisine.', 'free': True},
            {'title': 'Corporate Retreats', 'category': 'corporate', 'desc': '[DEMO] Venue for corporate events.', 'free': True},
            {'title': 'Family Outings', 'category': 'family', 'desc': '[DEMO] Memorable family getaways.', 'free': True},
            {'title': 'Special Events', 'category': 'events', 'desc': '[DEMO] Host your special occasions.', 'free': True},
        ]
        for ed in experiences_data:
            Experience.objects.get_or_create(
                title=ed['title'],
                defaults={'description': ed['desc'], 'category': ed['category'], 'is_free': ed['free'], 'is_active': True, 'short_description': ed['desc']},
            )

        # Menu (demo)
        mc, _ = MenuCategory.objects.get_or_create(name='Local Specialities', defaults={'display_order': 1})
        MenuItem.objects.get_or_create(
            name='Jollof Rice [DEMO]',
            defaults={'category': mc, 'price': Decimal('2500'), 'description': '[DEMO] Classic Nigerian jollof rice.', 'is_available': True},
        )
        MenuItem.objects.get_or_create(
            name='Suya Platter [DEMO]',
            defaults={'category': mc, 'price': Decimal('3500'), 'description': '[DEMO] Spicy grilled meat.', 'is_available': True},
        )
        mc2, _ = MenuCategory.objects.get_or_create(name='Continental', defaults={'display_order': 2})
        MenuItem.objects.get_or_create(
            name='Continental Breakfast [DEMO]',
            defaults={'category': mc2, 'price': Decimal('3000'), 'description': '[DEMO] Eggs, toast, tea/coffee.', 'is_available': True},
        )

        # FAQs (demo)
        faqs = [
            {'q': 'What are the check-in and check-out times?', 'a': '[DEMO] Check-in is from 2:00 PM and check-out is by 12:00 PM.', 'cat': 'booking'},
            {'q': 'Is breakfast included?', 'a': '[DEMO] Please check individual room details or contact us for current inclusions.', 'cat': 'accommodation'},
            {'q': 'What payment methods do you accept?', 'a': '[DEMO] We accept payments via Paystack (cards, bank transfer).', 'cat': 'payment'},
            {'q': 'Can I cancel my booking?', 'a': '[DEMO] Yes, you can request cancellation from your dashboard. Our team will review it per our cancellation policy.', 'cat': 'booking'},
        ]
        for i, faq in enumerate(faqs):
            FAQ.objects.get_or_create(question=faq['q'], defaults={'answer': faq['a'], 'category': faq['cat'], 'display_order': i})

        self.stdout.write(self.style.SUCCESS('=== DEMO DATA SEEDED SUCCESSFULLY ==='))
        self.stdout.write(self.style.WARNING('NOTE: All demo data is clearly labelled with [DEMO]. Replace before production.'))
