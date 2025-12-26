import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { motion } from 'framer-motion'

const Layout = ({ children }) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

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
              {user?.is_anonymous_mode && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="badge badge-primary shadow-sm"
                >
                  🔒 Anonymous
                </motion.span>
              )}
              <div className="hidden sm:flex items-center space-x-3 px-4 py-2 bg-white/50 rounded-xl shadow-sm">
                <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                  <span className="text-white text-sm font-semibold">
                    {(user?.display_name || user?.username)?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <span className="text-sm font-medium text-gray-700">
                  {user?.display_name || user?.username}
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

