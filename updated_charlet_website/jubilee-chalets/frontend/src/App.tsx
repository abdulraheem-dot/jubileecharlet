import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/features/authentication/AuthContext'
import ProtectedRoute from '@/components/common/ProtectedRoute'

// Layouts
import PublicLayout from '@/layouts/PublicLayout'
import AuthLayout from '@/layouts/AuthLayout'
import DashboardLayout from '@/layouts/DashboardLayout'

// Public pages
import HomePage from '@/pages/HomePage'
import AccommodationPage from '@/pages/AccommodationPage'
import RoomDetailPage from '@/pages/RoomDetailPage'
import ExperiencesPage from '@/pages/ExperiencesPage'
import DiningPage from '@/pages/DiningPage'
import EventsPage from '@/pages/EventsPage'
import GalleryPage from '@/pages/GalleryPage'
import AboutPage from '@/pages/AboutPage'
import ContactPage from '@/pages/ContactPage'
import PaymentResultPage from '@/pages/PaymentResultPage'

// Auth pages
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import ForgotPasswordPage from '@/pages/auth/ForgotPasswordPage'

// Dashboard pages
import DashboardOverviewPage from '@/pages/dashboard/DashboardOverviewPage'
import DashboardBookingsPage from '@/pages/dashboard/DashboardBookingsPage'
import BookingDetailPage from '@/pages/dashboard/BookingDetailPage'
import ProfilePage from '@/pages/dashboard/ProfilePage'
import ChangePasswordPage from '@/pages/dashboard/ChangePasswordPage'

// Simple policy pages
function PolicyPage({ title, content }: { title: string; content: string }) {
  return (
    <div className="pt-18 min-h-screen bg-white">
      <div className="container-xl px-4 sm:px-6 lg:px-8 py-16 max-w-3xl">
        <h1 className="font-display text-4xl font-bold text-brand-black mb-8">{title}</h1>
        <div className="prose text-gray-700 leading-relaxed">
          <p>{content}</p>
          <p className="text-gray-500 text-sm mt-8">
            These policies are subject to change. Please contact us for the most current version.
          </p>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public routes */}
        <Route element={<PublicLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/accommodation" element={<AccommodationPage />} />
          <Route path="/accommodation/:slug" element={<RoomDetailPage />} />
          <Route path="/experiences" element={<ExperiencesPage />} />
          <Route path="/dining" element={<DiningPage />} />
          <Route path="/events" element={<EventsPage />} />
          <Route path="/gallery" element={<GalleryPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/payment/result" element={<PaymentResultPage />} />
          <Route
            path="/privacy-policy"
            element={<PolicyPage title="Privacy Policy" content="Our privacy policy details how we collect, use, and protect your personal information. Contact us for the full policy document." />}
          />
          <Route
            path="/terms"
            element={<PolicyPage title="Terms & Conditions" content="Our terms and conditions govern your use of this website and our services. Contact us for the full terms document." />}
          />
          <Route
            path="/cancellation-policy"
            element={<PolicyPage title="Cancellation Policy" content="Our cancellation policy outlines the conditions under which bookings may be cancelled and any applicable fees. Contact us for full details." />}
          />
        </Route>

        {/* Auth routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        </Route>

        {/* Dashboard routes — require auth */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<DashboardOverviewPage />} />
          <Route path="/dashboard/bookings" element={<DashboardBookingsPage />} />
          <Route path="/dashboard/bookings/:id" element={<BookingDetailPage />} />
          <Route path="/dashboard/profile" element={<ProfilePage />} />
          <Route path="/dashboard/change-password" element={<ChangePasswordPage />} />
        </Route>

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}
