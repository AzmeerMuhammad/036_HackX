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
      const [profsRes, consentsRes] = await Promise.all([
        professionalsAPI.list(),
        consentAPI.status(),
      ])
      setProfessionals(profsRes.data.results || profsRes.data)
      setConsents(consentsRes.data)
    } catch (err) {
      console.error('Failed to load data', err)
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
            <p style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>No verified professionals available.</p>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default Professionals

