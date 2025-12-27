import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import ProfileDashboard from './ProfileDashboard'

const Layout = ({ children }) => {
  const { user, logout, setUser } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [showProfileDashboard, setShowProfileDashboard] = useState(false)

  // Determine if back button should be shown (not on Home or ProfessionalDashboard pages)
  const showBackButton = location.pathname !== '/home' && location.pathname !== '/professional/dashboard'

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const handleOpenProfile = () => {
    setShowProfileDashboard(true)
  }

  const handleCloseProfile = () => {
    setShowProfileDashboard(false)
  }

  return (
    <div className="min-h-screen" style={{ background: '#F7F3EC', fontFamily: "'Inter', sans-serif" }}>
      <nav className="glass shadow-soft sticky top-0 z-50 border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center">
              <Link to="/home" className="flex items-center space-x-3">
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center space-x-2"
                >
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ background: '#F15A2A' }}>
                    <span className="text-white text-xl font-bold">S</span>
                  </div>
                  <span className="text-2xl font-bold hidden sm:block" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                    SafeSpace
                  </span>
                </motion.div>
              </Link>
            </div>
            <div className="flex items-center space-x-3 sm:space-x-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleOpenProfile}
                className="hidden sm:flex items-center space-x-3 px-4 py-2 bg-white/50 hover:bg-white rounded-xl shadow-sm transition-all cursor-pointer"
              >
                <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: '#F15A2A' }}>
                  <span className="text-white text-sm font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                    {(user?.display_name || user?.username)?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <span className="text-sm font-medium" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                  {user?.display_name || user?.username}
                </span>
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium bg-white/50 hover:bg-white rounded-xl transition-all shadow-sm hover:shadow-md"
                style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}
              >
                Logout
              </motion.button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 relative">
        {showBackButton && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate(-1)}
            className="absolute top-4 left-4 sm:left-6 px-4 py-2 text-sm font-medium bg-white hover:bg-white/90 rounded-xl transition-all shadow-md hover:shadow-lg flex items-center gap-2 z-10"
            style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span>Back</span>
          </motion.button>
        )}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className={showBackButton ? 'pt-14' : ''}
        >
          {children}
        </motion.div>
      </main>

      {/* Profile Dashboard Window */}
      <AnimatePresence>
        {showProfileDashboard && (
          <ProfileDashboard
            user={user}
            onClose={handleCloseProfile}
            onLogout={() => {
              handleLogout()
            }}
            onUserUpdate={(updatedUser) => {
              setUser(updatedUser)
              localStorage.setItem('user', JSON.stringify(updatedUser))
            }}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

export default Layout

