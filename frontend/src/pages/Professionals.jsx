import { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import { professionalsAPI } from '../api/professionals'
import { consentAPI } from '../api/consent'
import { motion } from 'framer-motion'

const Professionals = () => {
  const [professionals, setProfessionals] = useState([])
  const [consents, setConsents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [profsRes, consentsRes] = await Promise.all([
        professionalsAPI.list(),
        consentAPI.status(),
      ])
      // Handle both paginated (results) and non-paginated (direct array) responses
      const professionalsList = Array.isArray(profsRes.data) 
        ? profsRes.data 
        : (profsRes.data.results || [])
      
      console.log('Professionals API Response:', profsRes.data)
      console.log('Professionals List:', professionalsList)
      
      setProfessionals(professionalsList)
      setConsents(consentsRes.data || [])
    } catch (err) {
      console.error('Failed to load data', err)
      console.error('Error details:', err.response?.data || err.message)
      setProfessionals([])
      setConsents([])
    } finally {
      setLoading(false)
    }
  }

  const handleGrantConsent = async (professionalId) => {
    if (!window.confirm('Grant consent to share your history with this professional?')) return

    try {
      await consentAPI.grant(professionalId)
      await loadData()
      alert('Consent granted successfully')
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to grant consent')
    }
  }

  const hasConsent = (professionalId) => {
    return consents.some(c => c.professional.id === professionalId && c.active)
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: '#F15A2A' }}></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Verified Professionals</h1>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {professionals.map((prof, idx) => (
            <motion.div
              key={prof.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="bg-white rounded-xl shadow-md p-6"
            >
              <h3 className="text-xl font-semibold mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                {prof.user.display_name}
              </h3>
              <p className="font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}>{prof.specialization}</p>
              {prof.city && <p className="text-sm mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>📍 {prof.city}</p>}
              {prof.availability && (
                <p className="text-sm mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>⏰ {prof.availability}</p>
              )}
              {hasConsent(prof.id) ? (
                <div className="bg-green-50 border border-green-200 rounded-lg p-2 text-sm text-center" style={{ fontFamily: "'Inter', sans-serif", color: '#10B981' }}>
                  Consent Granted
                </div>
              ) : (
                <button
                  onClick={() => handleGrantConsent(prof.id)}
                  className="w-full py-2 rounded-lg transition-colors"
                  style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
                >
                  Grant Consent
                </button>
              )}
            </motion.div>
          ))}
        </div>

        {professionals.length === 0 && (
          <div className="bg-white rounded-xl shadow-md p-8 text-center">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <p className="text-lg font-semibold mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
              No verified professionals available.
            </p>
            <p className="text-sm text-gray-600 mb-4" style={{ fontFamily: "'Inter', sans-serif" }}>
              Professionals need to be verified by an administrator before they appear here.
            </p>
            <p className="text-xs text-gray-500" style={{ fontFamily: "'Inter', sans-serif" }}>
              If you're an admin, verify professionals in Django Admin or run: <code className="bg-gray-100 px-2 py-1 rounded">python manage.py create_demo_data</code>
            </p>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default Professionals

