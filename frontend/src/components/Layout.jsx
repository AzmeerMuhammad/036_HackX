import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { authAPI } from '../api/auth'
import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

const Layout = ({ children }) => {
  const { user, logout, setUser } = useAuth()
  const navigate = useNavigate()
  const [isAnonymous, setIsAnonymous] = useState(user?.is_anonymous_mode ?? true)

  // Sync isAnonymous state with user object when it changes
  useEffect(() => {
    if (user?.is_anonymous_mode !== undefined) {
      setIsAnonymous(user.is_anonymous_mode)
    }
  }, [user?.is_anonymous_mode])

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const toggleAnonymousMode = async () => {
    const newAnonymousMode = !isAnonymous
    console.log('Toggling anonymous mode from', isAnonymous, 'to', newAnonymousMode)
    setIsAnonymous(newAnonymousMode)

    try {
      // Update backend
      console.log('Sending update to backend:', { is_anonymous_mode: newAnonymousMode })
      const response = await authAPI.updateMe({ is_anonymous_mode: newAnonymousMode })
      const updatedUser = response.data
      console.log('Backend response:', updatedUser)
      console.log('Updated is_anonymous_mode:', updatedUser.is_anonymous_mode)

      // Update context and localStorage with backend response
      setUser(updatedUser)
      localStorage.setItem('user', JSON.stringify(updatedUser))
      console.log('✓ Anonymous mode updated successfully')
    } catch (error) {
      console.error('Failed to update anonymous mode:', error)
      console.error('Error details:', error.response?.data)
      // Revert on error
      setIsAnonymous(!newAnonymousMode)
    }
  }

  // Check if user is a professional
  const isProfessional = user?.is_professional || user?.professional_type

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(to bottom right, #f5f3ff, #e0e7ff, #dbeafe)' }}>
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
                  <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center shadow-lg">
                    <span className="text-white text-xl font-bold">S</span>
                  </div>
                  <span className="text-2xl font-bold gradient-text hidden sm:block">
                    SafeSpace
                  </span>
                </motion.div>
              </Link>
            </div>
            <div className="flex items-center space-x-3 sm:space-x-4">
              {/* Anonymous Mode Toggle - Only show for regular users, not professionals */}
              {!isProfessional && (
                <motion.button
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={toggleAnonymousMode}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-xl transition-all shadow-sm ${
                    isAnonymous
                      ? 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                      : 'bg-white/50 text-gray-700 hover:bg-white'
                  }`}
                  title={isAnonymous ? 'Anonymous mode: ON' : 'Anonymous mode: OFF'}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {isAnonymous ? (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    ) : (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
                    )}
                  </svg>
                  <span className="text-xs font-medium hidden sm:inline">
                    {isAnonymous ? 'Anonymous' : 'Visible'}
                  </span>
                </motion.button>
              )}
              <div className="hidden sm:flex items-center space-x-3 px-4 py-2 bg-white/50 rounded-xl shadow-sm">
                <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                  <span className="text-white text-sm font-semibold">
                    {(user?.display_name || user?.username)?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <span className="text-sm font-medium text-gray-700">
                  {isAnonymous && !isProfessional ? 'Anonymous User' : (user?.display_name || user?.username)}
                </span>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 bg-white/50 hover:bg-white rounded-xl transition-all shadow-sm hover:shadow-md"
              >
                Logout
              </motion.button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {children}
        </motion.div>
      </main>
    </div>
  )
}

export default Layout

