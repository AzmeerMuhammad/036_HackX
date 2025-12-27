import { useState, useEffect, useRef } from 'react'
import Layout from '../components/Layout'
import { chatAPI } from '../api/chat'
import { useAuth } from '../contexts/AuthContext'
import { motion, AnimatePresence } from 'framer-motion'

const Chat = () => {
  const { user } = useAuth()
  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [isAnonymous, setIsAnonymous] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    initializeSession()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const initializeSession = async () => {
    try {
      const response = await chatAPI.getOrCreateSession()
      setSession(response.data)
      // Sync anonymous mode with session
      setIsAnonymous(response.data.is_anonymous || false)
      await loadMessages(response.data.id)
    } catch (err) {
      setError('Failed to initialize chat session')
    }
  }

  const loadMessages = async (sessionId) => {
    try {
      const response = await chatAPI.getMessages(sessionId)
      setMessages(response.data)
    } catch (err) {
      console.error('Failed to load messages', err)
    }
  }

  const toggleAnonymousMode = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (!session) {
      console.warn('Cannot toggle anonymous mode: session not loaded yet')
      setError('Please wait for chat session to load')
      return
    }
    
    console.log('Toggling anonymous mode:', { current: isAnonymous, sessionId: session.id })
    const newAnonymousMode = !isAnonymous
    setIsAnonymous(newAnonymousMode)

    try {
      // Update session's anonymous mode
      console.log('Sending update request:', { sessionId: session.id, is_anonymous: newAnonymousMode })
      const response = await chatAPI.updateSession(session.id, { is_anonymous: newAnonymousMode })
      console.log('Update response:', response.data)
      setSession(response.data)
      setError('') // Clear any previous errors
    } catch (error) {
      console.error('Failed to update anonymous mode:', error)
      console.error('Error details:', error.response?.data)
      setError(error.response?.data?.error || error.message || 'Failed to update anonymous mode')
      setIsAnonymous(!newAnonymousMode) // Revert on error
    }
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || !session) return

    const userMessage = input
    setInput('')
    setLoading(true)
    setError('')

    try {
      const response = await chatAPI.sendMessage(session.id, userMessage)
      setMessages([...messages, response.data.user_message, response.data.bot_message])

      if (response.data.escalated) {
        setError('✅ Your conversation has been escalated to a professional for review.')
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to send message')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ color: '#F15A2A' }}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <h1 className="text-4xl font-bold" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 800, color: '#3F3F3F' }}>Chat Support</h1>
            </div>
            {/* Anonymous Mode Toggle */}
            <motion.button
              type="button"
              whileHover={session ? { scale: 1.05 } : {}}
              whileTap={session ? { scale: 0.95 } : {}}
              onClick={toggleAnonymousMode}
              disabled={!session}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all shadow-sm ${
                !session
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed opacity-50'
                  : isAnonymous
                  ? 'bg-orange-500 text-white hover:bg-orange-600 cursor-pointer'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 cursor-pointer'
              }`}
              style={{ fontFamily: "'Inter', sans-serif" }}
              title={!session ? 'Loading session...' : (isAnonymous ? 'Anonymous mode: ON - Your identity is hidden' : 'Anonymous mode: OFF - Click to enable')}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                {isAnonymous ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                ) : (
                  <>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </>
                )}
              </svg>
              <span className="text-sm font-medium">
                {isAnonymous ? 'Anonymous' : 'Visible'}
              </span>
            </motion.button>
          </div>
          <p style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Talk to our empathetic AI chatbot anytime</p>
        </motion.div>

        {/* Disclaimer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="card-3d p-4 mb-6 bg-yellow-50 border-2 border-yellow-200"
        >
          <div className="flex items-start space-x-3">
            <svg className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p className="text-sm" style={{ fontFamily: "'Inter', sans-serif", color: '#78350F' }}>
              <strong>Important:</strong> This chatbot provides emotional support and information.
              It does NOT provide medical advice, diagnosis, or therapy.
              If you're in crisis, please contact emergency services immediately.
            </p>
          </div>
        </motion.div>

        {/* Error/Success Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className={`${error.includes('✅') ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-700'} border-2 px-4 py-3 rounded-xl mb-4 flex items-center space-x-2`}
            >
              <span>{error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Chat Container */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className={`card-3d h-[600px] flex flex-col overflow-hidden transition-all duration-300 ${
            isAnonymous ? 'border-2 border-orange-300 shadow-lg' : ''
          }`}
          style={isAnonymous ? { 
            background: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)',
            boxShadow: '0 10px 25px rgba(251, 146, 60, 0.2)'
          } : {}}
        >
          {/* Anonymous Mode Banner */}
          {isAnonymous && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-orange-100 border-b-2 border-orange-300 px-4 py-2 flex items-center space-x-2"
            >
              <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <span className="text-sm font-medium text-orange-800" style={{ fontFamily: "'Inter', sans-serif" }}>
                Anonymous Mode Active - Your identity is protected
              </span>
            </motion.div>
          )}
          {/* Messages Area */}
          <div className={`flex-1 overflow-y-auto p-6 space-y-4 transition-all duration-300 ${
            isAnonymous 
              ? 'bg-gradient-to-b from-orange-50/50 to-orange-100/30' 
              : 'bg-gradient-to-b from-gray-50 to-white'
          }`}>
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="mb-4">
                  <svg className="w-20 h-20 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ color: '#F15A2A' }}>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>Welcome to SafeSpace Chat</h3>
                <p className="max-w-md" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                  Start a conversation by typing a message below. I'm here to listen and support you.
                </p>
              </div>
            ) : (
              <AnimatePresence>
                {messages.map((message, idx) => (
                  <motion.div
                    key={message.id || idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex items-start space-x-2 max-w-[75%] ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                      {/* Avatar */}
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                        message.sender === 'user' ? 'text-white' : 'bg-gray-300 text-gray-700'
                      }`}
                      style={message.sender === 'user' 
                        ? { background: isAnonymous ? '#ea580c' : '#F15A2A' } 
                        : {}}>
                        {message.sender === 'user' ? (
                          isAnonymous ? (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                          ) : (
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                            </svg>
                          )
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                        )}
                      </div>

                      {/* Message Bubble */}
                      <div
                        className={`px-4 py-3 rounded-2xl shadow-sm transition-all duration-300 ${
                          message.sender === 'user'
                            ? `text-white rounded-tr-sm ${isAnonymous ? 'border-2 border-orange-400' : ''}`
                            : 'bg-white border-2 border-gray-200 rounded-tl-sm'
                        }`}
                        style={message.sender === 'user' 
                          ? { 
                              background: isAnonymous ? '#ea580c' : '#F15A2A', 
                              fontFamily: "'Inter', sans-serif",
                              boxShadow: isAnonymous ? '0 4px 12px rgba(234, 88, 12, 0.3)' : undefined
                            } 
                          : { 
                              fontFamily: "'Inter', sans-serif", 
                              color: '#3F3F3F',
                              background: isAnonymous ? '#fff7ed' : 'white'
                            }}
                      >
                        <div className="text-xs opacity-75 mb-1 font-medium" style={{ fontFamily: "'Inter', sans-serif" }}>
                          {message.sender === 'user' ? (isAnonymous ? 'Anonymous User' : 'You') : 'Support Bot'}
                        </div>
                        <div className="text-sm leading-relaxed" style={{ fontFamily: "'Inter', sans-serif" }}>{message.content_encrypted}</div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            )}

            {/* Typing Indicator */}
            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="flex items-center space-x-2 px-4 py-3 bg-white border-2 border-gray-200 rounded-2xl rounded-tl-sm">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <form onSubmit={handleSend} className={`border-t-2 p-4 transition-all duration-300 ${
            isAnonymous ? 'border-orange-300 bg-orange-50/50' : 'border-gray-200 bg-white'
          }`}>
            <div className="flex space-x-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 input-modern"
                disabled={loading || !session}
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="submit"
                disabled={loading || !session || !input.trim()}
                className="px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 rounded-lg"
                style={{ background: '#F15A2A', color: 'white', fontFamily: "'Inter', sans-serif" }}
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Sending</span>
                  </>
                ) : (
                  <>
                    <span>Send</span>
                    <span>📤</span>
                  </>
                )}
              </motion.button>
            </div>
          </form>
        </motion.div>

        {/* Help Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-6 text-center text-sm"
          style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}
        >
          💡 Tip: Be open and honest. The AI is here to help you work through your thoughts and feelings.
        </motion.div>
      </div>
    </Layout>
  )
}

export default Chat
