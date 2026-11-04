import { Outlet, Link } from 'react-router-dom'
import { motion } from 'framer-motion'

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-brand-light-grey flex">
      {/* Left panel — decorative */}
      <div
        className="hidden lg:flex lg:w-1/2 bg-brand-forest-green relative overflow-hidden"
        aria-hidden="true"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-brand-forest-green via-brand-dark-green to-brand-forest-green" />
        <div className="relative z-10 flex flex-col justify-between p-12 text-white">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center font-display font-bold text-lg">
              JC
            </div>
            <div>
              <div className="font-display font-bold text-lg leading-tight">Jubilee Chalets</div>
              <div className="text-white/60 text-xs tracking-wider">EPE · LAGOS</div>
            </div>
          </Link>
          <div>
            <blockquote className="font-display text-3xl font-bold leading-snug mb-4">
              "Escape the ordinary.<br />Experience serenity."
            </blockquote>
            <p className="text-white/70 text-sm leading-relaxed">
              Discover a refreshing destination for relaxation, memorable stays, and exceptional hospitality in Epe, Lagos.
            </p>
          </div>
          <p className="text-white/40 text-xs">© {new Date().getFullYear()} Jubilee Chalets Epe</p>
        </div>
        {/* Decorative circles */}
        <div className="absolute -top-32 -right-32 w-96 h-96 rounded-full bg-white/5" />
        <div className="absolute -bottom-48 -left-24 w-[30rem] h-[30rem] rounded-full bg-white/5" />
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <Link to="/" className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-9 h-9 rounded-xl bg-brand-dark-green flex items-center justify-center font-display font-bold text-base text-white">
              JC
            </div>
            <span className="font-display font-bold text-lg text-brand-dark-green">Jubilee Chalets</span>
          </Link>
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
          >
            <Outlet />
          </motion.div>
        </div>
      </div>
    </div>
  )
}
