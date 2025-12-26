import { useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'

const Home = () => {
  const { user } = useAuth()
  const [showPatientHistory, setShowPatientHistory] = useState(false)
  const [selectedPatient, setSelectedPatient] = useState(null)
  const [aiSummary, setAiSummary] = useState(null)
  const [loadingSummary, setLoadingSummary] = useState(false)

  // Mock patient data for professionals
  const mockPatients = [
    {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      sharedSince: '2024-01-15',
      lastEntry: '2024-01-20',
      entriesCount: 12,
      riskLevel: 'low'
    },
    {
      id: 2,
      name: 'Jane Smith',
      email: 'jane@example.com',
      sharedSince: '2024-01-10',
      lastEntry: '2024-01-19',
      entriesCount: 8,
      riskLevel: 'medium'
    },
    {
      id: 3,
      name: 'Michael Johnson',
      email: 'michael@example.com',
      sharedSince: '2024-01-05',
      lastEntry: '2024-01-18',
      entriesCount: 15,
      riskLevel: 'high'
    }
  ]

  const handleLoadAISummary = async (patient) => {
    setLoadingSummary(true)
    try {
      // Mock AI summary - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      setAiSummary({
        patientId: patient.id,
        overview: `Patient ${patient.name} shows consistent patterns of emotional expression through journaling. Recent entries indicate ${patient.riskLevel === 'low' ? 'stable mental health with positive coping mechanisms' : patient.riskLevel === 'medium' ? 'moderate stress levels with room for improvement' : 'elevated concern levels requiring close monitoring'}.`,
        keyThemes: patient.riskLevel === 'low'
          ? ['Self-care', 'Positive Thinking', 'Work-Life Balance', 'Social Connection']
          : patient.riskLevel === 'medium'
          ? ['Work Stress', 'Anxiety', 'Sleep Issues', 'Self-improvement']
          : ['Severe Anxiety', 'Depression Indicators', 'Isolation', 'Crisis Support Needed'],
        sentimentTrend: patient.riskLevel === 'low' ? 'stable' : patient.riskLevel === 'medium' ? 'improving' : 'declining',
        averageSentiment: patient.riskLevel === 'low' ? 0.65 : patient.riskLevel === 'medium' ? 0.45 : 0.15,
        riskIndicators: patient.riskLevel === 'low'
          ? ['No significant risks detected']
          : patient.riskLevel === 'medium'
          ? ['Moderate stress levels', 'Occasional sleep disruption']
          : ['High anxiety levels', 'Mentions of hopelessness', 'Social withdrawal'],
        recommendations: patient.riskLevel === 'low'
          ? ['Continue current positive practices', 'Maintain regular journaling', 'Encourage social activities']
          : patient.riskLevel === 'medium'
          ? ['Continue current treatment approach', 'Consider stress management techniques', 'Monitor sleep patterns closely']
          : ['Immediate consultation recommended', 'Consider crisis intervention resources', 'Increase monitoring frequency'],
        recentEntries: [
          {
            date: patient.lastEntry,
            sentiment: patient.riskLevel === 'low' ? 0.7 : patient.riskLevel === 'medium' ? 0.6 : 0.2,
            summary: patient.riskLevel === 'low' ? 'Feeling grateful and optimistic about the future' : patient.riskLevel === 'medium' ? 'Feeling more confident about work presentations' : 'Struggling with overwhelming feelings'
          },
          {
            date: '2024-01-19',
            sentiment: patient.riskLevel === 'low' ? 0.65 : patient.riskLevel === 'medium' ? 0.3 : 0.15,
            summary: patient.riskLevel === 'low' ? 'Had a productive day and good social interaction' : patient.riskLevel === 'medium' ? 'Struggled with team meeting anxiety' : 'Difficult to find motivation today'
          },
          {
            date: '2024-01-18',
            sentiment: patient.riskLevel === 'low' ? 0.6 : patient.riskLevel === 'medium' ? 0.5 : 0.1,
            summary: patient.riskLevel === 'low' ? 'Enjoyed time with family and friends' : patient.riskLevel === 'medium' ? 'Practiced breathing exercises, felt calmer' : 'Feeling isolated and disconnected'
          }
        ]
      })
    } catch (err) {
      alert('Failed to load AI summary')
    } finally {
      setLoadingSummary(false)
    }
  }

  // Check if user is a professional (adjust this check based on your auth context structure)
  const isProfessional = user?.is_professional || user?.role === 'professional' || user?.user_type === 'professional'

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  }

  const mainCards = [
    {
      title: 'Journal',
      description: 'Record your thoughts and feelings with AI-powered insights',
      iconSvg: (
        <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
      path: '/journal/new',
      gradient: 'from-purple-500 to-indigo-600'
    },
    {
      title: 'Chat Support',
      description: 'Talk to our empathetic AI chatbot anytime',
      iconSvg: (
        <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      path: '/chat',
      gradient: 'from-blue-500 to-cyan-600'
    }
  ]

  const quickLinks = [
    {
      title: 'Journal History',
      iconSvg: (
        <svg className="w-10 h-10 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      path: '/journal/history'
    },
    {
      title: '7-Day Insights',
      iconSvg: (
        <svg className="w-10 h-10 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      path: '/insights'
    },
    {
      title: 'Professionals',
      iconSvg: (
        <svg className="w-10 h-10 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      path: '/professionals'
    },
    {
      title: 'Share History',
      iconSvg: (
        <svg className="w-10 h-10 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
        </svg>
      ),
      path: '/history/share'
    }
  ]

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold gradient-text mb-4 flex items-center justify-center gap-3">
            <span>Welcome back, {user?.display_name || user?.username}!</span>
            <svg className="w-12 h-12 text-purple-600 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
            </svg>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Your secure AI-powered mental health journaling platform
          </p>
        </motion.div>

        {/* Main Action Cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid md:grid-cols-2 gap-8 mb-12"
        >
          {mainCards.map((card, index) => (
            <motion.div
              key={card.title}
              variants={itemVariants}
              whileHover={{ y: -8 }}
              whileTap={{ scale: 0.98 }}
            >
              <Link
                to={card.path}
                className="block card-3d p-8 group relative overflow-hidden"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${card.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
                <div className="relative z-10">
                  <div className="mb-6 text-purple-600">{card.iconSvg}</div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-3">
                    {card.title}
                  </h2>
                  <p className="text-gray-600 text-lg">
                    {card.description}
                  </p>
                </div>
                <div className="absolute bottom-4 right-4 text-primary-400 opacity-0 group-hover:opacity-100 transition-opacity">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>

        {/* Quick Links */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-8"
        >
          <h3 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
            Quick Access
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {quickLinks.map((link, index) => (
              <motion.div
                key={link.title}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link
                  to={link.path}
                  className="block card-3d p-6 text-center group"
                >
                  <div className="mb-3 text-purple-600 group-hover:text-purple-700 transition-colors">{link.iconSvg}</div>
                  <h4 className="font-semibold text-gray-800 group-hover:text-primary-600 transition-colors">
                    {link.title}
                  </h4>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Info Banner */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="card-3d p-6 bg-gradient-to-r from-primary-50 to-blue-50 border-2 border-primary-100"
        >
          <div className="flex items-center justify-center space-x-3">
            <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            <p className="text-gray-700 text-center">
              <span className="font-semibold">Your privacy matters.</span> All your data is encrypted and secure.
              {user?.is_anonymous_mode && <span className="ml-2 badge badge-primary">Anonymous Mode Active</span>}
            </p>
          </div>
        </motion.div>
      </div>
    </Layout>
  )
}

export default Home
