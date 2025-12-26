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
      alert('Failed to generate history snapshot')
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Share History</h1>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800">
            Your history will be shared with professionals you've granted consent to. 
            History includes journal summaries, themes, risk trends, and chat highlights from the last 7 days.
          </p>
        </div>

        {consents.length > 0 ? (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Professionals with Consent
              </h2>
              <div className="space-y-3">
                {consents.map((consent) => (
                  <div
                    key={consent.id}
                    className="flex justify-between items-center p-4 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <div className="font-medium text-gray-900">
                        {consent.professional.user.display_name}
                      </div>
                      <div className="text-sm text-gray-600">
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
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Generate & Download</h2>
              <p className="text-gray-600 mb-4">
                Generate a branded PDF report of your 7-day history that you can share with professionals.
              </p>
              <div className="flex space-x-4">
                <button
                  onClick={handleGenerate}
                  disabled={generating}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
                >
                  {generating ? 'Generating...' : 'Generate History Report'}
                </button>
                {snapshotId && (
                  <button
                    onClick={handleDownloadPDF}
                    className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Download PDF
                  </button>
                )}
              </div>
              {snapshotId && (
                <p className="text-sm text-gray-600 mt-4">
                  History snapshot #{snapshotId} generated successfully.
                </p>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-md p-8 text-center">
            <p className="text-gray-600 mb-4">
              You haven't granted consent to any professionals yet.
            </p>
            <a
              href="/professionals"
              className="text-primary-600 hover:text-primary-700 font-medium"
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

