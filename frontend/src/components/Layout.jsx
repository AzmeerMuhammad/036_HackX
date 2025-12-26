import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { motion } from 'framer-motion'

const Layout = ({ children }) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-sm border-b border-blue-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/home" className="flex items-center space-x-2">
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="text-2xl font-bold text-primary-600"
                >
                  SafeSpace
                </motion.div>
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              {user?.is_anonymous_mode && (
                <span className="px-3 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                  Anonymous Mode
                </span>
              )}
              <span className="text-sm text-gray-700">{user?.display_name || user?.username}</span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}

export default Layout

