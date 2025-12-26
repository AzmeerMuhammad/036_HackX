import { useState, useEffect, useRef } from 'react'
import Layout from '../components/Layout'
import { chatAPI } from '../api/chat'
import { motion } from 'framer-motion'

const Chat = () => {
  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const messagesEndRef = useRef(null)

  useEffect(() => {
    initializeSession()
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
        alert('Your conversation has been escalated to a professional. They will review it shortly.')
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to send message')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Chat Support</h1>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-yellow-800">
            <strong>Important:</strong> This chatbot is designed to provide emotional support and gather information. 
            It does NOT provide medical advice, diagnosis, or therapy recommendations. 
            If you're in crisis, please contact emergency services.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="bg-white rounded-xl shadow-md h-[600px] flex flex-col">
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                Start a conversation by typing a message below.
              </div>
            ) : (
              messages.map((message, idx) => (
                <motion.div
                  key={message.id || idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.sender === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="text-xs opacity-75 mb-1">
                      {message.sender === 'user' ? 'You' : 'Support Bot'}
                    </div>
                    <div>{message.content_encrypted}</div>
                  </div>
                </motion.div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSend} className="border-t border-gray-200 p-4">
            <div className="flex space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                disabled={loading || !session}
              />
              <button
                type="submit"
                disabled={loading || !session || !input.trim()}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  )
}

export default Chat

