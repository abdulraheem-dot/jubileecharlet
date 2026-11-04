import { Outlet } from 'react-router-dom'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import ScrollToTop from '@/components/common/ScrollToTop'
import BackToTop from '@/components/common/BackToTop'

export default function PublicLayout() {
  return (
    <>
      <ScrollToTop />
      <Navbar />
      <main>
        <Outlet />
      </main>
      <Footer />
      <BackToTop />
    </>
  )
}
