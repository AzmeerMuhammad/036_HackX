import { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import { historyAPI } from '../api/history'
import { consentAPI } from '../api/consent'
import { motion } from 'framer-motion'

const HistoryShare = () => {
  const [consents, setConsents] = useState([])
  const [generating, setGenerating] = useState(false)
  const [snapshotId, setSnapshotId] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadConsents()
  }, [])

  const loadConsents = async () => {
    try {
      const response = await consentAPI.status()
      setConsents(response.data)
    } catch (err) {
      console.error('Failed to load consents', err)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    setGenerating(true)

    try {
      const response = await historyAPI.generate()
      setSnapshotId(response.data.snapshot_id)
    } catch (err) {
      console.error('Failed to generate history snapshot:', err)
      const errorMessage = err.response?.data?.error || err.message || 'Failed to generate history snapshot'
      alert(errorMessage)
    } finally {
      setGenerating(false)
    }
  }

  const handleDownloadPDF = async () => {
    if (!snapshotId) {
      alert('Please generate history first')
      return
    }

    try {
      const response = await historyAPI.getPDF(snapshotId)
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `patient_history_${snapshotId}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      alert('Failed to download PDF')
    }
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
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Share History</h1>

        <div className="rounded-lg p-4 mb-6" style={{ background: 'rgba(241, 90, 42, 0.05)', border: '1px solid rgba(241, 90, 42, 0.2)' }}>
          <p className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}>
            Your complete history will be shared with professionals you've granted consent to.
            The report includes all journal entries, chat sessions, escalations, mood trends, risk assessments, and emotional patterns from your entire account history.
          </p>
        </div>

        {consents.length > 0 ? (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                Professionals with Consent
              </h2>
              <div className="space-y-3">
                {consents.map((consent) => (
                  <div
                    key={consent.id}
                    className="flex justify-between items-center p-4 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <div className="font-medium" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                        {consent.professional.user.display_name}
                      </div>
                      <div className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                        {consent.professional.specialization}
                      </div>
                    </div>
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                      Active
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Generate & Download</h2>
              <p className="mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                Generate a comprehensive PDF report of your complete history including all journal entries, chat sessions, and escalations. This report helps professionals with initial history-taking and provides a complete overview of your mental health journey.
              </p>
              <div className="flex space-x-4">
                <button
                  onClick={handleGenerate}
                  disabled={generating}
                  className="px-6 py-2 rounded-lg disabled:opacity-50 transition-colors"
                  style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
                >
                  {generating ? 'Generating...' : 'Generate History Report'}
                </button>
                {snapshotId && (
                  <button
                    onClick={handleDownloadPDF}
                    className="px-6 py-2 rounded-lg transition-colors"
                    style={{ background: '#10B981', color: 'white', fontFamily: "'Inter', sans-serif" }}
                  >
                    Download PDF
                  </button>
                )}
              </div>
              {snapshotId && (
                <p className="text-sm mt-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                  History snapshot #{snapshotId} generated successfully.
                </p>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-md p-8 text-center">
            <p className="mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
              You haven't granted consent to any professionals yet.
            </p>
            <a
              href="/professionals"
              className="font-medium"
              style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}
            >
              Browse Professionals
            </a>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default HistoryShare

