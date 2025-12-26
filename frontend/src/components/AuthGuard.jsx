import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const AuthGuard = ({ children }) => {
  const { user, loading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!loading && !user) {
      navigate('/login')
    }
  }, [user, loading, navigate])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(to bottom right, #f5f3ff, #e0e7ff, #dbeafe)' }}>
        <div className="flex flex-col items-center space-y-4">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-primary-200"></div>
            <div className="absolute top-0 left-0 animate-spin rounded-full h-16 w-16 border-t-4 border-primary-600"></div>
          </div>
          <p className="text-gray-600 font-medium">Loading SafeSpace...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return children
}

export default AuthGuard

