import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { professionalsAPI } from '../api/professionals'

const VerificationModal = ({ onClose, onVerified, onLogout, canSkip = false }) => {
  const [step, setStep] = useState('select')
  const [professionalType, setProfessionalType] = useState('')
  const [pmdcId, setPmdcId] = useState('')
  const [degreePicture, setDegreePicture] = useState(null)
  const [universityName, setUniversityName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSelectType = (type) => {
    setProfessionalType(type)
    setStep('documents')
    setError('')
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setDegreePicture(file)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('professional_type', professionalType)

      if (professionalType === 'psychiatrist') {
        if (!pmdcId) {
          setError('PMDC ID is required')
          setLoading(false)
          return
        }
        formData.append('pmdc_id', pmdcId)
      } else {
        if (!degreePicture) {
          setError('Degree picture is required')
          setLoading(false)
          return
        }
        if (!universityName) {
          setError('University name is required')
          setLoading(false)
          return
        }
        formData.append('degree_picture', degreePicture)
        formData.append('university_name', universityName)
      }

      await professionalsAPI.verify(formData)
      setStep('success')
      setTimeout(() => {
        onVerified()
        onClose()
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.error || 'Verification failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
        onClick={canSkip ? onClose : undefined}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ type: 'spring', damping: 25 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden"
        >
          {/* Header */}
          <div className="p-6 text-white" style={{ background: '#F15A2A' }}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <h2 className="text-2xl font-bold" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Verify Your Identity
                </h2>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={onLogout}
                  className="text-white hover:bg-white/20 rounded-lg px-3 py-2 transition-colors flex items-center gap-2"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span className="text-sm font-medium">Logout</span>
                </button>
                {canSkip && (
                  <button
                    onClick={onClose}
                    className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Body */}
          <div className="p-6">
            {step === 'select' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <p className="text-gray-600 mb-6" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Please select your professional type to continue with verification
                </p>

                <div className="space-y-3">
                  {[
                    {
                      value: 'psychiatrist',
                      label: 'Psychiatrist',
                      icon: (
                        <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: 'rgba(241, 90, 42, 0.1)' }}>
                          <svg className="w-7 h-7" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                      )
                    },
                    {
                      value: 'therapist',
                      label: 'Therapist',
                      icon: (
                        <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: 'rgba(241, 90, 42, 0.1)' }}>
                          <svg className="w-7 h-7" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                          </svg>
                        </div>
                      )
                    },
                    {
                      value: 'psychologist',
                      label: 'Psychologist',
                      icon: (
                        <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: 'rgba(241, 90, 42, 0.1)' }}>
                          <svg className="w-7 h-7" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                          </svg>
                        </div>
                      )
                    }
                  ].map((type) => (
                    <motion.button
                      key={type.value}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleSelectType(type.value)}
                      className="w-full p-4 border-2 rounded-xl flex items-center gap-4 transition-all hover:shadow-md"
                      style={{
                        borderColor: 'rgba(241, 90, 42, 0.3)',
                        fontFamily: "'Inter', sans-serif"
                      }}
                    >
                      {type.icon}
                      <span className="text-lg font-semibold" style={{ color: '#3F3F3F' }}>{type.label}</span>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}

            {step === 'documents' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <button
                  onClick={() => setStep('select')}
                  className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors mb-4"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                  Back
                </button>

                <h3 className="text-xl font-bold capitalize" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                  {professionalType} Verification
                </h3>

                {error && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-red-50 border-2 border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center space-x-2"
                  >
                    <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <span style={{ fontFamily: "'Inter', sans-serif" }}>{error}</span>
                  </motion.div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  {professionalType === 'psychiatrist' ? (
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                        PMDC ID <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        value={pmdcId}
                        onChange={(e) => setPmdcId(e.target.value)}
                        placeholder="Enter your PMDC ID"
                        className="input-modern"
                        required
                      />
                    </div>
                  ) : (
                    <>
                      <div>
                        <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                          Degree Certificate <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="file"
                          accept="image/*,.pdf"
                          onChange={handleFileChange}
                          className="input-modern"
                          required
                        />
                        {degreePicture && (
                          <p className="text-sm text-green-600 mt-2">✓ {degreePicture.name}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                          University Name <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={universityName}
                          onChange={(e) => setUniversityName(e.target.value)}
                          placeholder="Enter your university name"
                          className="input-modern"
                          required
                        />
                      </div>
                    </>
                  )}

                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    type="submit"
                    disabled={loading}
                    className="w-full py-3 rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-6"
                    style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Verifying...</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>Submit Verification</span>
                      </>
                    )}
                  </motion.button>
                </form>
              </motion.div>
            )}

            {step === 'success' && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-8"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                  className="w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center"
                  style={{ background: '#10B981' }}
                >
                  <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </motion.div>
                <h3 className="text-2xl font-bold mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                  Verified!
                </h3>
                <p className="text-gray-600" style={{ fontFamily: "'Inter', sans-serif" }}>
                  You now have full access to the dashboard
                </p>
              </motion.div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default VerificationModal
