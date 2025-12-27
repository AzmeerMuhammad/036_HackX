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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: '#F15A2A' }}></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>7-Day Insights</h1>

        {insights ? (
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-xl shadow-md p-6"
            >
              <h2 className="text-xl font-semibold mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Overview</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="rounded-lg p-4" style={{ background: 'rgba(241, 90, 42, 0.05)' }}>
                  <div className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Total Entries</div>
                  <div className="text-2xl font-bold" style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}>{insights.totalEntries}</div>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Avg Sentiment</div>
                  <div className="text-2xl font-bold" style={{ fontFamily: "'Inter', sans-serif", color: insights.avgSentiment >= 0 ? '#10B981' : '#DC2626' }}>
                    {insights.avgSentiment > 0 ? '+' : ''}{insights.avgSentiment.toFixed(2)}
                  </div>
                </div>
                <div className="rounded-lg p-4" style={{ background: 'rgba(241, 90, 42, 0.05)' }}>
                  <div className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Avg Intensity</div>
                  <div className="text-2xl font-bold" style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}>
                    {insights.avgIntensity.toFixed(2)}
                  </div>
                </div>
                <div className="bg-yellow-50 rounded-lg p-4">
                  <div className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Risk Flags</div>
                  <div className="text-2xl font-bold" style={{ fontFamily: "'Inter', sans-serif", color: '#D97706' }}>{insights.riskCount}</div>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-xl shadow-md p-6"
            >
              <h2 className="text-xl font-semibold mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Trend</h2>
              <div className={`p-4 rounded-lg ${
                insights.trend === 'positive' ? 'bg-green-50 border border-green-200' :
                insights.trend === 'negative' ? 'bg-red-50 border border-red-200' :
                'bg-gray-50 border border-gray-200'
              }`}>
                <div className="text-lg font-semibold capitalize" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                  {insights.trend} trend detected
                </div>
                {insights.trend === 'negative' && insights.riskCount > 0 && (
                  <p className="text-sm mt-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
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
                <h2 className="text-xl font-semibold mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Top Themes</h2>
                <div className="flex flex-wrap gap-2">
                  {insights.topThemes.map((theme, idx) => (
                    <span
                      key={idx}
                      className="px-4 py-2 rounded-full font-medium"
                      style={{ fontFamily: "'Inter', sans-serif", background: 'rgba(241, 90, 42, 0.1)', color: '#F15A2A' }}
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
            <p style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Not enough data for 7-day insights.</p>
            <p className="mt-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Create more journal entries to see insights.</p>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default Insights

