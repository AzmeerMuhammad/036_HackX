import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { journalAPI } from '../api/journal'
import { motion } from 'framer-motion'

const JournalNew = () => {
  const [text, setText] = useState('')
  const [checkinMood, setCheckinMood] = useState('')
  const [checkinIntensity, setCheckinIntensity] = useState(0.5)
  const [voiceFile, setVoiceFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!text.trim()) {
      setError('Please enter some text')
      return
    }

    setLoading(true)
    setError('')

    try {
      const formData = {
        text,
        checkin_mood: checkinMood,
        checkin_intensity: checkinIntensity,
        voice_file: voiceFile,
      }
      const response = await journalAPI.create(formData)
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create journal entry')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">New Journal Entry</h1>

        {!result ? (
          <motion.form
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onSubmit={handleSubmit}
            className="bg-white rounded-xl shadow-md p-6 space-y-6"
          >
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                How are you feeling? (Optional)
              </label>
              <input
                type="text"
                value={checkinMood}
                onChange={(e) => setCheckinMood(e.target.value)}
                placeholder="e.g., anxious, calm, happy"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Intensity: {Math.round(checkinIntensity * 100)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={checkinIntensity}
                onChange={(e) => setCheckinIntensity(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Journal Entry *
              </label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                rows={10}
                required
                placeholder="Write about your thoughts, feelings, or experiences..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Voice Recording (Optional)
              </label>
              <input
                type="file"
                accept="audio/*"
                onChange={(e) => setVoiceFile(e.target.files[0])}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Analyzing...' : 'Submit & Analyze'}
            </button>
          </motion.form>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl shadow-md p-6 space-y-6"
          >
            <h2 className="text-2xl font-bold text-gray-900">AI Analysis Results</h2>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">Summary</h3>
              <p className="text-gray-700">{result.ai_summary}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Sentiment Score</div>
                <div className="text-2xl font-bold text-primary-600">
                  {result.sentiment_score > 0 ? '+' : ''}{result.sentiment_score.toFixed(2)}
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Intensity Score</div>
                <div className="text-2xl font-bold text-primary-600">
                  {result.intensity_score.toFixed(2)}
                </div>
              </div>
            </div>

            {result.key_themes && result.key_themes.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Key Themes</h3>
                <div className="flex flex-wrap gap-2">
                  {result.key_themes.map((theme, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm"
                    >
                      {theme}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {result.risk_flags && Object.values(result.risk_flags).some(v => v) && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="font-semibold text-yellow-900 mb-2">Risk Flags Detected</h3>
                <ul className="list-disc list-inside text-yellow-800">
                  {Object.entries(result.risk_flags)
                    .filter(([_, value]) => value)
                    .map(([key, _]) => (
                      <li key={key}>{key.replace('_', ' ')}</li>
                    ))}
                </ul>
              </div>
            )}

            {result.suggest_start_chat && (
              <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
                <p className="text-primary-900 mb-4">
                  Based on your entry, we recommend starting a chat session for additional support.
                </p>
                <button
                  onClick={() => navigate('/chat')}
                  className="w-full py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
                >
                  Start Chat
                </button>
              </div>
            )}

            <div className="flex space-x-4">
              <button
                onClick={() => {
                  setResult(null)
                  setText('')
                  setCheckinMood('')
                  setCheckinIntensity(0.5)
                  setVoiceFile(null)
                }}
                className="flex-1 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
              >
                New Entry
              </button>
              <button
                onClick={() => navigate('/journal/history')}
                className="flex-1 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                View History
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </Layout>
  )
}

export default JournalNew

