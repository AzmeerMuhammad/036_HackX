import { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import { journalAPI } from '../api/journal'
import { motion } from 'framer-motion'

const Insights = () => {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [insights, setInsights] = useState(null)

  useEffect(() => {
    loadInsights()
  }, [])

  const loadInsights = async () => {
    try {
      const response = await journalAPI.list()
      const data = response.data.results || response.data
      setEntries(data)

      // Calculate 7-day insights
      const last7Days = data.filter(entry => {
        const entryDate = new Date(entry.created_at)
        const sevenDaysAgo = new Date()
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
        return entryDate >= sevenDaysAgo
      })

      if (last7Days.length > 0) {
        const avgSentiment = last7Days.reduce((sum, e) => sum + e.sentiment_score, 0) / last7Days.length
        const avgIntensity = last7Days.reduce((sum, e) => sum + e.intensity_score, 0) / last7Days.length
        const riskCount = last7Days.filter(e => e.risk_flags && Object.values(e.risk_flags).some(v => v)).length
        const themes = {}
        last7Days.forEach(e => {
          if (e.key_themes) {
            e.key_themes.forEach(theme => {
              themes[theme] = (themes[theme] || 0) + 1
            })
          }
        })
        const topThemes = Object.entries(themes)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5)
          .map(([theme]) => theme)

        setInsights({
          totalEntries: last7Days.length,
          avgSentiment,
          avgIntensity,
          riskCount,
          topThemes,
          trend: avgSentiment < -0.3 ? 'negative' : avgSentiment > 0.3 ? 'positive' : 'neutral',
        })
      }
    } catch (err) {
      console.error('Failed to load insights', err)
    } finally {
      setLoading(false)
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
        <h1 className="text-3xl font-bold text-gray-900 mb-6">7-Day Insights</h1>

        {insights ? (
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-xl shadow-md p-6"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Overview</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Total Entries</div>
                  <div className="text-2xl font-bold text-primary-600">{insights.totalEntries}</div>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Avg Sentiment</div>
                  <div className={`text-2xl font-bold ${insights.avgSentiment >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {insights.avgSentiment > 0 ? '+' : ''}{insights.avgSentiment.toFixed(2)}
                  </div>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Avg Intensity</div>
                  <div className="text-2xl font-bold text-purple-600">
                    {insights.avgIntensity.toFixed(2)}
                  </div>
                </div>
                <div className="bg-yellow-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Risk Flags</div>
                  <div className="text-2xl font-bold text-yellow-600">{insights.riskCount}</div>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-xl shadow-md p-6"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Trend</h2>
              <div className={`p-4 rounded-lg ${
                insights.trend === 'positive' ? 'bg-green-50 border border-green-200' :
                insights.trend === 'negative' ? 'bg-red-50 border border-red-200' :
                'bg-gray-50 border border-gray-200'
              }`}>
                <div className="text-lg font-semibold text-gray-900 capitalize">
                  {insights.trend} trend detected
                </div>
                {insights.trend === 'negative' && insights.riskCount > 0 && (
                  <p className="text-sm text-gray-700 mt-2">
                    Consider starting a chat session for additional support.
                  </p>
                )}
              </div>
            </motion.div>

            {insights.topThemes.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-white rounded-xl shadow-md p-6"
              >
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Top Themes</h2>
                <div className="flex flex-wrap gap-2">
                  {insights.topThemes.map((theme, idx) => (
                    <span
                      key={idx}
                      className="px-4 py-2 bg-primary-100 text-primary-800 rounded-full font-medium"
                    >
                      {theme}
                    </span>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-md p-8 text-center">
            <p className="text-gray-600">Not enough data for 7-day insights.</p>
            <p className="text-gray-600 mt-2">Create more journal entries to see insights.</p>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default Insights

