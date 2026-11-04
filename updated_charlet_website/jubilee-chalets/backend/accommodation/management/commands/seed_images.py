"""
Management command: seed_images
================================
Copies the real Jubilee Chalets photos from the project root into the backend
media folder and wires them to the correct database records:

  - Rooms  →  RoomImage  (primary + additional images per room category)
  - Gallery →  GalleryImage  (all photos, correctly categorised)
  - Experiences → Experience.image  (one hero per activity)
  - WebsiteSettings → logo field (if it exists) or just saved to media/logo/

Run once:
    python manage.py seed_images

Safe to re-run: skips records that already have an image attached.
"""

import os
import shutil
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.files import File

from accommodation.models import Room, RoomImage, RoomCategory, Amenity
from gallery.models import GalleryImage
from experiences.models import Experience
from website.models import WebsiteSettings

# ── Absolute path to the folder where the images live ────────────────────────
IMAGE_SRC = Path(r"C:\Users\USER\Documents\Charlet_project")

# ── Mapping: filename (without -Copy suffix) → where it goes ─────────────────
# Each entry is (media_subfolder, category_or_usage, alt_text)
IMAGE_MAP = {
    "01 - Guest Bedroom Twin Beds.jpg":          ("rooms",       "room",        "Guest bedroom with twin beds"),
    "02 - Conference Auditorium.jpg":             ("gallery",     "events",      "Conference auditorium – large hall"),
    "03 - Guest Bedroom Double Bed.jpg":          ("rooms",       "room",        "Guest bedroom with double bed"),
    "04 - Jubilee Chalets Logo.jpg":              ("logo",        "logo",        "Jubilee Chalets Epe logo"),
    "05 - Modern Glass Building Exterior Day.jpg":("gallery",     "outdoor",     "Jubilee Chalets glass building – day"),
    "06 - Residential Estate Entrance Road.jpg":  ("gallery",     "outdoor",     "Resort entrance road"),
    "07 - Guest Bathroom Interior.jpg":           ("rooms",       "room",        "Guest suite lounge with TV"),
    "08 - Reception Lounge Seating.jpg":          ("rooms",       "room",        "Executive suite lounge"),
    "09 - Estate Landscape Road View.jpg":        ("gallery",     "outdoor",     "Estate road and landscape"),
    "10 - Sunny Modern Neighborhood Street.jpg":  ("gallery",     "outdoor",     "Resort street – sunny day"),
    "11 - Family Group Seating.jpg":              ("gallery",     "general",     "Guests relaxing at the resort"),
    "12 - Estate Road and Buildings.jpg":         ("gallery",     "outdoor",     "Estate road and chalet buildings"),
    "13 - Guest Bathroom Shower Area.jpg":        ("rooms",       "room",        "Guest chalet kitchen area"),
    "14 - Banquet Hall Dining Setup.jpg":         ("gallery",     "events",      "Banquet hall – conference setup"),
    "15 - Buffet Kitchen Food Service.jpg":       ("gallery",     "dining",      "Buffet food service"),
    "16 - Restaurant Dining Lounge.jpg":          ("rooms",       "room",        "Executive suite interior"),
    "17 - Jubilee Chalets Exterior Day.jpg":      ("gallery",     "outdoor",     "Jubilee Chalets exterior – daytime"),
    "18 - Illuminated Glass Pavilion Night.jpg":  ("gallery",     "outdoor",     "Glass pavilion at night with pool"),
    "19 - Outdoor Sports Field.jpg":              ("gallery",     "recreation",  "Tennis court"),
    "20 - Living Room Lounge Interior.jpg":       ("rooms",       "room",        "Guest bedroom – master suite"),
    "21 - Swimming Pool and Chalets.jpg":         ("gallery",     "recreation",  "Swimming pool with guests"),
    "22 - Family Group Portrait.jpg":             ("gallery",     "general",     "Families enjoying the resort"),
    "23 - Conference Meeting Room.jpg":           ("gallery",     "events",      "Conference meeting room – boardroom"),
    "24 - Glass Pavilion Exterior Overcast.jpg":  ("gallery",     "outdoor",     "Glass pavilion exterior – overcast"),
    "25 - Celebration Group in White.jpg":        ("gallery",     "general",     "Christmas celebration at the resort"),
    "26 - Meeting Room Interior.jpg":             ("gallery",     "dining",      "Restaurant dining hall"),
    "27 - Plated Dining Meal.jpg":                ("gallery",     "dining",      "Plated meal – fried rice and fish"),
    "28 - Reflective Glass Tower Day.jpg":        ("gallery",     "outdoor",     "Jubilee Chalets glass tower – sunset"),
    "29 - Guests Swimming in Pool.jpg":           ("gallery",     "recreation",  "Guests in the pool"),
    "30 - Banquet Dining Hall.jpg":               ("gallery",     "dining",      "Panoramic glass dining room"),
    "31 - Golf Carts at Resort.jpg":              ("gallery",     "outdoor",     "Golf carts at the resort"),
    "32 - Football Field Aerial View.jpg":        ("gallery",     "recreation",  "Aerial – sports complex and waterfront"),
    "33 - Conference Auditorium Wide.jpg":        ("gallery",     "events",      "Conference auditorium – wide setup"),
    "34 - Jubilee Sports Complex Aerial.jpg":     ("gallery",     "outdoor",     "Chalet exterior street view"),
    "35 - Chalet Exterior Street View.jpg":       ("gallery",     "outdoor",     "Resort grounds night view"),
    "36 - Resort Grounds Night View.jpg":         ("gallery",     "outdoor",     "Resort grounds – night"),
    "37 - Soccer Field Players.jpg":              ("gallery",     "recreation",  "Kids playing football"),
    "38 - Guest Bedroom Interior.jpg":            ("rooms",       "room",        "Guest bedroom – upholstered headboard"),
}

# ── Which room image goes with which room category ───────────────────────────
# Maps the images that are room photos to the room category they best illustrate
ROOM_IMAGE_ASSIGNMENTS = [
    ("01 - Guest Bedroom Twin Beds.jpg",    "Standard Chalet",  True),   # primary
    ("03 - Guest Bedroom Double Bed.jpg",   "Standard Chalet",  False),
    ("38 - Guest Bedroom Interior.jpg",     "Standard Chalet",  False),
    ("20 - Living Room Lounge Interior.jpg","Deluxe Chalet",    True),   # primary
    ("16 - Restaurant Dining Lounge.jpg",   "Deluxe Chalet",    False),
    ("08 - Reception Lounge Seating.jpg",   "Family Suite",     True),   # primary
    ("07 - Guest Bathroom Interior.jpg",    "Family Suite",     False),
    ("13 - Guest Bathroom Shower Area.jpg", "Family Suite",     False),
]

# ── Which images seed which Experiences ──────────────────────────────────────
EXPERIENCE_IMAGE_ASSIGNMENTS = {
    "Swimming Pool":      "21 - Swimming Pool and Chalets.jpg",
    "Outdoor Recreation": "10 - Sunny Modern Neighborhood Street.jpg",
    "Restaurant Dining":  "26 - Meeting Room Interior.jpg",
    "Corporate Retreats": "14 - Banquet Hall Dining Setup.jpg",
    "Family Outings":     "11 - Family Group Seating.jpg",
    "Special Events":     "25 - Celebration Group in White.jpg",
}


class Command(BaseCommand):
    help = "Copy real Jubilee Chalets photos into media/ and seed database records"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Seeding real Jubilee Chalets images ==="))

        copied = 0
        missing = []

        # ── 1. Copy every image into its media subfolder ──────────────────
        self.stdout.write("Copying images to media/...")
        for filename, (subfolder, _, _) in IMAGE_MAP.items():
            src = IMAGE_SRC / filename
            if not src.exists():
                missing.append(filename)
                continue

            dest_dir = Path("media") / subfolder
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / filename

            if not dest.exists():
                shutil.copy2(src, dest)
                copied += 1

        if missing:
            self.stdout.write(self.style.WARNING(f"  ⚠ {len(missing)} files not found (skipped): {missing[:3]}..."))
        self.stdout.write(self.style.SUCCESS(f"  ✓ {copied} new files copied"))

        # ── 2. Gallery images ─────────────────────────────────────────────
        self.stdout.write("Creating gallery records...")
        gallery_created = 0
        for order, (filename, (subfolder, category, alt)) in enumerate(IMAGE_MAP.items()):
            if subfolder != "gallery":
                continue
            img_path = Path("media") / subfolder / filename
            if not img_path.exists():
                continue
            if GalleryImage.objects.filter(alt_text=alt).exists():
                continue
            with open(img_path, "rb") as f:
                gi = GalleryImage(
                    alt_text=alt,
                    caption=alt,
                    category=category,
                    display_order=order,
                    is_active=True,
                )
                gi.image.save(filename, File(f), save=True)
                gallery_created += 1
        self.stdout.write(self.style.SUCCESS(f"  ✓ {gallery_created} gallery images created"))

        # ── 3. Room images ────────────────────────────────────────────────
        self.stdout.write("Attaching images to rooms...")
        room_imgs_created = 0
        for filename, cat_name, is_primary in ROOM_IMAGE_ASSIGNMENTS:
            img_path = Path("media") / "rooms" / filename
            if not img_path.exists():
                continue
            try:
                cat = RoomCategory.objects.get(name=cat_name)
            except RoomCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  ⚠ Category '{cat_name}' not found – run seed_demo_data first"))
                continue

            rooms = Room.objects.filter(category=cat)
            if not rooms.exists():
                continue

            alt = IMAGE_MAP.get(filename, ("", "", "Unknown room"))[2]
            for room in rooms:
                # Only attach if this exact alt_text isn't already there
                if room.images.filter(alt_text=alt).exists():
                    continue
                with open(img_path, "rb") as f:
                    ri = RoomImage(
                        room=room,
                        alt_text=alt,
                        is_primary=is_primary,
                        display_order=0 if is_primary else 1,
                    )
                    ri.image.save(filename, File(f), save=True)
                    room_imgs_created += 1
        self.stdout.write(self.style.SUCCESS(f"  ✓ {room_imgs_created} room images attached"))

        # ── 4. Experience images ──────────────────────────────────────────
        self.stdout.write("Attaching images to experiences...")
        exp_updated = 0
        for exp_title, filename in EXPERIENCE_IMAGE_ASSIGNMENTS.items():
            img_path = Path("media") / "gallery" / filename
            if not img_path.exists():
                # also try rooms subfolder
                img_path = Path("media") / "rooms" / filename
            if not img_path.exists():
                continue
            try:
                exp = Experience.objects.get(title=exp_title)
            except Experience.DoesNotExist:
                continue
            if exp.image:
                continue  # already has one
            with open(img_path, "rb") as f:
                exp.image.save(filename, File(f), save=True)
                exp_updated += 1
        self.stdout.write(self.style.SUCCESS(f"  ✓ {exp_updated} experience images attached"))

        # ── 5. Logo → WebsiteSettings ─────────────────────────────────────
        self.stdout.write("Checking logo...")
        logo_path = Path("media") / "logo" / "04 - Jubilee Chalets Logo.jpg"
        settings = WebsiteSettings.get_settings()
        # WebsiteSettings has no logo field by default; we'll skip silently
        # if there's no field, but note where the file is.
        if logo_path.exists():
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ Logo saved to media/logo/04 - Jubilee Chalets Logo.jpg"
            ))
        else:
            self.stdout.write(self.style.WARNING("  ⚠ Logo file not found"))

        self.stdout.write(self.style.SUCCESS("\n=== Image seeding complete ==="))
        self.stdout.write("  Run the dev server and open http://localhost:5173 to see your photos.")
