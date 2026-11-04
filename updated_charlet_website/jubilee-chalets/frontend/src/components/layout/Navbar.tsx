import { useState, useEffect } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X, ChevronDown, User, LogOut, LayoutDashboard } from 'lucide-react'
import { useAuth } from '@/features/authentication/AuthContext'
import { cn } from '@/utils'
import { toast } from 'sonner'

const navLinks = [
  { label: 'Home', to: '/' },
  { label: 'Accommodation', to: '/accommodation' },
  { label: 'Experiences', to: '/experiences' },
  { label: 'Dining', to: '/dining' },
  { label: 'Events', to: '/events' },
  { label: 'Gallery', to: '/gallery' },
  { label: 'About', to: '/about' },
  { label: 'Contact', to: '/contact' },
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Close mobile menu on route change
  useEffect(() => { setMenuOpen(false) }, [navigate])

  const handleLogout = async () => {
    try {
      await logout()
      toast.success('Logged out successfully')
      navigate('/')
    } catch {
      toast.error('Logout failed')
    }
  }

  const isTransparent = !scrolled && !menuOpen

  return (
    <header
      className={cn(
        'fixed top-0 inset-x-0 z-40 transition-all duration-300',
        isTransparent
          ? 'bg-transparent'
          : 'bg-white shadow-sm border-b border-gray-100',
      )}
    >
      <div className="container-xl">
        <div className="flex items-center justify-between h-18 px-4 sm:px-6 lg:px-8">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 shrink-0">
            <div className={cn(
              'w-10 h-10 rounded-xl flex items-center justify-center font-display font-bold text-lg transition-colors',
              isTransparent ? 'bg-white/20 text-white' : 'bg-brand-dark-green text-white',
            )}>
              JC
            </div>
            <div className="leading-none">
              <span className={cn(
                'font-display font-bold text-lg transition-colors leading-tight block',
                isTransparent ? 'text-white' : 'text-brand-dark-green',
              )}>
                Jubilee Chalets
              </span>
              <span className={cn(
                'text-xs tracking-wider transition-colors',
                isTransparent ? 'text-white/70' : 'text-gray-500',
              )}>
                EPE · LAGOS
              </span>
            </div>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden lg:flex items-center gap-1" aria-label="Main navigation">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === '/'}
                className={({ isActive }) => cn(
                  'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isTransparent
                    ? isActive
                      ? 'text-white bg-white/20'
                      : 'text-white/90 hover:text-white hover:bg-white/10'
                    : isActive
                      ? 'text-brand-dark-green bg-brand-light-green'
                      : 'text-gray-700 hover:text-brand-dark-green hover:bg-brand-light-green',
                )}
              >
                {link.label}
              </NavLink>
            ))}
          </nav>

          {/* Right side */}
          <div className="hidden lg:flex items-center gap-3">
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isTransparent
                      ? 'text-white hover:bg-white/10'
                      : 'text-gray-700 hover:bg-brand-light-green hover:text-brand-dark-green',
                  )}
                  aria-expanded={userMenuOpen}
                  aria-haspopup="true"
                >
                  <div className={cn(
                    'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold',
                    isTransparent ? 'bg-white/20 text-white' : 'bg-brand-dark-green text-white',
                  )}>
                    {user?.first_name?.[0]?.toUpperCase() ?? 'U'}
                  </div>
                  <span>{user?.first_name}</span>
                  <ChevronDown className={cn('w-4 h-4 transition-transform', userMenuOpen && 'rotate-180')} />
                </button>

                <AnimatePresence>
                  {userMenuOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 5 }}
                      transition={{ duration: 0.15 }}
                      className="absolute right-0 mt-2 w-52 bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-50"
                      onMouseLeave={() => setUserMenuOpen(false)}
                    >
                      <Link
                        to="/dashboard"
                        className="flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:bg-brand-light-green hover:text-brand-dark-green transition-colors"
                        onClick={() => setUserMenuOpen(false)}
                      >
                        <LayoutDashboard className="w-4 h-4" />
                        My Dashboard
                      </Link>
                      <Link
                        to="/dashboard/profile"
                        className="flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:bg-brand-light-green hover:text-brand-dark-green transition-colors"
                        onClick={() => setUserMenuOpen(false)}
                      >
                        <User className="w-4 h-4" />
                        My Profile
                      </Link>
                      {user?.is_staff && (
                        <Link
                          to="/admin"
                          className="flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:bg-brand-light-green hover:text-brand-dark-green transition-colors"
                          onClick={() => setUserMenuOpen(false)}
                        >
                          <LayoutDashboard className="w-4 h-4" />
                          Admin Dashboard
                        </Link>
                      )}
                      <div className="border-t border-gray-100 mt-1 pt-1">
                        <button
                          onClick={handleLogout}
                          className="flex items-center gap-3 w-full px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors"
                        >
                          <LogOut className="w-4 h-4" />
                          Sign Out
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <Link
                to="/login"
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                  isTransparent
                    ? 'text-white hover:bg-white/10'
                    : 'text-gray-700 hover:text-brand-dark-green',
                )}
              >
                Sign In
              </Link>
            )}
            <Link to="/accommodation" className="btn-primary text-sm px-5 py-2.5">
              Book Now
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className={cn(
              'lg:hidden p-2 rounded-lg transition-colors',
              isTransparent ? 'text-white hover:bg-white/10' : 'text-brand-black hover:bg-gray-100',
            )}
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={menuOpen}
          >
            {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25, ease: 'easeInOut' }}
            className="lg:hidden bg-white border-t border-gray-100 overflow-hidden"
          >
            <nav className="px-4 py-4 space-y-1" aria-label="Mobile navigation">
              {navLinks.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.to === '/'}
                  onClick={() => setMenuOpen(false)}
                  className={({ isActive }) => cn(
                    'block px-4 py-3 rounded-xl text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-brand-light-green text-brand-dark-green'
                      : 'text-gray-700 hover:bg-gray-50',
                  )}
                >
                  {link.label}
                </NavLink>
              ))}
              <div className="pt-3 border-t border-gray-100 space-y-2">
                {isAuthenticated ? (
                  <>
                    <Link
                      to="/dashboard"
                      onClick={() => setMenuOpen(false)}
                      className="block px-4 py-3 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      My Dashboard
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-3 rounded-xl text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
                    >
                      Sign Out
                    </button>
                  </>
                ) : (
                  <Link
                    to="/login"
                    onClick={() => setMenuOpen(false)}
                    className="block px-4 py-3 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Sign In
                  </Link>
                )}
                <Link
                  to="/accommodation"
                  onClick={() => setMenuOpen(false)}
                  className="btn-primary w-full justify-center"
                >
                  Book Now
                </Link>
              </div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
