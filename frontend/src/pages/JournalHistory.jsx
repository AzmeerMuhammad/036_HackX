import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { journalAPI } from '../api/journal'
import { motion } from 'framer-motion'
import DataTable from '../components/DataTable'

const JournalHistory = () => {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadEntries()
  }, [])

  const loadEntries = async () => {
    try {
      const response = await journalAPI.list()
      setEntries(response.data.results || response.data)
    } catch (err) {
      setError('Failed to load journal entries')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this entry? This action cannot be undone.')) return

    try {
      await journalAPI.delete(id)
      // Remove from local state - entry is deleted from database
      setEntries(entries.filter(e => e.id !== id))
      setError('') // Clear any previous errors
    } catch (err) {
      console.error('Delete error:', err)
      setError(err.response?.data?.error || err.response?.data?.message || 'Failed to delete entry. Please try again.')
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
      <div className="w-full mx-auto px-4">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Journal History</h1>
          <Link
            to="/journal/new"
            className="px-4 py-2 rounded-lg transition-colors"
            style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
          >
            New Entry
          </Link>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {entries.length === 0 ? (
          <div className="bg-white rounded-xl shadow-md p-8 text-center">
            <p className="mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>No journal entries yet.</p>
            <Link
              to="/journal/new"
              className="font-medium"
              style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}
            >
              Create your first entry
            </Link>
          </div>
        ) : (
          <div className="card-3d overflow-hidden">
            <DataTable
              columns={[
                {
                  key: 'created_at',
                  label: 'Date & Time',
                  width: '140px',
                  icon: (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  ),
                  render: (value) => (
                    <div className="flex flex-col items-center">
                      <div className="font-medium text-xs" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                        {new Date(value).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: '2-digit',
                        })}
                      </div>
                      <div className="text-xs" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>
                        {new Date(value).toLocaleTimeString('en-US', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                    </div>
                  )
                },
                {
                  key: 'sentiment_score',
                  label: 'Sentiment',
                  width: '100px',
                  icon: (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  ),
                  render: (value) => (
                    <span className={`font-bold text-sm ${
                      value >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {value > 0 ? '+' : ''}{value.toFixed(2)}
                    </span>
                  )
                },
                {
                  key: 'intensity_score',
                  label: 'Intensity',
                  width: '90px',
                  icon: (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  ),
                  render: (value, row) => {
                    // Show NA if sentiment is positive
                    if (row.sentiment_score > 0) {
                      return (
                        <span className="font-bold text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}>
                          NA
                        </span>
                      );
                    }
                    // Calculate intensity as average of detected emotion confidences
                    if (row.detected_emotions && row.detected_emotions.length > 0) {
                      const avgConfidence = row.detected_emotions.reduce((sum, e) => sum + e.confidence, 0) / row.detected_emotions.length;
                      return (
                        <span className="font-bold text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}>
                          {avgConfidence.toFixed(2)}
                        </span>
                      );
                    }
                    // No emotions detected, show NA
                    return (
                      <span className="font-bold text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}>
                        NA
                      </span>
                    );
                  }
                },
                {
                  key: 'key_themes',
                  label: 'Themes',
                  width: '150px',
                  nowrap: false,
                  render: (value) => (
                    <div className="flex flex-wrap gap-1.5 justify-center">
                      {value && value.length > 0 ? (
                        value.slice(0, 2).map((theme, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1.5 rounded-full text-xs font-medium inline-block text-center min-w-[80px]"
                            style={{ 
                              fontFamily: "'Inter', sans-serif", 
                              background: 'rgba(241, 90, 42, 0.12)', 
                              color: '#F15A2A', 
                              border: '1px solid rgba(241, 90, 42, 0.2)',
                              display: 'inline-flex',
                              alignItems: 'center',
                              justifyContent: 'center'
                            }}
                          >
                            {theme}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs italic" style={{ fontFamily: "'Inter', sans-serif", color: '#9CA3AF' }}>None</span>
                      )}
                      {value && value.length > 2 && (
                        <span className="text-xs font-medium" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>+{value.length - 2}</span>
                      )}
                    </div>
                  )
                },
                {
                  key: 'risk_flags',
                  label: 'Risk',
                  width: '90px',
                  render: (value) => {
                    const hasRisk = value && Object.values(value).some(v => v)
                    return (
                      <div className="flex justify-center">
                        {hasRisk ? (
                          <span className="px-3 py-1.5 bg-red-100 text-red-800 rounded-full text-xs font-semibold shadow-sm border border-red-200">
                            ⚠️ Flags
                          </span>
                        ) : (
                          <span className="px-3 py-1.5 bg-green-100 text-green-800 rounded-full text-xs font-semibold shadow-sm border border-green-200">
                            ✓ Safe
                          </span>
                        )}
                      </div>
                    )
                  }
                },
                {
                  key: 'actions',
                  label: 'Actions',
                  width: '90px',
                  render: (_, row) => (
                    <div className="flex justify-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(row.id)
                        }}
                        className="px-3 py-1.5 hover:bg-red-50 rounded-lg transition-all text-xs font-medium shadow-sm hover:shadow border border-red-200 hover:border-red-300"
                        style={{ fontFamily: "'Inter', sans-serif", color: '#DC2626', background: 'rgba(220, 38, 38, 0.05)' }}
                      >
                        Delete
                      </button>
                    </div>
                  )
                }
              ]}
              data={entries}
              emptyMessage="No journal entries yet. Create your first entry!"
            />
          </div>
        )}
      </div>
    </Layout>
  )
}

export default JournalHistory

