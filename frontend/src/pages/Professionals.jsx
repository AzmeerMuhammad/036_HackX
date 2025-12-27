import { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import { professionalsAPI } from '../api/professionals'
import { consentAPI } from '../api/consent'
import { motion } from 'framer-motion'

const Professionals = () => {
  const [professionals, setProfessionals] = useState([])
  const [consents, setConsents] = useState([])
  const [loading, setLoading] = useState(true)
  const [showApply, setShowApply] = useState(false)
  const [applyForm, setApplyForm] = useState({
    specialization: '',
    availability: '',
    city: '',
  })
  const [applying, setApplying] = useState(false)

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

  const handleApply = async (e) => {
    e.preventDefault()
    setApplying(true)

    try {
      await professionalsAPI.apply(applyForm)
      alert('Application submitted! It will be reviewed by administrators.')
      setShowApply(false)
      setApplyForm({ specialization: '', availability: '', city: '' })
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to submit application')
    } finally {
      setApplying(false)
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
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Verified Professionals</h1>
          <button
            onClick={() => setShowApply(!showApply)}
            className="px-4 py-2 rounded-lg transition-colors"
            style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
          >
            Apply to Become Professional
          </button>
        </div>

        {showApply && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-md p-6 mb-6"
          >
            <h2 className="text-xl font-semibold mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Apply as Professional</h2>
            <form onSubmit={handleApply} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                  Specialization *
                </label>
                <input
                  type="text"
                  required
                  value={applyForm.specialization}
                  onChange={(e) => setApplyForm({ ...applyForm, specialization: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                  placeholder="e.g., Clinical Psychology"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                  Availability *
                </label>
                <input
                  type="text"
                  required
                  value={applyForm.availability}
                  onChange={(e) => setApplyForm({ ...applyForm, availability: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                  placeholder="e.g., Mon-Fri 9AM-5PM"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                  City
                </label>
                <input
                  type="text"
                  value={applyForm.city}
                  onChange={(e) => setApplyForm({ ...applyForm, city: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                  placeholder="e.g., Karachi"
                />
              </div>
              <div className="flex space-x-4">
                <button
                  type="submit"
                  disabled={applying}
                  className="px-6 py-2 rounded-lg disabled:opacity-50 transition-colors"
                  style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
                >
                  {applying ? 'Submitting...' : 'Submit Application'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowApply(false)}
                  className="px-6 py-2 rounded-lg transition-colors"
                  style={{ background: '#E5E7EB', fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </motion.div>
        )}

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

