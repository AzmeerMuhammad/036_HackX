import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'

const Home = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [showPatientHistory, setShowPatientHistory] = useState(false)
  const [selectedPatient, setSelectedPatient] = useState(null)
  const [aiSummary, setAiSummary] = useState(null)
  const [loadingSummary, setLoadingSummary] = useState(false)

  // Redirect professionals to their dashboard
  useEffect(() => {
    const isProfessional = user?.is_professional ||
                          user?.role === 'professional' ||
                          user?.user_type === 'professional' ||
                          user?.professional_type
    
    if (isProfessional) {
      navigate('/professional/dashboard', { replace: true })
    }
  }, [user, navigate])

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
  const isProfessional = user?.is_professional ||
                        user?.role === 'professional' ||
                        user?.user_type === 'professional' ||
                        user?.professional_type

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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Hero Section - Apple Style */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
          className="text-center mb-20 sm:mb-24 pt-8 sm:pt-12"
        >
          <motion.h1 
            className="text-4xl sm:text-5xl md:text-6xl font-bold mb-4 sm:mb-6" 
            style={{ 
              fontFamily: "'Inter', sans-serif", 
              fontWeight: 700,
              color: '#1d1d1f',
              letterSpacing: '-0.03em',
              lineHeight: '1.1'
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
          >
            Welcome back,{' '}
            <span style={{ 
              background: 'linear-gradient(135deg, #F15A2A 0%, #d14a1f 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              color: 'transparent'
            }}>
              {user?.display_name || user?.username}
            </span>
          </motion.h1>
          <motion.p 
            className="text-lg sm:text-xl md:text-2xl max-w-3xl mx-auto leading-relaxed" 
            style={{ 
              fontFamily: "'Inter', sans-serif", 
              color: '#86868b',
              fontWeight: 400,
              letterSpacing: '-0.01em'
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            Your secure AI-powered mental health journaling platform
          </motion.p>
        </motion.div>

        {/* Main Action Cards - Apple Style */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid md:grid-cols-2 gap-6 lg:gap-8 mb-20 sm:mb-24"
        >
          {mainCards.map((card, index) => (
            <motion.div
              key={card.title}
              variants={itemVariants}
              whileHover={{ y: -12, scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
            >
              <Link
                to={card.path}
                className="block group relative overflow-hidden rounded-3xl bg-white/80 backdrop-blur-xl border border-gray-200/50 p-10 sm:p-12 lg:p-14"
                style={{
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05)'
                }}
              >
                {/* Subtle gradient overlay on hover */}
                <motion.div
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                  style={{
                    background: 'linear-gradient(135deg, rgba(241, 90, 42, 0.03) 0%, rgba(241, 90, 42, 0.01) 100%)'
                  }}
                />
                
                {/* Enhanced shadow on hover */}
                <div className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10"
                  style={{
                    boxShadow: '0 20px 60px -12px rgba(241, 90, 42, 0.15), 0 0 0 1px rgba(241, 90, 42, 0.05)'
                  }}
                />

                <div className="relative z-10">
                  <motion.div 
                    className="mb-8" 
                    style={{ color: '#F15A2A' }}
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ duration: 0.3 }}
                  >
                    {card.iconSvg}
                  </motion.div>
                  <h2 
                    className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-3 sm:mb-4" 
                    style={{ 
                      fontFamily: "'Inter', sans-serif", 
                      color: '#1d1d1f',
                      fontWeight: 700,
                      letterSpacing: '-0.03em',
                      lineHeight: '1.1'
                    }}
                  >
                    {card.title}
                  </h2>
                  <p 
                    className="text-base sm:text-lg lg:text-xl leading-relaxed mb-6" 
                    style={{ 
                      fontFamily: "'Inter', sans-serif", 
                      color: '#86868b',
                      fontWeight: 400,
                      letterSpacing: '-0.01em'
                    }}
                  >
                    {card.description}
                  </p>
                  
                  <motion.div 
                    className="flex items-center gap-2 text-primary-600 font-semibold text-base sm:text-lg"
                    initial={{ x: 0 }}
                    whileHover={{ x: 8 }}
                    transition={{ duration: 0.3 }}
                  >
                    <span>Get started</span>
                    <motion.svg 
                      className="w-5 h-5" 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                      initial={{ x: 0 }}
                      whileHover={{ x: 4 }}
                      transition={{ duration: 0.3 }}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </motion.svg>
                  </motion.div>
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>

        {/* Quick Links - Apple Style */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.8 }}
          className="mb-20 sm:mb-24"
        >
          <motion.h3 
            className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-8 sm:mb-12 text-center" 
            style={{ 
              fontFamily: "'Inter', sans-serif", 
              color: '#1d1d1f',
              fontWeight: 700,
              letterSpacing: '-0.03em'
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            Quick Access
          </motion.h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
            {quickLinks.map((link, index) => (
              <motion.div
                key={link.title}
                initial={{ opacity: 0, y: 30, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ delay: 0.6 + index * 0.1, duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
                whileHover={{ y: -8, scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Link
                  to={link.path}
                  className="block group relative overflow-hidden rounded-2xl bg-white/80 backdrop-blur-xl border border-gray-200/50 p-6 sm:p-8 text-center"
                  style={{
                    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.03)'
                  }}
                >
                  {/* Hover gradient */}
                  <motion.div
                    className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    style={{
                      background: 'linear-gradient(135deg, rgba(241, 90, 42, 0.05) 0%, rgba(241, 90, 42, 0.02) 100%)'
                    }}
                  />

                  {/* Enhanced shadow on hover */}
                  <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10"
                    style={{
                      boxShadow: '0 12px 40px -8px rgba(241, 90, 42, 0.12)'
                    }}
                  />

                  <motion.div 
                    className="mb-4 sm:mb-6 transition-colors relative z-10" 
                    style={{ color: '#F15A2A' }}
                    whileHover={{ scale: 1.15 }}
                    transition={{ duration: 0.3 }}
                  >
                    {link.iconSvg}
                  </motion.div>
                  <h4 
                    className="font-semibold text-base sm:text-lg transition-colors relative z-10" 
                    style={{ 
                      fontFamily: "'Inter', sans-serif", 
                      color: '#1d1d1f',
                      fontWeight: 600,
                      letterSpacing: '-0.01em'
                    }}
                  >
                    {link.title}
                  </h4>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Info Banner - Apple Style */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-50/60 to-primary-100/40 border border-primary-200/50 p-8 sm:p-10 lg:p-12"
          style={{
            boxShadow: '0 4px 20px rgba(241, 90, 42, 0.1), 0 1px 3px rgba(241, 90, 42, 0.05)'
          }}
        >
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6 relative z-10">
            <motion.div
              whileHover={{ scale: 1.1 }}
              transition={{ duration: 0.3 }}
            >
              <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-xl flex items-center justify-center" 
                style={{ 
                  background: 'linear-gradient(135deg, #F15A2A 0%, #d14a1f 100%)',
                  boxShadow: '0 4px 12px rgba(241, 90, 42, 0.25)'
                }}>
                <svg className="w-6 h-6 sm:w-7 sm:h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
            </motion.div>
            <p 
              className="text-center sm:text-left text-base sm:text-lg lg:text-xl" 
              style={{ 
                fontFamily: "'Inter', sans-serif", 
                color: '#92400E',
                fontWeight: 500,
                letterSpacing: '-0.01em'
              }}
            >
              <span className="font-bold" style={{ color: '#78350f' }}>Your privacy matters.</span>{' '}
              <span style={{ opacity: 0.9 }}>All your data is encrypted and secure.</span>
            </p>
          </div>
        </motion.div>
      </div>
    </Layout>
  )
}

export default Home
