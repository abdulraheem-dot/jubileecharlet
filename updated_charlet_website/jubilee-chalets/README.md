# Jubilee Chalets Epe — Premium Resort & Hotel Booking Website

A complete, production-ready full-stack web application for Jubilee Chalets Epe, a resort and accommodation business in Epe, Lagos State, Nigeria.

## Tech Stack

| Layer       | Technology                                             |
|-------------|--------------------------------------------------------|
| Frontend    | React 18, TypeScript, Vite, Tailwind CSS, Framer Motion |
| State       | TanStack Query, React Hook Form, Zod                   |
| Backend     | Python, Django 5, Django REST Framework, Simple JWT    |
| Database    | SQLite (dev) / PostgreSQL (production)                 |
| Payments    | Paystack (Nigerian payment gateway)                     |
| Images      | Cloudinary (production) / local media (dev)             |
| API Docs    | drf-spectacular (OpenAPI/Swagger)                       |

## Project Structure

```
jubilee-chalets/
├── frontend/          # React + Vite + TypeScript
│   └── src/
│       ├── components/  # Reusable UI components
│       ├── layouts/     # Page layout wrappers
│       ├── pages/       # Route-level pages
│       ├── features/    # Feature-based modules (auth, bookings, etc.)
│       ├── services/    # API client and service layer
│       ├── types/       # TypeScript type definitions
│       └── utils/       # Utility functions
├── backend/           # Django + DRF
│   ├── config/         # Django project settings
│   ├── accounts/       # User auth & profiles
│   ├── accommodation/  # Rooms, categories, amenities
│   ├── bookings/       # Booking engine & cancellations
│   ├── payments/       # Paystack integration
│   ├── experiences/    # Resort experiences
│   ├── dining/         # Restaurant menu
│   ├── events/         # Event venues & enquiries
│   ├── gallery/        # Photo gallery
│   ├── enquiries/      # Contact, testimonials, FAQs, newsletter
│   └── website/        # Site settings & admin dashboard
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your values (or use defaults for development)

# Run migrations
python manage.py migrate

# Seed demo data (optional — clearly labelled as demo)
python manage.py seed_demo_data

# Create a superuser
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

The backend runs on `http://localhost:8000`.

**Django Admin** is available at `http://localhost:8000/admin/`.

**API Documentation** (Swagger) is at `http://localhost:8000/api/docs/`.

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create env file
cp .env.example .env
# Edit if your backend URL differs

# Start dev server
npm run dev
```

The frontend runs on `http://localhost:5173`.

The Vite dev server proxies `/api` requests to the backend automatically.

## Demo Accounts

After running `seed_demo_data`:

| Role  | Email                    | Password    |
|-------|--------------------------|-------------|
| Admin | admin@jubileechalets.com| demo12345   |
| Guest | guest@example.com        | demo12345   |

All seeded data is clearly labelled with `[DEMO]` and should be replaced before production use.

## Key Features

### Public
- Premium homepage with hero, booking search bar, room previews, experiences, gallery, testimonials, location map
- Accommodation listing with filters (category, price, occupancy) and sorting
- Room detail pages with image gallery, amenities, and inline booking form
- Experiences, Dining, Events, Gallery, About, and Contact pages
- User registration and login (JWT authentication)
- Newsletter subscription

### Booking System
- Real-time room availability checking (server-side)
- Booking creation with server-validated pricing (never trusts frontend prices)
- Double-booking prevention via `SELECT FOR UPDATE` row-level locking
- Booking statuses: pending → awaiting_payment → confirmed → checked_in → checked_out
- Cancellation request workflow
- Unique booking references (JC-XXXXXXXX format)

### Payment Integration
- Paystack integration for Nigerian payments (NGN)
- Payment initialization through backend (secret key never exposed to frontend)
- Server-side payment verification via Paystack API
- Webhook signature validation and idempotent processing
- Mock payment mode when credentials not configured (clearly labelled)
- Amount verification (protects against partial payment attacks)

### Customer Dashboard
- Booking overview with stats
- Booking list with status filters
- Booking detail with price breakdown
- Payment initiation
- Cancellation requests
- Profile management
- Password change

### Admin (Django Admin)
- Room, category, and amenity management
- Booking management and status updates
- Payment records
- Content management (experiences, menu, gallery, FAQs, testimonials)
- Contact and event enquiry management
- Website settings (contact info, policies, social links)
- Admin dashboard summary stats

## API Endpoints

### Authentication
| Method | Endpoint                        | Description              |
|--------|---------------------------------|--------------------------|
| POST   | /api/auth/register/             | Register new user        |
| POST   | /api/auth/login/               | Login (returns JWT)      |
| POST   | /api/auth/logout/               | Logout (blacklist token) |
| POST   | /api/auth/token/refresh/        | Refresh access token     |
| GET    | /api/auth/profile/              | Get current user profile |
| PATCH  | /api/auth/profile/              | Update profile           |
| POST   | /api/auth/password-change/     | Change password           |
| POST   | /api/auth/password-reset/      | Request password reset    |
| POST   | /api/auth/password-reset/confirm/ | Confirm password reset  |

### Rooms
| Method | Endpoint                        | Description              |
|--------|---------------------------------|--------------------------|
| GET    | /api/rooms/                    | List rooms (with filters)|
| GET    | /api/rooms/:slug/              | Room detail              |
| GET    | /api/rooms/categories/         | List room categories     |
| GET    | /api/rooms/availability/       | Check availability       |

### Bookings
| Method | Endpoint                        | Description              |
|--------|---------------------------------|--------------------------|
| POST   | /api/bookings/                  | Create booking            |
| GET    | /api/bookings/                  | List user's bookings      |
| GET    | /api/bookings/:id/              | Booking detail            |
| POST   | /api/bookings/:id/cancel/       | Request cancellation      |
| GET    | /api/dashboard/summary/         | Dashboard stats           |

### Payments
| Method | Endpoint                        | Description              |
|--------|---------------------------------|--------------------------|
| POST   | /api/payments/initialize/      | Initialize Paystack payment|
| GET    | /api/payments/verify/:ref/      | Verify payment            |
| POST   | /api/payments/webhook/         | Paystack webhook handler  |

### Content
| Method | Endpoint                        | Description              |
|--------|---------------------------------|--------------------------|
| GET    | /api/experiences/               | List experiences          |
| GET    | /api/menu/                      | List menu items           |
| GET    | /api/menu/categories/           | List menu categories      |
| GET    | /api/gallery/                   | List gallery images       |
| GET    | /api/events/venues/             | List event venues         |
| POST   | /api/events/enquiries/          | Submit event enquiry      |
| GET    | /api/faqs/                      | List FAQs                 |
| GET    | /api/testimonials/              | List testimonials         |
| POST   | /api/contact/                   | Submit contact form       |
| POST   | /api/newsletter/subscribe/      | Subscribe to newsletter   |
| GET    | /api/website/settings/         | Get site settings         |

## Security

- Environment variables for all secrets (`.env` — never committed)
- JWT authentication with token refresh and blacklisting
- Server-side pricing validation (frontend prices never trusted)
- `SELECT FOR UPDATE` for concurrent booking protection
- Paystack webhook signature verification
- CORS restricted to approved origins
- Input validation on frontend (Zod) and backend (DRF serializers)
- Password hashing via Django's built-in system
- No card data stored (Paystack handles PCI compliance)
- Custom exception handler prevents stack trace exposure

## Deployment

### Backend (Production)

1. Set `DEBUG=False` in `.env`
2. Configure `DATABASE_URL` for PostgreSQL
3. Set up Cloudinary credentials for image storage
4. Configure Paystack with real credentials
5. Set `CORS_ALLOWED_ORIGINS` to your production frontend URL
6. Configure SMTP email settings
7. Run `python manage.py migrate`
8. Run `python manage.py collectstatic`
9. Use Gunicorn: `gunicorn config.wsgi:application`
10. Use a reverse proxy (nginx) for static files and HTTPS

### Frontend (Production)

1. Set `VITE_API_URL` to your production backend URL
2. Build: `npm run build`
3. Deploy the `dist/` folder to your hosting platform

## Testing

### Backend
```bash
cd backend
python manage.py test
```

### Frontend
```bash
cd frontend
npm run test
```

## Important Notes

- All demo data is clearly labelled with `[DEMO]` and must be replaced before production use.
- Paystack operates in mock mode when credentials are not configured or are placeholder values.
- The application uses SQLite by default for easy local development. Switch to PostgreSQL for production.
- Image uploads use local media storage in development. Configure Cloudinary for production.
- No fake reviews, testimonials, or business claims are seeded. All seeded content is clearly marked as demo.

## License

This project is built for Jubilee Chalets Epe. All rights reserved.
