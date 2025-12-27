import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import { authAPI } from '../api/auth'
import { journalAPI } from '../api/journal'
import { chatAPI } from '../api/chat'

const ProfileDashboard = ({ user, onClose, onLogout, onUserUpdate }) => {
  const [activeSection, setActiveSection] = useState('snapshot')
  const [profileData, setProfileData] = useState({
    email: '',
    password: '',
    password_confirm: ''
  })
  const [profileLoading, setProfileLoading] = useState(false)
  const [profileError, setProfileError] = useState('')
  const [profileSuccess, setProfileSuccess] = useState('')

  // Real-time stats
  const [journalStats, setJournalStats] = useState(null)
  const [moodOverview, setMoodOverview] = useState(null)
  const [sessionHistory, setSessionHistory] = useState(null)
  const [statsLoading, setStatsLoading] = useState(false)

  const isProfessional = user?.is_professional || user?.professional_type

  useEffect(() => {
    loadDashboardData()
    setProfileData({
      email: user?.email || '',
      password: '',
      password_confirm: ''
    })
  }, [user])

  const loadDashboardData = async () => {
    setStatsLoading(true)
    try {
      // Load journal stats and mood data
      const journals = await journalAPI.list()
      const entries = journals.data.results || journals.data

      if (entries.length > 0) {
        // Calculate journaling stats
        const totalEntries = entries.length
        const sortedEntries = entries.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

        // Calculate daily streak
        let streak = 0
        let currentDate = new Date()
        currentDate.setHours(0, 0, 0, 0)

        for (let i = 0; i < sortedEntries.length; i++) {
          const entryDate = new Date(sortedEntries[i].created_at)
          entryDate.setHours(0, 0, 0, 0)
          const daysDiff = Math.floor((currentDate - entryDate) / (1000 * 60 * 60 * 24))

          if (daysDiff === streak) {
            streak++
          } else if (daysDiff > streak) {
            break
          }
        }

        // Calculate mood distribution
        const moodCounts = {}
        let totalSentiment = 0
        let totalIntensity = 0
        const recentMoods = []

        entries.forEach(entry => {
          if (entry.checkin_mood) {
            moodCounts[entry.checkin_mood] = (moodCounts[entry.checkin_mood] || 0) + 1
          }
          totalSentiment += entry.sentiment_score || 0
          totalIntensity += entry.intensity_score || 0

          if (recentMoods.length < 10) {
            recentMoods.push({
              date: entry.created_at,
              mood: entry.checkin_mood,
              sentiment: entry.sentiment_score,
              intensity: entry.intensity_score
            })
          }
        })

        setJournalStats({
          totalEntries,
          dailyStreak: streak,
          avgSentiment: (totalSentiment / totalEntries).toFixed(2),
          avgIntensity: (totalIntensity / totalEntries).toFixed(2),
          lastEntryDate: sortedEntries[0].created_at
        })

        setMoodOverview({
          moodDistribution: moodCounts,
          averageSentiment: (totalSentiment / totalEntries).toFixed(2),
          averageIntensity: (totalIntensity / totalEntries).toFixed(2),
          recentMoods,
          totalEntries
        })
      } else {
        setJournalStats({
          totalEntries: 0,
          dailyStreak: 0,
          avgSentiment: '0',
          avgIntensity: '0',
          lastEntryDate: null
        })
        setMoodOverview({
          moodDistribution: {},
          averageSentiment: '0',
          averageIntensity: '0',
          recentMoods: [],
          totalEntries: 0
        })
      }

      // Load session history
      const sessions = await chatAPI.getSessions()
      setSessionHistory(sessions.data || [])
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
    } finally {
      setStatsLoading(false)
    }
  }

  const handleProfileUpdate = async (e) => {
    e.preventDefault()
    setProfileError('')
    setProfileSuccess('')

    // Validate passwords match if password is being changed
    if (profileData.password || profileData.password_confirm) {
      if (profileData.password !== profileData.password_confirm) {
        setProfileError('Passwords do not match')
        return
      }
      if (profileData.password.length < 8) {
        setProfileError('Password must be at least 8 characters')
        return
      }
    }

    setProfileLoading(true)

    try {
      const updateData = {}

      // Only include email if it changed
      if (profileData.email && profileData.email !== user?.email) {
        updateData.email = profileData.email
      }

      // Only include password if provided
      if (profileData.password) {
        updateData.password = profileData.password
      }

      // If nothing to update
      if (Object.keys(updateData).length === 0) {
        setProfileError('No changes to save')
        setProfileLoading(false)
        return
      }

      const response = await authAPI.updateMe(updateData)

      // Update user in context and localStorage
      onUserUpdate(response.data)

      setProfileSuccess('Profile updated successfully!')

      // Clear password fields
      setProfileData(prev => ({
        ...prev,
        password: '',
        password_confirm: ''
      }))

      // Auto-close success message after 3 seconds
      setTimeout(() => {
        setProfileSuccess('')
      }, 3000)
    } catch (err) {
      setProfileError(err.response?.data?.error || 'Failed to update profile')
    } finally {
      setProfileLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        transition={{ type: 'spring', damping: 25 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl h-[90vh] overflow-hidden flex"
      >
        {/* Sidebar Navigation */}
        <div className="w-64 p-6 border-r border-gray-200" style={{ background: '#F7F3EC' }}>
          <div className="flex items-center gap-3 mb-8 pb-6 border-b-2 border-gray-200">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg" style={{ background: '#F15A2A' }}>
              <span className="text-white text-xl font-bold" style={{ fontFamily: "'Inter', sans-serif" }}>
                {(user?.display_name || user?.username)?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <h3 className="font-bold text-lg" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                {user?.display_name || user?.username}
              </h3>
              <p className="text-xs capitalize" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>
                {isProfessional ? user?.professional_type || 'Professional' : 'User'}
              </p>
            </div>
          </div>

          <nav className="space-y-2">
            {[
              { id: 'snapshot', label: 'User Snapshot', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg> },
              { id: 'mood', label: 'Mood Overview', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> },
              { id: 'stats', label: 'Journaling Stats', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg> },
              { id: 'sessions', label: 'Session History', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg> },
              { id: 'settings', label: 'Settings', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg> }
            ].map((item) => (
              <motion.button
                key={item.id}
                whileHover={{ x: 4 }}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  activeSection === item.id ? 'shadow-md' : 'hover:bg-white/50'
                }`}
                style={activeSection === item.id
                  ? { background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }
                  : { color: '#3F3F3F', fontFamily: "'Inter', sans-serif" }
                }
              >
                {item.icon}
                <span className="font-medium">{item.label}</span>
              </motion.button>
            ))}

            <motion.button
              whileHover={{ x: 4 }}
              onClick={() => { onLogout(); onClose(); }}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-red-600 hover:bg-red-50 mt-4"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span className="font-medium" style={{ fontFamily: "'Inter', sans-serif" }}>Logout</span>
            </motion.button>
          </nav>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 overflow-y-auto p-8 relative" style={{ background: '#F7F3EC' }}>
          {/* Close Button - Top Right */}
          <motion.button
            whileHover={{ scale: 1.1, rotate: 90 }}
            whileTap={{ scale: 0.9 }}
            onClick={onClose}
            className="absolute top-6 right-6 z-10 w-10 h-10 rounded-full bg-white shadow-lg hover:shadow-xl transition-all flex items-center justify-center"
            style={{ color: '#F15A2A' }}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </motion.button>

          {/* User Snapshot Section */}
          {activeSection === 'snapshot' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <h2 className="text-3xl font-bold mb-6" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>User Snapshot</h2>

              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-xl shadow-sm">
                  <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Username</label>
                  <p className="text-lg font-semibold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{user?.username}</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm">
                  <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Display Name</label>
                  <p className="text-lg font-semibold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{user?.display_name || 'Not set'}</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm">
                  <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Email</label>
                  <p className="text-lg font-semibold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{user?.email || 'Not set'}</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm">
                  <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Account Type</label>
                  <p className="text-lg font-semibold capitalize" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                    {isProfessional ? user?.professional_type || 'Professional' : 'Regular User'}
                  </p>
                </div>

                {isProfessional && (
                  <div className="bg-white p-6 rounded-xl shadow-sm">
                    <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Professional Type</label>
                    <p className="text-lg font-semibold capitalize" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{user?.professional_type}</p>
                  </div>
                )}

                <div className="bg-white p-6 rounded-xl shadow-sm">
                  <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Member Since</label>
                  <p className="text-lg font-semibold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Mood Overview Section */}
          {activeSection === 'mood' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <h2 className="text-3xl font-bold mb-6" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Mood Overview</h2>

              {statsLoading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: '#F15A2A' }}></div>
                </div>
              ) : moodOverview?.totalEntries > 0 ? (
                <>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-white p-6 rounded-xl shadow-sm">
                      <h3 className="text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Average Sentiment</h3>
                      <p className={`text-4xl font-bold ${parseFloat(moodOverview.averageSentiment) >= 0 ? 'text-green-600' : 'text-red-600'}`} style={{ fontFamily: "'Inter', sans-serif" }}>
                        {moodOverview.averageSentiment > 0 ? '+' : ''}{moodOverview.averageSentiment}
                      </p>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow-sm">
                      <h3 className="text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Average Intensity</h3>
                      <p className="text-4xl font-bold" style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}>
                        {moodOverview.averageIntensity}
                      </p>
                    </div>
                  </div>

                  <div className="bg-white p-6 rounded-xl shadow-sm">
                    <h3 className="text-lg font-semibold mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Mood Distribution</h3>
                    <div className="space-y-3">
                      {Object.entries(moodOverview.moodDistribution).map(([mood, count]) => (
                        <div key={mood} className="flex items-center gap-3">
                          <span className="capitalize font-medium w-32" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{mood}</span>
                          <div className="flex-1 bg-gray-200 rounded-full h-4 overflow-hidden">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${(count / moodOverview.totalEntries) * 100}%`,
                                background: '#F15A2A'
                              }}
                            />
                          </div>
                          <span className="font-semibold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-white p-6 rounded-xl shadow-sm">
                    <h3 className="text-lg font-semibold mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Recent Moods</h3>
                    <div className="space-y-2">
                      {moodOverview.recentMoods.map((entry, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium capitalize" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{entry.mood || 'No mood'}</p>
                            <p className="text-xs" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>
                              {new Date(entry.date).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className={`text-sm font-semibold ${entry.sentiment >= 0 ? 'text-green-600' : 'text-red-600'}`} style={{ fontFamily: "'Inter', sans-serif" }}>
                              Sentiment: {entry.sentiment?.toFixed(2)}
                            </p>
                            <p className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}>
                              Intensity: {entry.intensity?.toFixed(2)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <div className="bg-white p-12 rounded-xl shadow-sm text-center">
                  <svg className="w-16 h-16 mx-auto mb-4" style={{ color: '#6B7280' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>No journal entries yet. Start journaling to see your mood overview!</p>
                </div>
              )}
            </motion.div>
          )}

          {/* Journaling Stats Section */}
          {activeSection === 'stats' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <h2 className="text-3xl font-bold mb-6" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Journaling Stats</h2>

              {statsLoading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: '#F15A2A' }}></div>
                </div>
              ) : journalStats ? (
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="bg-white p-6 rounded-xl shadow-sm text-center">
                    <svg className="w-12 h-12 mx-auto mb-3" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 className="text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Total Entries</h3>
                    <p className="text-4xl font-bold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                      {journalStats.totalEntries}
                    </p>
                  </div>

                  <div className="bg-white p-6 rounded-xl shadow-sm text-center">
                    <svg className="w-12 h-12 mx-auto mb-3" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
                    </svg>
                    <h3 className="text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Daily Streak</h3>
                    <p className="text-4xl font-bold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                      {journalStats.dailyStreak} {journalStats.dailyStreak === 1 ? 'day' : 'days'}
                    </p>
                  </div>

                  <div className="bg-white p-6 rounded-xl shadow-sm text-center">
                    <svg className="w-12 h-12 mx-auto mb-3" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h3 className="text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Avg Sentiment</h3>
                    <p className={`text-4xl font-bold ${parseFloat(journalStats.avgSentiment) >= 0 ? 'text-green-600' : 'text-red-600'}`} style={{ fontFamily: "'Inter', sans-serif" }}>
                      {journalStats.avgSentiment > 0 ? '+' : ''}{journalStats.avgSentiment}
                    </p>
                  </div>

                  <div className="bg-white p-6 rounded-xl shadow-sm text-center">
                    <svg className="w-12 h-12 mx-auto mb-3" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <h3 className="text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Avg Intensity</h3>
                    <p className="text-4xl font-bold" style={{ fontFamily: "'Inter', sans-serif", color: '#F15A2A' }}>
                      {journalStats.avgIntensity}
                    </p>
                  </div>

                  {journalStats.lastEntryDate && (
                    <div className="md:col-span-2 bg-white p-6 rounded-xl shadow-sm text-center">
                      <svg className="w-12 h-12 mx-auto mb-3" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <h3 className="text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>Last Entry</h3>
                      <p className="text-xl font-semibold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                        {new Date(journalStats.lastEntryDate).toLocaleDateString()} at {new Date(journalStats.lastEntryDate).toLocaleTimeString()}
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-white p-12 rounded-xl shadow-sm text-center">
                  <p style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>No stats available</p>
                </div>
              )}
            </motion.div>
          )}

          {/* Session History Section */}
          {activeSection === 'sessions' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <h2 className="text-3xl font-bold mb-6" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Session History</h2>

              {statsLoading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: '#F15A2A' }}></div>
                </div>
              ) : sessionHistory && sessionHistory.length > 0 ? (
                <div className="space-y-4">
                  {sessionHistory.map((session, idx) => (
                    <div key={session.id || idx} className="bg-white p-6 rounded-xl shadow-sm">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-semibold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                          Session #{session.id}
                        </h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          session.status === 'open' ? 'bg-green-100 text-green-800' :
                          session.status === 'escalated' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`} style={{ fontFamily: "'Inter', sans-serif" }}>
                          {session.status}
                        </span>
                      </div>
                      <div className="text-sm space-y-1" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>
                        <p>Created: {new Date(session.created_at).toLocaleString()}</p>
                        {session.updated_at && (
                          <p>Last Updated: {new Date(session.updated_at).toLocaleString()}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-white p-12 rounded-xl shadow-sm text-center">
                  <svg className="w-16 h-16 mx-auto mb-4" style={{ color: '#6B7280' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <p style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>No chat sessions yet. Start a chat to see your history!</p>
                </div>
              )}
            </motion.div>
          )}

          {/* Settings Section */}
          {activeSection === 'settings' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <h2 className="text-3xl font-bold mb-6" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Settings</h2>

              <form onSubmit={handleProfileUpdate} className="space-y-6">
                {profileError && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-red-50 border-2 border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center space-x-2"
                  >
                    <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <span style={{ fontFamily: "'Inter', sans-serif" }}>{profileError}</span>
                  </motion.div>
                )}

                {profileSuccess && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-green-50 border-2 border-green-200 text-green-700 px-4 py-3 rounded-xl flex items-center space-x-2"
                  >
                    <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span style={{ fontFamily: "'Inter', sans-serif" }}>{profileSuccess}</span>
                  </motion.div>
                )}

                <div className="bg-white p-6 rounded-xl shadow-sm space-y-4">
                  <h3 className="text-lg font-semibold mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Update Your Information</h3>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                      Email (Optional)
                    </label>
                    <input
                      type="email"
                      value={profileData.email}
                      onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                      placeholder="your.email@example.com"
                      className="input-modern"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                      New Password (Optional)
                    </label>
                    <input
                      type="password"
                      value={profileData.password}
                      onChange={(e) => setProfileData({ ...profileData, password: e.target.value })}
                      placeholder="Enter new password"
                      className="input-modern"
                    />
                    <p className="text-xs mt-1" style={{ fontFamily: "'Inter', sans-serif", color: '#6B7280' }}>
                      Leave blank to keep current password. Minimum 8 characters.
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      value={profileData.password_confirm}
                      onChange={(e) => setProfileData({ ...profileData, password_confirm: e.target.value })}
                      placeholder="Confirm new password"
                      className="input-modern"
                      disabled={!profileData.password}
                    />
                  </div>

                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    type="submit"
                    disabled={profileLoading}
                    className="w-full py-3 rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
                  >
                    {profileLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Saving...</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>Save Changes</span>
                      </>
                    )}
                  </motion.button>
                </div>
              </form>
            </motion.div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}

export default ProfileDashboard
