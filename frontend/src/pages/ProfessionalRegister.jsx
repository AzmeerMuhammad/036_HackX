import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { motion } from 'framer-motion'

const ProfessionalRegister = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    password_confirm: '',
    display_name: '',
    email: '',
    is_professional: true,
    professional_type: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.password_confirm) {
      setError('Passwords do not match')
      return
    }

    if (!formData.professional_type) {
      setError('Please select your professional type')
      return
    }

    setLoading(true)

    try {
      await register(formData)
      // Always redirect to professional dashboard for professional signup
      navigate('/professional/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.password?.[0] || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-purple-blue py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Large floating orbs */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute -top-1/2 -left-1/2 w-full h-full bg-white rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-purple-300 rounded-full blur-3xl"
        />

        {/* Floating particles */}
        {[...Array(12)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-white/40 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              x: [0, Math.random() * 20 - 10, 0],
              opacity: [0.2, 0.6, 0.2],
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
              background: `radial-gradient(circle, ${
                i % 3 === 0 ? 'rgba(167, 139, 250, 0.15)' :
                i % 3 === 1 ? 'rgba(139, 92, 246, 0.1)' :
                'rgba(79, 172, 254, 0.12)'
              }, transparent)`,
            }}
            animate={{
              y: [0, -50 - Math.random() * 50, 0],
              x: [0, Math.random() * 60 - 30, 0],
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.6, 0.3],
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
            backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(167, 139, 250, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(79, 172, 254, 0.3) 0%, transparent 50%)',
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
              <div className="w-20 h-20 bg-gradient-primary rounded-2xl flex items-center justify-center shadow-xl mx-auto">
                <span className="text-white text-4xl font-bold">S</span>
              </div>
            </motion.div>
            <h2 className="text-3xl font-bold gradient-text mb-2">
              Join as a Professional
            </h2>
            <p className="text-gray-600">Create your professional account</p>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            {error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-red-50 border-2 border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center space-x-2"
              >
                <span>⚠️</span>
                <span className="text-sm">{error}</span>
              </motion.div>
            )}

            <div className="space-y-4">
              <div>
                <label htmlFor="professional_type" className="block text-sm font-medium text-gray-700 mb-2">
                  Professional Type <span className="text-red-500">*</span>
                </label>
                <select
                  id="professional_type"
                  name="professional_type"
                  required
                  value={formData.professional_type}
                  onChange={handleChange}
                  className="input-modern"
                >
                  <option value="">Select your profession</option>
                  <option value="psychiatrist">Psychiatrist</option>
                  <option value="therapist">Therapist</option>
                  <option value="psychologist">Psychologist</option>
                </select>
              </div>

              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                  Username <span className="text-red-500">*</span>
                </label>
                <input
                  id="username"
                  type="text"
                  name="username"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  className="input-modern"
                  placeholder="Choose a username"
                />
              </div>

              <div>
                <label htmlFor="display_name" className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name <span className="text-red-500">*</span>
                </label>
                <input
                  id="display_name"
                  type="text"
                  name="display_name"
                  required
                  value={formData.display_name}
                  onChange={handleChange}
                  className="input-modern"
                  placeholder="Your full name"
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email <span className="text-red-500">*</span>
                </label>
                <input
                  id="email"
                  type="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="input-modern"
                  placeholder="your.email@example.com"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password <span className="text-red-500">*</span>
                </label>
                <input
                  id="password"
                  type="password"
                  name="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="input-modern"
                  placeholder="Create a strong password"
                />
              </div>

              <div>
                <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700 mb-2">
                  Confirm Password <span className="text-red-500">*</span>
                </label>
                <input
                  id="password_confirm"
                  type="password"
                  name="password_confirm"
                  required
                  value={formData.password_confirm}
                  onChange={handleChange}
                  className="input-modern"
                  placeholder="Confirm your password"
                />
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full btn-primary text-base py-4 disabled:opacity-50 disabled:cursor-not-allowed mt-6"
            >
              {loading ? (
                <span className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Creating account...</span>
                </span>
              ) : (
                'Create Professional Account'
              )}
            </motion.button>

            <div className="text-center pt-4 space-y-2">
              <Link
                to="/login"
                className="block font-medium text-primary-600 hover:text-primary-700 transition-colors"
              >
                Already have an account? <span className="underline">Sign in</span>
              </Link>
              <Link
                to="/register"
                className="block text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                Register as a user instead
              </Link>
            </div>
          </form>
        </div>

        {/* Footer Text */}
        <p className="text-center text-white/80 text-sm">
          🔒 Your privacy is our priority
        </p>
      </motion.div>
    </div>
  )
}

export default ProfessionalRegister
