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
    if (!window.confirm('Are you sure you want to delete this entry?')) return

    try {
      await journalAPI.delete(id)
      setEntries(entries.filter(e => e.id !== id))
    } catch (err) {
      setError('Failed to delete entry')
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
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Journal History</h1>
          <Link
            to="/journal/new"
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
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
            <p className="text-gray-600 mb-4">No journal entries yet.</p>
            <Link
              to="/journal/new"
              className="text-primary-600 hover:text-primary-700 font-medium"
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
                  icon: (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  ),
                  minWidth: '180px',
                  render: (value) => (
                    <div>
                      <div className="font-medium text-gray-900">
                        {new Date(value).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                        })}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(value).toLocaleTimeString('en-US', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                    </div>
                  )
                },
                {
                  key: 'checkin_mood',
                  label: 'Mood',
                  icon: (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  ),
                  render: (value, row) => (
                    <div>
                      {value ? (
                        <>
                          <span className="font-medium text-gray-900 capitalize">{value}</span>
                          <span className="text-xs text-gray-500 ml-2">
                            ({Math.round((row.checkin_intensity || 0) * 100)}%)
                          </span>
                        </>
                      ) : (
                        <span className="text-gray-400 italic">Not specified</span>
                      )}
                    </div>
                  )
                },
                {
                  key: 'sentiment_score',
                  label: 'Sentiment',
                  icon: (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  ),
                  render: (value) => (
                    <span className={`font-bold text-lg ${
                      value >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {value > 0 ? '+' : ''}{value.toFixed(2)}
                    </span>
                  )
                },
                {
                  key: 'intensity_score',
                  label: 'Intensity',
                  icon: (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  ),
                  render: (value) => (
                    <span className="font-bold text-lg text-purple-600">
                      {value.toFixed(2)}
                    </span>
                  )
                },
                {
                  key: 'key_themes',
                  label: 'Themes',
                  minWidth: '200px',
                  render: (value) => (
                    <div className="flex flex-wrap gap-1">
                      {value && value.length > 0 ? (
                        value.slice(0, 2).map((theme, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium"
                          >
                            {theme}
                          </span>
                        ))
                      ) : (
                        <span className="text-gray-400 text-xs italic">None</span>
                      )}
                      {value && value.length > 2 && (
                        <span className="text-xs text-gray-500">+{value.length - 2} more</span>
                      )}
                    </div>
                  )
                },
                {
                  key: 'risk_flags',
                  label: 'Risk',
                  render: (value) => {
                    const hasRisk = value && Object.values(value).some(v => v)
                    return (
                      <div>
                        {hasRisk ? (
                          <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold">
                            ⚠️ Flags
                          </span>
                        ) : (
                          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
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
                  render: (_, row) => (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDelete(row.id)
                      }}
                      className="px-3 py-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors text-sm font-medium"
                    >
                      Delete
                    </button>
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

