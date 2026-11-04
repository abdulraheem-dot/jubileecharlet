import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Calendar, User, Lock, LogOut, ChevronRight } from 'lucide-react'
import { useAuth } from '@/features/authentication/AuthContext'
import { toast } from 'sonner'
import { cn } from '@/utils'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import ScrollToTop from '@/components/common/ScrollToTop'

const sidebarLinks = [
  { label: 'Overview', to: '/dashboard', icon: LayoutDashboard, end: true },
  { label: 'My Bookings', to: '/dashboard/bookings', icon: Calendar },
  { label: 'Profile', to: '/dashboard/profile', icon: User },
  { label: 'Change Password', to: '/dashboard/change-password', icon: Lock },
]

export default function DashboardLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    toast.success('Logged out successfully')
    navigate('/')
  }

  return (
    <>
      <ScrollToTop />
      <Navbar />
      <div className="min-h-screen bg-brand-light-grey pt-18">
        <div className="container-xl px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Sidebar */}
            <aside className="lg:w-64 shrink-0">
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                {/* User info */}
                <div className="bg-brand-dark-green p-5 text-white">
                  <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center font-display font-bold text-xl mb-3">
                    {user?.first_name?.[0]?.toUpperCase() ?? 'U'}
                  </div>
                  <div className="font-semibold text-sm">{user?.first_name} {user?.last_name}</div>
                  <div className="text-white/60 text-xs mt-0.5 truncate">{user?.email}</div>
                </div>

                <nav className="p-2" aria-label="Dashboard navigation">
                  {sidebarLinks.map(({ label, to, icon: Icon, end }) => (
                    <NavLink
                      key={to}
                      to={to}
                      end={end}
                      className={({ isActive }) => cn(
                        'flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-medium transition-colors group',
                        isActive
                          ? 'bg-brand-light-green text-brand-dark-green'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-brand-dark-green',
                      )}
                    >
                      <Icon className="w-4 h-4 shrink-0" />
                      <span className="flex-1">{label}</span>
                      <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </NavLink>
                  ))}
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-3 px-3 py-3 w-full rounded-xl text-sm font-medium text-red-600 hover:bg-red-50 transition-colors mt-1"
                  >
                    <LogOut className="w-4 h-4" />
                    Sign Out
                  </button>
                </nav>
              </div>
            </aside>

            {/* Main content */}
            <main className="flex-1 min-w-0">
              <Outlet />
            </main>
          </div>
        </div>
      </div>
      <Footer />
    </>
  )
}
