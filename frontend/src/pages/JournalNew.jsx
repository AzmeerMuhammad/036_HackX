import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { journalAPI } from '../api/journal'
import { motion } from 'framer-motion'

const JournalNew = () => {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [isListening, setIsListening] = useState(false)
  const [voiceSupported, setVoiceSupported] = useState(false)
  const recognitionRef = useRef(null)
  const finalTranscriptRef = useRef('') // Store final transcript separately
  const navigate = useNavigate()

  useEffect(() => {
    // Check if browser supports Web Speech API
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setVoiceSupported(true)
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      
      try {
        recognitionRef.current = new SpeechRecognition()
        recognitionRef.current.continuous = true
        recognitionRef.current.interimResults = true
        recognitionRef.current.lang = 'en-US' // Can be changed to 'ur-PK' for Urdu

        recognitionRef.current.onresult = (event) => {
          let interimTranscript = ''
          let finalTranscript = ''

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript
            if (event.results[i].isFinal) {
              finalTranscript += transcript + ' '
            } else {
              interimTranscript += transcript
            }
          }

          // Update final transcript
          if (finalTranscript) {
            finalTranscriptRef.current += finalTranscript
            setText(finalTranscriptRef.current + interimTranscript)
          } else if (interimTranscript) {
            // Show final + interim in real-time
            setText(finalTranscriptRef.current + interimTranscript)
          }
        }

        recognitionRef.current.onerror = (event) => {
          console.error('Speech recognition error:', event.error)
          setIsListening(false)
          
          let errorMessage = 'Speech recognition error occurred.'
          switch (event.error) {
            case 'no-speech':
              errorMessage = 'No speech detected. Please speak clearly and try again.'
              break
            case 'not-allowed':
              errorMessage = 'Microphone access denied. Please allow microphone permissions in your browser settings.'
              break
            case 'audio-capture':
              errorMessage = 'No microphone found. Please connect a microphone.'
              break
            case 'network':
              errorMessage = 'Network error. Please check your internet connection.'
              break
            case 'aborted':
              // User stopped manually, don't show error
              return
            default:
              errorMessage = `Speech recognition error: ${event.error}`
          }
          setError(errorMessage)
        }

        recognitionRef.current.onend = () => {
          setIsListening(false)
        }

        recognitionRef.current.onstart = () => {
          setError('')
        }
      } catch (err) {
        console.error('Failed to initialize speech recognition:', err)
        setVoiceSupported(false)
        setError('Failed to initialize voice recognition. Please refresh the page.')
      }
    } else {
      setVoiceSupported(false)
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop()
        } catch (e) {
          // Ignore errors on cleanup
        }
      }
    }
  }, [])

  const toggleVoiceInput = () => {
    if (!voiceSupported) {
      setError('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.')
      return
    }

    if (isListening) {
      try {
        recognitionRef.current.stop()
        setIsListening(false)
      } catch (err) {
        console.error('Error stopping recognition:', err)
        setIsListening(false)
      }
    } else {
      setError('')
      // Reset final transcript when starting new session
      finalTranscriptRef.current = text
      try {
        recognitionRef.current.start()
        setIsListening(true)
      } catch (err) {
        console.error('Error starting recognition:', err)
        setError('Failed to start voice recognition. Please try again.')
        setIsListening(false)
      }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!text.trim()) {
      setError('Please enter some text')
      return
    }

    setLoading(true)
    setError('')

    // Stop voice recording if active
    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    }

    try {
      const formData = {
        text,
        checkin_mood: '',
        checkin_intensity: 0.5,
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
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <svg className="w-10 h-10" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <h1 className="text-4xl font-bold" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 800, color: '#3F3F3F' }}>New Journal Entry</h1>
          </div>
          <p style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Express your thoughts and let AI provide insights</p>
        </motion.div>

        {!result ? (
          <motion.form
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            onSubmit={handleSubmit}
            className="card-3d p-8 space-y-6"
          >
            {error && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-red-50 border-2 border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center space-x-2"
              >
                <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>{error}</span>
              </motion.div>
            )}

            <div>
              <label className="block text-sm font-semibold mb-3 flex items-center gap-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                <svg className="w-5 h-5" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
                <span>Journal Entry <span className="text-red-500">*</span></span>
              </label>

              <div className="relative">
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={12}
                  required
                  placeholder={isListening
                    ? "Speak now... Your words will appear here as you speak."
                    : "Write about your thoughts, feelings, or experiences... This is your safe space."}
                  className="input-modern resize-none font-serif pr-24"
                  disabled={isListening && !text}
                />

                {/* Voice Button - Bottom Right Corner */}
                <div className="absolute bottom-3 right-3 flex items-center gap-2">
                  {/* Recording Indicator */}
                  {isListening && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      className="flex items-center gap-2 bg-gradient-to-r from-red-500 via-pink-500 to-red-600 text-white px-4 py-2 rounded-full text-xs font-bold shadow-lg shadow-red-500/50 border-2 border-white/30"
                    >
                      {/* Pulsing dot */}
                      <motion.span
                        animate={{
                          scale: [1, 1.4, 1],
                          opacity: [1, 0.7, 1]
                        }}
                        transition={{
                          duration: 1,
                          repeat: Infinity,
                          ease: "easeInOut"
                        }}
                        className="w-2 h-2 bg-white rounded-full shadow-lg"
                      />
                      <span className="tracking-wide">Recording</span>
                    </motion.div>
                  )}

                  {/* Round Voice Button */}
                  {voiceSupported ? (
                    <motion.button
                      type="button"
                      onClick={toggleVoiceInput}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className={`relative overflow-hidden w-12 h-12 rounded-full font-bold transition-all duration-300 border-2 flex items-center justify-center ${
                        isListening
                          ? 'bg-gradient-to-r from-red-500 via-pink-500 to-red-600 text-white shadow-xl shadow-red-500/60 border-red-300'
                          : 'text-white shadow-lg hover:shadow-xl'
                      }`}
                      style={!isListening ? { background: '#F15A2A', borderColor: 'rgba(241, 90, 42, 0.3)' } : {}}
                    >
                      {/* Animated pulsing background when listening */}
                      {isListening && (
                        <>
                          <motion.div
                            className="absolute inset-0 bg-gradient-to-r from-red-400 via-pink-500 to-red-600"
                            animate={{
                              backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                            }}
                            transition={{
                              duration: 2,
                              repeat: Infinity,
                              ease: "linear"
                            }}
                            style={{
                              backgroundSize: '200% 200%',
                            }}
                          />
                          {/* Pulsing rings */}
                          <motion.div
                            className="absolute inset-0 rounded-full border-2 border-white/40"
                            animate={{
                              scale: [1, 1.3, 1],
                              opacity: [0.6, 0, 0.6],
                            }}
                            transition={{
                              duration: 1.5,
                              repeat: Infinity,
                              ease: "easeInOut"
                            }}
                          />
                        </>
                      )}

                      {/* Microphone Icon */}
                      <div className="relative z-10">
                        {isListening ? (
                          <motion.div
                            animate={{ scale: [1, 1.15, 1] }}
                            transition={{ duration: 1, repeat: Infinity, ease: "easeInOut" }}
                          >
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                            </svg>
                          </motion.div>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                          </svg>
                        )}
                      </div>

                      {/* Shimmer effect when not listening */}
                      {!isListening && (
                        <motion.div
                          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                          animate={{ x: ['-200%', '200%'] }}
                          transition={{ duration: 2, repeat: Infinity, repeatDelay: 1, ease: "easeInOut" }}
                        />
                      )}
                    </motion.button>
                  ) : (
                    <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex justify-between items-center text-xs text-gray-500 mt-2">
                <span>{text.length} characters</span>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full py-4 text-base disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 rounded-xl font-medium transition-all"
              style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Analyzing your entry...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Submit & Analyze</span>
                </>
              )}
            </motion.button>
          </motion.form>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
            className="space-y-6"
          >
            {/* Success Header */}
            <div className="card-3d p-6 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200">
              <div className="flex items-center space-x-3">
                <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Entry Saved Successfully!</h2>
                  <p className="text-gray-600">AI analysis completed</p>
                </div>
              </div>
            </div>

            {/* AI Summary */}
            <div className="card-3d p-6">
              <h3 className="font-bold text-lg mb-3 flex items-center space-x-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                <svg className="w-6 h-6" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span>AI Summary</span>
              </h3>
              <p className="text-gray-700 leading-relaxed">{result.ai_summary}</p>
            </div>

            {/* Scores */}
            <div className="grid grid-cols-2 gap-4">
              <div className="card-3d p-6 text-center">
                <div className="text-sm mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Sentiment Score</div>
                <div className={`text-4xl font-bold ${result.sentiment_score >= 0 ? 'text-green-600' : 'text-orange-600'}`} style={{ fontFamily: "'Inter', sans-serif" }}>
                  {result.sentiment_score > 0 ? '+' : ''}{result.sentiment_score.toFixed(2)}
                </div>
                <div className="text-xs text-gray-500 mt-2 flex items-center justify-center gap-1">
                  {result.sentiment_score >= 0 ? (
                    <>
                      <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>Positive</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>Needs attention</span>
                    </>
                  )}
                </div>
              </div>
              <div className="card-3d p-6 text-center">
                <div className="text-sm mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Intensity Score</div>
                <div className="text-4xl font-bold" style={{ color: '#F15A2A', fontFamily: "'Inter', sans-serif" }}>
                  {result.sentiment_score < 0 && result.detected_emotions && result.detected_emotions.length > 0
                    ? (result.detected_emotions.reduce((sum, e) => sum + e.confidence, 0) / result.detected_emotions.length).toFixed(2)
                    : 'NA'}
                </div>
                <div className="text-xs text-gray-500 mt-2">
                  Emotional intensity
                </div>
              </div>
            </div>

            {/* Detected Emotions */}
            {result.detected_emotions && result.detected_emotions.length > 0 && (
              <div className="card-3d p-6">
                <h3 className="font-bold text-lg mb-3 flex items-center gap-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                  <svg className="w-6 h-6" style={{ color: '#F15A2A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  <span>Detected Emotions</span>
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.detected_emotions.map((emotion, idx) => (
                    <motion.span
                      key={idx}
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: idx * 0.1 }}
                      className="badge badge-primary text-base px-4 py-2 flex items-center gap-2"
                    >
                      <span className="capitalize">{emotion.emotion}</span>
                      <span className="font-bold" style={{ color: '#F15A2A' }}>
                        {Math.round(emotion.confidence * 100)}%
                      </span>
                    </motion.span>
                  ))}
                </div>
              </div>
            )}

            {/* Risk Flags */}
            {result.risk_flags && Object.values(result.risk_flags).some(v => v) && (
              <div className="card-3d p-6 bg-yellow-50 border-2 border-yellow-200">
                <h3 className="font-bold text-lg text-yellow-900 mb-3 flex items-center space-x-2">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span>Risk Flags Detected</span>
                </h3>
                <ul className="list-disc list-inside text-yellow-800 space-y-1">
                  {Object.entries(result.risk_flags)
                    .filter(([_, value]) => value)
                    .map(([key, _]) => (
                      <li key={key} className="capitalize">{key.replace('_', ' ')}</li>
                    ))}
                </ul>
              </div>
            )}

            {/* Suggest Chat */}
            {result.suggest_start_chat && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card-3d p-6 bg-gradient-to-r from-primary-50 to-indigo-50 border-2 border-primary-200"
              >
                <div className="flex items-start space-x-4">
                  <svg className="w-10 h-10 text-purple-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <div className="flex-1">
                    <p className="text-gray-900 mb-4 font-medium">
                      Based on your entry, we recommend starting a chat session for additional support.
                    </p>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => navigate('/chat')}
                      className="px-6 py-3 rounded-xl font-medium transition-all"
                      style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
                    >
                      Start Chat Now
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  setResult(null)
                  setText('')
                }}
                className="flex-1 py-3 bg-white rounded-xl hover:bg-gray-50 transition-colors font-medium shadow-sm flex items-center justify-center gap-2"
                style={{ border: '2px solid rgba(241, 90, 42, 0.2)', color: '#3F3F3F', fontFamily: "'Inter', sans-serif" }}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
                <span>New Entry</span>
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => navigate('/journal/history')}
                className="flex-1 py-3 flex items-center justify-center gap-2 rounded-xl font-medium transition-all"
                style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>View History</span>
              </motion.button>
            </div>
          </motion.div>
        )}
      </div>
    </Layout>
  )
}

export default JournalNew
