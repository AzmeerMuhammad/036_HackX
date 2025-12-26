import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { journalAPI } from '../api/journal'
import { motion } from 'framer-motion'

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
          <div className="space-y-4">
            {entries.map((entry, idx) => (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="bg-white rounded-xl shadow-md p-6"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <div className="text-sm text-gray-500">
                      {new Date(entry.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                    {entry.checkin_mood && (
                      <div className="mt-1 text-sm text-gray-700">
                        Mood: {entry.checkin_mood} ({Math.round(entry.checkin_intensity * 100)}%)
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => handleDelete(entry.id)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Delete
                  </button>
                </div>

                {entry.ai_summary && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                    <div className="text-sm font-semibold text-gray-900 mb-1">AI Summary</div>
                    <div className="text-gray-700">{entry.ai_summary}</div>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="text-sm">
                    <span className="text-gray-600">Sentiment: </span>
                    <span className={`font-semibold ${entry.sentiment_score >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {entry.sentiment_score > 0 ? '+' : ''}{entry.sentiment_score.toFixed(2)}
                    </span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-600">Intensity: </span>
                    <span className="font-semibold text-primary-600">
                      {entry.intensity_score.toFixed(2)}
                    </span>
                  </div>
                </div>

                {entry.key_themes && entry.key_themes.length > 0 && (
                  <div className="mb-4">
                    <div className="text-sm text-gray-600 mb-2">Themes:</div>
                    <div className="flex flex-wrap gap-2">
                      {entry.key_themes.map((theme, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-primary-100 text-primary-800 rounded-full text-xs"
                        >
                          {theme}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {entry.risk_flags && Object.values(entry.risk_flags).some(v => v) && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                    <div className="text-sm font-semibold text-yellow-900 mb-1">Risk Flags</div>
                    <div className="text-xs text-yellow-800">
                      {Object.entries(entry.risk_flags)
                        .filter(([_, value]) => value)
                        .map(([key, _]) => key.replace('_', ' '))
                        .join(', ')}
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}

export default JournalHistory

