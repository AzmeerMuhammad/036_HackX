import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { authAPI } from '../api/auth'
import { motion } from 'framer-motion'
import safespaceLogo from '../assets/safespace_logo.png'

const Login = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // First login to get tokens
      await login(username, password)

      // Then fetch complete user profile to get all fields including professional status
      const response = await authAPI.me()
      const userData = response.data

      // Debug: Log the complete userData
      console.log('Complete user data from /auth/me/:', userData)
      console.log('User data (stringified):', JSON.stringify(userData, null, 2))

      // Check if user is a professional and redirect accordingly
      // Check multiple possible field names and structures
      const isProfessional = userData?.is_professional === true ||
                           userData?.role === 'professional' ||
                           userData?.user_type === 'professional' ||
                           (userData?.professional_type && userData.professional_type !== '') ||
                           // Check nested user object in case backend returns different structure
                           userData?.user?.is_professional === true ||
                           userData?.user?.professional_type

      console.log('isProfessional:', isProfessional)
      console.log('Redirecting to:', isProfessional ? '/professional/dashboard' : '/home')

      navigate(isProfessional ? '/professional/dashboard' : '/home')
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden" style={{ background: '#F7F3EC', fontFamily: "'Inter', sans-serif" }}>
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Large floating orbs */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.1, 0.2, 0.1],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute -top-1/2 -left-1/2 w-full h-full rounded-full blur-3xl"
          style={{ background: 'rgba(241, 90, 42, 0.1)' }}
        />
        <motion.div
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.1, 0.2, 0.1],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute -bottom-1/2 -right-1/2 w-full h-full rounded-full blur-3xl"
          style={{ background: 'rgba(241, 90, 42, 0.08)' }}
        />

        {/* Floating particles */}
        {[...Array(12)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              background: 'rgba(241, 90, 42, 0.3)',
            }}
            animate={{
              y: [0, -30, 0],
              x: [0, Math.random() * 20 - 10, 0],
              opacity: [0.1, 0.3, 0.1],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 3 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 2,
              ease: "easeInOut"
            }}
          />
        ))}

        {/* Floating gradient circles */}
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={`circle-${i}`}
            className="absolute rounded-full"
            style={{
              width: `${100 + Math.random() * 200}px`,
              height: `${100 + Math.random() * 200}px`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              background: `radial-gradient(circle, rgba(241, 90, 42, ${0.08 + Math.random() * 0.05}), transparent)`,
            }}
            animate={{
              y: [0, -50 - Math.random() * 50, 0],
              x: [0, Math.random() * 60 - 30, 0],
              scale: [1, 1.2, 1],
              opacity: [0.2, 0.4, 0.2],
            }}
            transition={{
              duration: 8 + Math.random() * 6,
              repeat: Infinity,
              delay: Math.random() * 3,
              ease: "easeInOut"
            }}
          />
        ))}

        {/* Animated lines/waves */}
        <motion.div
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(241, 90, 42, 0.15) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(241, 90, 42, 0.1) 0%, transparent 50%)',
          }}
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-md w-full space-y-8 relative z-10"
      >
        {/* Card */}
        <div className="bg-white/95 backdrop-blur-lg p-10 rounded-3xl shadow-card-hover">
          {/* Logo and Title */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-block mb-4"
            >
              <img 
                src={safespaceLogo} 
                alt="SafeSpace" 
                className="h-20 sm:h-24 md:h-28 w-auto object-contain mx-auto"
                style={{ maxWidth: '240px' }}
              />
            </motion.div>
            <h2 className="text-3xl font-bold mb-2" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 800, color: '#3F3F3F' }}>
              Welcome Back
            </h2>
            <p style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F', opacity: 0.7 }}>Sign in to your SafeSpace account</p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-red-50 border-2 border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center space-x-2"
              >
                <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>{error}</span>
              </motion.div>
            )}

            <div className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="input-modern"
                  placeholder="Enter your username"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-modern"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full btn-primary text-base py-4 disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden"
            >
              {loading ? (
                <span className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Signing in...</span>
                </span>
              ) : (
                'Sign In'
              )}
            </motion.button>

            <div className="text-center pt-4 space-y-2">
              <Link
                to="/register"
                className="block font-medium transition-colors"
                style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#d14a1f'}
                onMouseLeave={(e) => e.currentTarget.style.color = '#F15A2A'}
              >
                Don't have an account? <span className="underline">Register</span>
              </Link>
              <Link
                to="/professional/register"
                className="block text-sm transition-colors"
                style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F', opacity: 0.7 }}
                onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
                onMouseLeave={(e) => e.currentTarget.style.opacity = '0.7'}
              >
                Register as a professional instead
              </Link>
            </div>
          </form>
        </div>

        {/* Footer Text */}
        <p className="text-center text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F', opacity: 0.6 }}>
          Your safe space for mental wellness
        </p>
      </motion.div>
    </div>
  )
}

export default Login
