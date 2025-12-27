import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { professionalsAPI } from '../api/professionals'
import { motion, AnimatePresence } from 'framer-motion'
import VerificationModal from '../components/VerificationModal'
import { useAuth } from '../contexts/AuthContext'

const ProfessionalDashboard = () => {
  const { user, setUser, logout } = useAuth()
  const navigate = useNavigate()

  // Verification State
  const [isVerified, setIsVerified] = useState(true) // Default to true to prevent flash
  const [showVerificationModal, setShowVerificationModal] = useState(false)
  const [checkingVerification, setCheckingVerification] = useState(true)

  // Tab State
  const [activeTab, setActiveTab] = useState('patients') // patients, availability, escalations

  // Modal State for Patient History
  const [showPatientHistoryModal, setShowPatientHistoryModal] = useState(false)
  const [modalSelectedPatient, setModalSelectedPatient] = useState(null)
  const [modalAiSummary, setModalAiSummary] = useState(null)
  const [modalLoadingSummary, setModalLoadingSummary] = useState(false)

  // Escalations State
  const [escalations, setEscalations] = useState([])
  const [selectedTicket, setSelectedTicket] = useState(null)
  const [verdict, setVerdict] = useState('')
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  // Patients State
  const [patients, setPatients] = useState([])
  const [loadingPatients, setLoadingPatients] = useState(true)
  const [selectedPatient, setSelectedPatient] = useState(null)
  const [aiSummary, setAiSummary] = useState(null)
  const [loadingSummary, setLoadingSummary] = useState(false)
  const [newPatientsCount, setNewPatientsCount] = useState(0)

  // Availability State
  const [availability, setAvailability] = useState({
    monday: { available: false, startTime: '09:00', endTime: '17:00' },
    tuesday: { available: false, startTime: '09:00', endTime: '17:00' },
    wednesday: { available: false, startTime: '09:00', endTime: '17:00' },
    thursday: { available: false, startTime: '09:00', endTime: '17:00' },
    friday: { available: false, startTime: '09:00', endTime: '17:00' },
    saturday: { available: false, startTime: '09:00', endTime: '17:00' },
    sunday: { available: false, startTime: '09:00', endTime: '17:00' },
  })
  const [location, setLocation] = useState({
    type: 'in-person', // in-person, online, both
    address: '',
    city: '',
    state: '',
    zipCode: '',
    country: '',
    onlineLink: ''
  })
  const [profileInfo, setProfileInfo] = useState({
    specialization: '',
    yearsOfExperience: '',
    bio: '',
    languages: '',
    sessionFee: ''
  })

  // Removed auto-loading of escalations to prevent 403 errors
  // Escalations will be loaded when needed
  // useEffect(() => {
  //   loadEscalations()
  // }, [])

  useEffect(() => {
    // Just set loading to false since we're not auto-loading escalations
    setLoading(false)
  }, [])

  // Check verification status
  useEffect(() => {
    const checkVerification = async () => {
      try {
        const response = await professionalsAPI.getProfile()
        const verified = response.data.verified || false
        setIsVerified(verified)
        if (!verified) {
          setShowVerificationModal(true)
        }
      } catch (err) {
        console.error('Error checking verification:', err)
        setIsVerified(false)
        setShowVerificationModal(true)
      } finally {
        setCheckingVerification(false)
      }
    }

    checkVerification()
  }, [])

  const fetchPatients = async () => {
    try {
      setLoadingPatients(true)
      const response = await professionalsAPI.getPatients()
      const newPatients = response.data || []
      
      // Check for new patients (compare by ID)
      if (patients.length > 0) {
        const existingIds = new Set(patients.map(p => p.id))
        const newOnes = newPatients.filter(p => !existingIds.has(p.id))
        if (newOnes.length > 0) {
          setNewPatientsCount(newOnes.length)
          // Show subtle notification (non-blocking)
          console.log(`✅ ${newOnes.length} new patient(s) have shared their history with you!`)
        }
      } else if (newPatients.length > 0 && patients.length === 0) {
        // First time loading with patients
        console.log(`✅ ${newPatients.length} patient(s) have shared their history with you!`)
      }
      
      setPatients(newPatients)
    } catch (error) {
      console.error('Error fetching patients:', error)
      setPatients([]) // Set empty array on error
    } finally {
      setLoadingPatients(false)
    }
  }

  useEffect(() => {
    // Initial fetch
    fetchPatients()
    
    // Auto-refresh every 30 seconds to show new consents
    const interval = setInterval(() => {
      fetchPatients()
    }, 30000) // 30 seconds
    
    // Cleanup interval on unmount
    return () => clearInterval(interval)
  }, [])

  const loadEscalations = async () => {
    try {
      const response = await professionalsAPI.getEscalations()
      setEscalations(response.data)
    } catch (err) {
      // Silently handle 403 errors for now since escalations require additional verification
      console.log('Escalations not available:', err.response?.status)
    } finally {
      setLoading(false)
    }
  }

  const loadTicketDetail = async (id) => {
    try {
      const response = await professionalsAPI.getEscalationDetail(id)
      setSelectedTicket(response.data)
    } catch (err) {
      alert('Failed to load ticket details')
    }
  }

  const handleSubmitVerdict = async (e) => {
    e.preventDefault()
    if (!verdict) {
      alert('Please select a verdict')
      return
    }

    setSubmitting(true)

    try {
      await professionalsAPI.submitVerdict(selectedTicket.id, { verdict, professional_notes: notes })
      alert('Verdict submitted successfully')
      setSelectedTicket(null)
      setVerdict('')
      setNotes('')
      await loadEscalations()
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to submit verdict')
    } finally {
      setSubmitting(false)
    }
  }

  const handleLoadAISummary = async (patientId) => {
    setLoadingSummary(true)
    try {
      const response = await professionalsAPI.getPatientSummary(patientId)
      setAiSummary(response.data)
    } catch (err) {
      console.error('Error loading AI summary:', err)
      alert(err.response?.data?.error || 'Failed to load AI summary')
    } finally {
      setLoadingSummary(false)
    }
  }

  const handleSaveAvailability = () => {
    // TODO: Implement API call to save availability
    alert('Availability saved successfully!')
  }

  const handleSaveProfile = () => {
    // TODO: Implement API call to save profile info
    alert('Profile updated successfully!')
  }

  const handleVerified = async () => {
    setIsVerified(true)
    setShowVerificationModal(false)
    // Refresh user data
    try {
      const response = await professionalsAPI.getProfile()
      // Update user context if needed
      if (setUser) {
        setUser(prev => ({
          ...prev,
          professional_profile: response.data
        }))
      }
    } catch (err) {
      console.error('Error refreshing profile:', err)
    }
  }

  const handleShowVerification = () => {
    setShowVerificationModal(true)
  }

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const handleModalLoadAISummary = async (patient) => {
    setModalLoadingSummary(true)
    try {
      const response = await professionalsAPI.getPatientSummary(patient.id)
      // Map recentEntries to historyEntries for backward compatibility
      const summary = response.data
      setModalAiSummary({
        ...summary,
        historyEntries: summary.recentEntries || []
      })
    } catch (err) {
      console.error('Error loading AI summary:', err)
      alert(err.response?.data?.error || 'Failed to load AI summary')
    } finally {
      setModalLoadingSummary(false)
    }
  }

  const tabs = [
    { id: 'patients', label: 'My Patients', icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    )},
    { id: 'escalations', label: 'Escalations', icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    )}
  ]

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
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <svg className="w-10 h-10" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h1 className="text-4xl font-bold" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 800, color: '#3F3F3F' }}>Professional Dashboard</h1>
          </div>
          <p style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Manage your patients, availability, and escalations</p>
        </motion.div>

        {/* Quick Access Tiles */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <h2 className="text-xl font-semibold mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Quick Access</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <motion.div
              whileHover={{ y: -8, scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowPatientHistoryModal(true)}
              className="card-3d p-8 cursor-pointer group relative overflow-hidden"
            >
              <div className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-300" style={{ background: 'rgba(241, 90, 42, 0.05)' }} />
              <div className="relative z-10">
                <div className="mb-6" style={{ color: '#F15A2A' }}>
                  <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <h3 className="text-3xl font-bold mb-3" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>See Patient History</h3>
                <p className="text-lg" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>View detailed journal histories and AI insights from patients who have shared their data with you</p>
              </div>
              <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: '#F15A2A' }}>
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <div className="flex space-x-1">
            {tabs.map((tab) => (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`flex items-center gap-2 px-6 py-3 font-medium transition-all rounded-t-lg ${
                  activeTab === tab.id
                    ? 'border-b-2'
                    : 'hover:bg-gray-50'
                }`}
                style={activeTab === tab.id
                  ? { background: 'rgba(241, 90, 42, 0.05)', color: '#F15A2A', borderColor: '#F15A2A', fontFamily: "'Inter', sans-serif" }
                  : { color: '#3F3F3F', fontFamily: "'Inter', sans-serif" }
                }
              >
                {tab.icon}
                <span>{tab.label}</span>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'patients' && (
            <motion.div
              key="patients"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
              className="grid lg:grid-cols-2 gap-6"
            >
              {/* Patients List */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-semibold flex items-center gap-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                    <svg className="w-6 h-6" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                    <span>Patients Sharing History</span>
                    {newPatientsCount > 0 && (
                      <span className="ml-2 px-2 py-1 text-xs font-bold rounded-full text-white animate-pulse" style={{ background: '#10B981' }}>
                        {newPatientsCount} New
                      </span>
                    )}
                  </h2>
                  <button
                    onClick={fetchPatients}
                    disabled={loadingPatients}
                    className="px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
                    style={{ 
                      background: loadingPatients ? '#ccc' : '#F15A2A', 
                      color: 'white', 
                      fontFamily: "'Inter', sans-serif",
                      cursor: loadingPatients ? 'not-allowed' : 'pointer'
                    }}
                    title="Refresh patient list"
                  >
                    <svg className={`w-4 h-4 ${loadingPatients ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <span>{loadingPatients ? 'Refreshing...' : 'Refresh'}</span>
                  </button>
                </div>
                {loadingPatients ? (
                  <div className="card-3d p-8 text-center">
                    <p className="text-gray-600">Loading patients...</p>
                  </div>
                ) : patients.length === 0 ? (
                  <div className="card-3d p-8 text-center">
                    <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                    <p className="text-gray-600">No patients have shared their history with you yet.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {patients.map((patient) => (
                      <motion.div
                        key={patient.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        whileHover={{ y: -4 }}
                        className="card-3d p-6 cursor-pointer"
                        onClick={() => setSelectedPatient(patient)}
                      >
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h3 className="font-semibold text-lg" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{patient.name}</h3>
                            <p className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{patient.email}</p>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            patient.riskLevel === 'low' ? 'bg-green-100 text-green-800' :
                            patient.riskLevel === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {patient.riskLevel.toUpperCase()}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-3 text-sm">
                          <div>
                            <span style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Shared Since:</span>
                            <p className="font-medium" style={{ fontFamily: "'Inter', sans-serif" }}>{new Date(patient.sharedSince).toLocaleDateString()}</p>
                          </div>
                          <div>
                            <span style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Entries:</span>
                            <p className="font-medium" style={{ fontFamily: "'Inter', sans-serif" }}>{patient.entriesCount}</p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>

              {/* Patient Detail & AI Summary */}
              <div>
                {selectedPatient ? (
                  <div className="space-y-4">
                    <div className="card-3d p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h2 className="text-2xl font-semibold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{selectedPatient.name}</h2>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => handleLoadAISummary(selectedPatient.id)}
                          disabled={loadingSummary}
                          className="px-4 py-2 flex items-center gap-2 rounded-xl font-medium transition-all"
                          style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                          {loadingSummary ? 'Generating...' : 'AI Summary'}
                        </motion.button>
                      </div>

                      <div className="space-y-3">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="rounded-lg p-3" style={{ background: 'rgba(241, 90, 42, 0.05)' }}>
                            <p className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Total Entries</p>
                            <p className="text-2xl font-bold" style={{ color: '#F15A2A', fontFamily: "'Inter', sans-serif" }}>{selectedPatient.entriesCount}</p>
                          </div>
                          <div className="rounded-lg p-3" style={{ background: 'rgba(241, 90, 42, 0.05)' }}>
                            <p className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Risk Level</p>
                            <p className="text-2xl font-bold capitalize" style={{ color: '#F15A2A', fontFamily: "'Inter', sans-serif" }}>{selectedPatient.riskLevel}</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* AI Summary */}
                    {aiSummary && aiSummary.patientId === selectedPatient.id && (
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="card-3d p-6 space-y-4"
                      >
                        <h3 className="text-xl font-semibold flex items-center gap-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                          <svg className="w-6 h-6" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                          AI-Generated Summary
                        </h3>

                        <div className="space-y-4">
                          <div>
                            <h4 className="font-semibold mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Overview</h4>
                            <p style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{aiSummary.overview}</p>
                          </div>

                          <div>
                            <h4 className="font-semibold mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Key Themes</h4>
                            <div className="flex flex-wrap gap-2">
                              {aiSummary.keyThemes.map((theme, idx) => (
                                <span key={idx} className="badge badge-primary">{theme}</span>
                              ))}
                            </div>
                          </div>

                          <div>
                            <h4 className="font-semibold mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Risk Indicators</h4>
                            <ul className="list-disc list-inside space-y-1" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                              {aiSummary.riskIndicators.map((risk, idx) => (
                                <li key={idx}>{risk}</li>
                              ))}
                            </ul>
                          </div>

                          <div>
                            <h4 className="font-semibold mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Recommendations</h4>
                            <ul className="list-disc list-inside space-y-1" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                              {aiSummary.recommendations.map((rec, idx) => (
                                <li key={idx}>{rec}</li>
                              ))}
                            </ul>
                          </div>

                          <div>
                            <h4 className="font-semibold mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Recent Entries</h4>
                            <div className="space-y-2">
                              {aiSummary.recentEntries.map((entry, idx) => (
                                <div key={idx} className="bg-gray-50 rounded-lg p-3">
                                  <div className="flex justify-between items-start mb-1">
                                    <span className="text-sm font-medium" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                                      {new Date(entry.date).toLocaleDateString()}
                                    </span>
                                    <span className={`text-xs font-medium ${
                                      entry.sentiment > 0.5 ? 'text-green-600' :
                                      entry.sentiment > 0.3 ? 'text-yellow-600' :
                                      'text-orange-600'
                                    }`} style={{ fontFamily: "'Inter', sans-serif" }}>
                                      Sentiment: {(entry.sentiment * 100).toFixed(0)}%
                                    </span>
                                  </div>
                                  <p className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{entry.summary}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </div>
                ) : (
                  <div className="card-3d p-8 text-center">
                    <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <p className="text-gray-600">Select a patient to view details and generate AI summary</p>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'escalations' && (
            <motion.div
              key="escalations"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
              className="grid lg:grid-cols-2 gap-6"
            >
              {/* Escalations List */}
              <div>
                <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                  <svg className="w-6 h-6" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Pending Escalations
                </h2>

                {escalations.length === 0 ? (
                  <div className="card-3d p-8 text-center">
                    <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-gray-600">No pending escalations.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {escalations.map((ticket) => (
                      <motion.div
                        key={ticket.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        whileHover={{ y: -4 }}
                        className="card-3d p-6 cursor-pointer"
                        onClick={() => loadTicketDetail(ticket.id)}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <div className="font-semibold text-gray-900">Ticket #{ticket.id}</div>
                            <div className="text-sm text-gray-600">
                              User: {ticket.user.display_name}
                            </div>
                          </div>
                          <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs font-medium">
                            {ticket.status}
                          </span>
                        </div>
                        <div className="text-sm text-gray-700 mt-2">{ticket.reason}</div>
                        <div className="text-xs text-gray-500 mt-2">
                          {new Date(ticket.created_at).toLocaleString()}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>

              {/* Ticket Detail */}
              <div>
                {selectedTicket ? (
                  <div className="card-3d p-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">
                      Ticket #{selectedTicket.id}
                    </h2>
                    <div className="space-y-4 mb-6">
                      <div>
                        <div className="text-sm text-gray-600">User</div>
                        <div className="font-medium">{selectedTicket.user.display_name}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Reason</div>
                        <div className="text-gray-900">{selectedTicket.reason}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Created</div>
                        <div className="text-gray-900">
                          {new Date(selectedTicket.created_at).toLocaleString()}
                        </div>
                      </div>
                    </div>

                    {selectedTicket.status === 'pending' && (
                      <form onSubmit={handleSubmitVerdict} className="space-y-4">
                        <div>
                          <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Verdict *
                          </label>
                          <select
                            value={verdict}
                            onChange={(e) => setVerdict(e.target.value)}
                            required
                            className="input-modern"
                          >
                            <option value="">Select verdict</option>
                            <option value="consult_required">Consult Required</option>
                            <option value="monitor">Monitor</option>
                            <option value="no_action">No Action</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Professional Notes
                          </label>
                          <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            rows={4}
                            className="input-modern resize-none"
                            placeholder="Add your notes..."
                          />
                        </div>
                        <div className="flex space-x-4">
                          <motion.button
                            type="submit"
                            disabled={submitting}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="flex-1 py-3 disabled:opacity-50 rounded-xl font-medium transition-all"
                            style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
                          >
                            {submitting ? 'Submitting...' : 'Submit Verdict'}
                          </motion.button>
                          <motion.button
                            type="button"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => {
                              setSelectedTicket(null)
                              setVerdict('')
                              setNotes('')
                            }}
                            className="px-6 py-3 bg-white rounded-xl hover:bg-gray-50 transition-colors font-medium"
                            style={{ border: '2px solid rgba(241, 90, 42, 0.2)', color: '#3F3F3F', fontFamily: "'Inter', sans-serif" }}
                          >
                            Close
                          </motion.button>
                        </div>
                      </form>
                    )}
                  </div>
                ) : (
                  <div className="card-3d p-8 text-center">
                    <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <p className="text-gray-600">Select a ticket to review</p>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Patient History Modal */}
        <AnimatePresence>
          {showPatientHistoryModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
              onClick={() => {
                setShowPatientHistoryModal(false)
                setModalSelectedPatient(null)
                setModalAiSummary(null)
              }}
            >
              <motion.div
                initial={{ scale: 0.9, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.9, y: 20 }}
                onClick={(e) => e.stopPropagation()}
                className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden"
              >
                {/* Modal Header */}
                <div className="p-6 text-white" style={{ background: '#F15A2A' }}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                      </svg>
                      <h2 className="text-2xl font-bold">Patient History</h2>
                    </div>
                    <button
                      onClick={() => {
                        setShowPatientHistoryModal(false)
                        setModalSelectedPatient(null)
                        setModalAiSummary(null)
                      }}
                      className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
                    >
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Modal Body */}
                <div className="grid lg:grid-cols-2 gap-6 p-6 max-h-[calc(90vh-120px)] overflow-y-auto">
                  {/* Patient List */}
                  <div>
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-xl font-semibold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Patients Sharing History</h3>
                      <button
                        onClick={fetchPatients}
                        disabled={loadingPatients}
                        className="px-3 py-1 text-sm rounded-lg transition-colors flex items-center gap-2"
                        style={{ 
                          background: loadingPatients ? '#ccc' : '#F15A2A', 
                          color: 'white', 
                          fontFamily: "'Inter', sans-serif",
                          cursor: loadingPatients ? 'not-allowed' : 'pointer'
                        }}
                        title="Refresh patient list"
                      >
                        <svg className={`w-4 h-4 ${loadingPatients ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <span>{loadingPatients ? 'Refreshing...' : 'Refresh'}</span>
                      </button>
                    </div>
                    {loadingPatients ? (
                      <div className="card-3d p-8 text-center">
                        <p className="text-gray-600">Loading patients...</p>
                      </div>
                    ) : patients.length === 0 ? (
                      <div className="card-3d p-8 text-center">
                        <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                        </svg>
                        <p className="text-gray-600">No patients have shared their history with you yet.</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {patients.map((patient) => (
                          <motion.div
                            key={patient.id}
                            whileHover={{ x: 4 }}
                            className={`p-4 rounded-lg cursor-pointer transition-all ${
                              modalSelectedPatient?.id === patient.id
                                ? 'border-2'
                                : 'bg-gray-50 border-2 border-transparent hover:border-gray-300'
                            }`}
                            style={modalSelectedPatient?.id === patient.id
                              ? { background: 'rgba(241, 90, 42, 0.05)', borderColor: '#F15A2A' }
                              : {}
                            }
                            onClick={() => {
                              setModalSelectedPatient(patient)
                              setModalAiSummary(null)
                            }}
                          >
                            <div className="flex justify-between items-start mb-2">
                              <div>
                                <h4 className="font-semibold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{patient.name}</h4>
                                <p className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{patient.email}</p>
                              </div>
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                patient.riskLevel === 'low' ? 'bg-green-100 text-green-800' :
                                patient.riskLevel === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {patient.riskLevel.toUpperCase()}
                              </span>
                            </div>
                            <div className="flex gap-4 text-xs text-gray-600">
                              <span>{patient.entriesCount} entries</span>
                              <span>Last: {patient.lastEntry ? new Date(patient.lastEntry).toLocaleDateString() : 'N/A'}</span>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Patient Detail & AI Summary */}
                  <div>
                    {modalSelectedPatient ? (
                      <div className="space-y-4">
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-4">
                            <h3 className="text-xl font-semibold" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{modalSelectedPatient.name}</h3>
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => handleModalLoadAISummary(modalSelectedPatient)}
                              disabled={modalLoadingSummary}
                              className="px-4 py-2 flex items-center gap-2 text-sm rounded-xl font-medium transition-all"
                              style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                              </svg>
                              {modalLoadingSummary ? 'Loading...' : 'AI Summary'}
                            </motion.button>
                          </div>

                          <div className="grid grid-cols-3 gap-3">
                            <div className="bg-white rounded p-3 text-center">
                              <p className="text-xs" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Entries</p>
                              <p className="text-lg font-bold" style={{ color: '#F15A2A', fontFamily: "'Inter', sans-serif" }}>{modalSelectedPatient.entriesCount}</p>
                            </div>
                            <div className="bg-white rounded p-3 text-center">
                              <p className="text-xs" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Risk Level</p>
                              <p className="text-lg font-bold capitalize" style={{ color: '#F15A2A', fontFamily: "'Inter', sans-serif" }}>{modalSelectedPatient.riskLevel}</p>
                            </div>
                            <div className="bg-white rounded p-3 text-center">
                              <p className="text-xs" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Sharing Since</p>
                              <p className="text-xs font-medium mt-1" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{new Date(modalSelectedPatient.sharedSince).toLocaleDateString()}</p>
                            </div>
                          </div>
                        </div>

                        {/* AI Summary */}
                        {modalAiSummary && modalAiSummary.patientId === modalSelectedPatient.id && (
                          <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white rounded-lg p-4 space-y-4 max-h-[600px] overflow-y-auto"
                            style={{ border: '2px solid rgba(241, 90, 42, 0.2)' }}
                          >
                            <h4 className="text-lg font-semibold flex items-center gap-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                              <svg className="w-5 h-5" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                              </svg>
                              AI-Generated Summary
                            </h4>

                            <div className="space-y-3">
                              <div>
                                <h5 className="font-semibold text-sm mb-1" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Overview</h5>
                                <p className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{modalAiSummary.overview}</p>
                              </div>

                              <div>
                                <h5 className="font-semibold text-sm mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Key Themes</h5>
                                <div className="flex flex-wrap gap-2">
                                  {modalAiSummary.keyThemes.map((theme, idx) => (
                                    <span key={idx} className="badge badge-primary text-xs">{theme}</span>
                                  ))}
                                </div>
                              </div>

                              <div>
                                <h5 className="font-semibold text-sm mb-1" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Risk Indicators</h5>
                                <ul className="list-disc list-inside text-sm space-y-1" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                                  {modalAiSummary.riskIndicators.map((risk, idx) => (
                                    <li key={idx} className={risk.includes('HIGH RISK') ? 'text-red-600 font-semibold' : ''}>{risk}</li>
                                  ))}
                                </ul>
                              </div>

                              <div>
                                <h5 className="font-semibold text-sm mb-1" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Recommendations</h5>
                                <ul className="list-disc list-inside text-sm space-y-1" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                                  {modalAiSummary.recommendations.map((rec, idx) => (
                                    <li key={idx} className={rec.includes('URGENT') ? 'text-red-600 font-semibold' : ''}>{rec}</li>
                                  ))}
                                </ul>
                              </div>

                              <div>
                                <h5 className="font-semibold text-sm mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Recent Journal Entries</h5>
                                <div className="space-y-2">
                                  {modalAiSummary.historyEntries.map((entry, idx) => (
                                    <div key={idx} className="bg-gray-50 rounded p-3 text-sm">
                                      <div className="flex justify-between items-start mb-1">
                                        <span className="font-medium text-xs" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                                          {new Date(entry.date).toLocaleDateString()}
                                        </span>
                                        <span className={`text-xs font-medium ${
                                          entry.sentiment > 0.5 ? 'text-green-600' :
                                          entry.sentiment > 0.3 ? 'text-yellow-600' :
                                          'text-red-600'
                                        }`} style={{ fontFamily: "'Inter', sans-serif" }}>
                                          Sentiment: {(entry.sentiment * 100).toFixed(0)}%
                                        </span>
                                      </div>
                                      <p className="text-xs mb-1" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Mood: {entry.mood}</p>
                                      <p className="text-xs" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>{entry.summary}</p>
                                      {entry.riskFlags && entry.riskFlags.length > 0 && (
                                        <div className="mt-2 flex flex-wrap gap-1">
                                          {entry.riskFlags.map((flag, i) => (
                                            <span key={i} className="text-xs bg-red-100 text-red-800 px-2 py-0.5 rounded">
                                              {flag}
                                            </span>
                                          ))}
                                        </div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </div>
                    ) : (
                      <div className="bg-gray-50 rounded-lg p-8 text-center h-full flex items-center justify-center">
                        <div>
                          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                          <p className="text-gray-600">Select a patient to view details and generate AI summary</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Verification Overlay */}
        {!isVerified && !checkingVerification && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 bg-black bg-opacity-60 z-40 flex items-center justify-center p-4"
            style={{ pointerEvents: 'all' }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 text-center"
            >
              <div className="w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center"
                style={{ background: 'rgba(241, 90, 42, 0.1)' }}>
                <svg className="w-12 h-12" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                Verify to Gain Full Access
              </h3>
              <p className="text-gray-600 mb-6" style={{ fontFamily: "'Inter', sans-serif" }}>
                Please complete your identity verification to access the professional dashboard and all its features.
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleShowVerification}
                className="px-8 py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2 mx-auto"
                style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span>Verify Now</span>
              </motion.button>
            </motion.div>
          </motion.div>
        )}

        {/* Verification Modal */}
        {showVerificationModal && (
          <VerificationModal
            onClose={() => setShowVerificationModal(false)}
            onVerified={handleVerified}
            onLogout={handleLogout}
            canSkip={false}
          />
        )}
      </div>
    </Layout>
  )
}

export default ProfessionalDashboard
