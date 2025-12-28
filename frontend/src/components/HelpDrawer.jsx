import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const HelpDrawer = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [openCategory, setOpenCategory] = useState(null)
  const [expandedAnswers, setExpandedAnswers] = useState(new Set())

  // Remember if user opened Help before
  useEffect(() => {
    const hasOpenedBefore = localStorage.getItem('safespace_help_opened')
    if (!hasOpenedBefore) {
      // Optionally auto-open on first visit (commented out for now)
      // setIsOpen(true)
      // localStorage.setItem('safespace_help_opened', 'true')
    }
  }, [])

  // Handle ESC key
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false)
      }
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [isOpen])

  const handleOpen = () => {
    setIsOpen(true)
    localStorage.setItem('safespace_help_opened', 'true')
  }

  const handleClose = () => {
    setIsOpen(false)
  }

  const toggleCategory = (category) => {
    setOpenCategory(openCategory === category ? null : category)
  }

  const toggleAnswer = (questionId) => {
    setExpandedAnswers(prev => {
      const newSet = new Set(prev)
      if (newSet.has(questionId)) {
        newSet.delete(questionId)
      } else {
        newSet.add(questionId)
      }
      return newSet
    })
  }


  const faqCategories = [
    {
      id: 'about',
      title: 'About SafeSpace',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      questions: [
        {
          q: 'What is SafeSpace?',
          a: 'SafeSpace is a secure, AI-powered mental health journaling platform designed to support your emotional wellbeing. It provides a private space to express your thoughts, gain insights through AI analysis, and connect with professional support when needed. We prioritize your privacy and safety above all else.'
        },
        {
          q: 'Is SafeSpace an AI therapist?',
          a: 'No, SafeSpace is not a replacement for therapy or professional mental health care. Our AI chatbot is designed to provide empathetic support, ask clarifying questions, and help you reflect on your feelings. It follows strict guidelines and never provides medical advice, diagnosis, or therapy recommendations. For serious concerns, we connect you with verified professionals.'
        }
      ]
    },
    {
      id: 'journaling',
      title: 'Journaling',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
      questions: [
        {
          q: 'How does journaling help me?',
          short: 'Journaling is a powerful tool for emotional processing and self-awareness.',
          full: 'Journaling is a powerful tool for emotional processing and self-awareness. By regularly writing about your thoughts and feelings, you create space to understand patterns, process difficult emotions, and track your mental health journey. Our AI analysis helps you identify themes and trends that might not be immediately obvious, giving you valuable insights into your emotional wellbeing.'
        },
        {
          q: 'Does anyone read my journal?',
          short: 'Your journal entries are private and encrypted. No one at SafeSpace reads your entries unless you explicitly grant consent.',
          full: 'Your journal entries are private and encrypted. No one at SafeSpace reads your entries unless you explicitly grant consent to share your history with a verified professional. Even then, sharing is always your choice. Our AI analysis is automated and doesn\'t involve human review unless a high-risk situation is detected, in which case we follow our safety protocols to ensure you get the support you need.'
        }
      ]
    },
    {
      id: 'chat',
      title: 'Chat & AI',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      questions: [
        {
          q: 'Can the AI give medical advice?',
          short: 'No, our AI chatbot is specifically designed to never provide medical advice, diagnosis, or treatment recommendations.',
          full: 'No, our AI chatbot is specifically designed to never provide medical advice, diagnosis, or treatment recommendations. It follows strict Standard Operating Procedures (SOPs) that prioritize your safety. The chatbot can offer empathetic support, ask clarifying questions, help you reflect, and guide you toward appropriate resources. For medical or therapeutic needs, we connect you with verified professionals.'
        },
        {
          q: 'How does the AI analysis work?',
          short: 'Our AI analyzes your journal entries to provide insights like sentiment scores, key themes, and emotional patterns.',
          full: 'Our AI analyzes your journal entries to provide insights like sentiment scores, key themes, and emotional patterns. This analysis is automated and designed to help you understand your emotional journey better. The AI identifies potential risk indicators and may suggest chatting with our support bot or connecting with a professional if concerning patterns are detected.'
        }
      ]
    },
    {
      id: 'privacy',
      title: 'Privacy & Security',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      ),
      questions: [
        {
          q: 'Is my data encrypted?',
          short: 'Yes, all your journal entries and personal data are encrypted both in transit and at rest.',
          full: 'Yes, all your journal entries and personal data are encrypted both in transit and at rest. We use industry-standard encryption protocols to ensure your information remains private and secure. Your data is stored securely and is only accessible to you, unless you explicitly choose to share it with a verified professional.'
        },
        {
          q: 'Is SafeSpace anonymous?',
          short: 'You can register with a username or alias without providing your real identity.',
          full: 'You can register with a username or alias without providing your real identity. We respect your privacy and allow you to use SafeSpace anonymously. However, if you choose to connect with a professional, you may need to share additional information as part of that process. Your anonymity is always your choice.'
        }
      ]
    },
    {
      id: 'professional',
      title: 'Professional Support',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      questions: [
        {
          q: 'How are professionals involved?',
          short: 'Verified mental health professionals can review your journal entries and AI analysis if you grant consent or if our system detects a high-risk situation.',
          full: 'Verified mental health professionals can review your journal entries and AI analysis if you grant consent or if our system detects a high-risk situation that requires professional intervention. Professionals follow ethical guidelines and provide support based on their expertise. You always have control over who sees your information.'
        },
        {
          q: 'Is SafeSpace a replacement for therapy?',
          short: 'No, SafeSpace is not a replacement for professional therapy or mental health treatment.',
          full: 'No, SafeSpace is not a replacement for professional therapy or mental health treatment. It is a supportive tool that complements professional care. If you\'re experiencing serious mental health concerns, we strongly encourage you to seek help from qualified mental health professionals. SafeSpace can help you track your journey and provide support, but it should be used alongside, not instead of, professional care.'
        }
      ]
    },
    {
      id: 'crisis',
      title: 'Crisis & Safety',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      questions: [
        {
          q: 'What happens if something serious is detected?',
          short: 'If our AI analysis detects indicators of serious risk, our system automatically escalates the situation to verified professionals for immediate review.',
          full: 'If our AI analysis detects indicators of serious risk (such as self-harm or crisis situations), our system automatically escalates the situation to verified professionals for immediate review. This is done to ensure your safety. The professional will review your information and reach out through appropriate channels to provide support. Your safety is our highest priority.'
        },
        {
          q: 'When should I seek professional help?',
          short: 'You should seek professional help if you\'re experiencing persistent feelings of hopelessness, thoughts of self-harm, or severe anxiety or depression.',
          full: 'You should seek professional help if you\'re experiencing persistent feelings of hopelessness, thoughts of self-harm, severe anxiety or depression that interferes with daily life, or any mental health concern that feels overwhelming. SafeSpace is here to support you, but professional mental health care is essential for serious conditions. Don\'t hesitate to reach out to local mental health services or emergency services if you\'re in immediate danger.'
        }
      ]
    }
  ]

  return (
    <>
      {/* Floating Help Button */}
      <motion.button
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 260, damping: 20, delay: 0.5 }}
        whileHover={{ scale: 1.08, y: -2 }}
        whileTap={{ scale: 0.92 }}
        onClick={handleOpen}
        className="fixed bottom-6 right-6 md:bottom-8 md:right-8 z-40 w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 group"
        style={{
          background: 'linear-gradient(135deg, #F15A2A 0%, #d14a1f 100%)',
          boxShadow: '0 8px 24px -4px rgba(241, 90, 42, 0.35), 0 0 0 1px rgba(255, 255, 255, 0.1) inset'
        }}
        aria-label="Open Help & FAQ"
      >
        <motion.div
          className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          style={{
            background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.05) 100%)',
            boxShadow: '0 12px 32px -6px rgba(241, 90, 42, 0.45)'
          }}
        />
        <motion.svg
          className="w-6 h-6 text-white relative z-10"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          whileHover={{ rotate: [0, -10, 10, -10, 0] }}
          transition={{ duration: 0.5 }}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2.5}
            d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </motion.svg>
      </motion.button>

      {/* Backdrop */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              onClick={handleClose}
              className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
              style={{ backdropFilter: 'blur(4px)' }}
            />

            {/* Mobile: Slide from bottom */}
            <motion.div
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="md:hidden fixed bottom-0 left-0 right-0 h-[85vh] z-50 bg-white rounded-t-3xl overflow-hidden"
              style={{
                background: 'linear-gradient(to bottom, #ffffff 0%, #faf9f7 100%)',
                boxShadow: '0 -8px 32px -4px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.04)'
              }}
            >
              <div className="h-full overflow-y-auto">
                <HelpContent
                  onClose={handleClose}
                  faqCategories={faqCategories}
                  openCategory={openCategory}
                  toggleCategory={toggleCategory}
                  expandedAnswers={expandedAnswers}
                  toggleAnswer={toggleAnswer}
                />
              </div>
            </motion.div>

            {/* Desktop: Slide from right */}
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="hidden md:block fixed top-0 right-0 h-full w-[480px] lg:w-[520px] z-50 bg-white overflow-hidden"
              style={{
                background: 'linear-gradient(to bottom, #ffffff 0%, #faf9f7 100%)',
                boxShadow: '-8px 0 32px -4px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.04)'
              }}
            >
              <div className="h-full overflow-y-auto">
                <HelpContent
                  onClose={handleClose}
                  faqCategories={faqCategories}
                  openCategory={openCategory}
                  toggleCategory={toggleCategory}
                  expandedAnswers={expandedAnswers}
                  toggleAnswer={toggleAnswer}
                />
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}

const HelpContent = ({ onClose, faqCategories, openCategory, toggleCategory, expandedAnswers, toggleAnswer }) => {
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white/98 backdrop-blur-md border-b border-gray-200/60 px-6 py-6 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-2xl font-bold mb-1" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
              Help & Support
            </h2>
            <div className="h-0.5 w-12 bg-gradient-to-r from-primary-500 to-primary-400 rounded-full" />
          </div>
          <motion.button
            whileHover={{ scale: 1.05, rotate: 90 }}
            whileTap={{ scale: 0.95 }}
            onClick={onClose}
            className="w-9 h-9 rounded-xl flex items-center justify-center hover:bg-gray-100 transition-all focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            aria-label="Close Help"
          >
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </motion.button>
        </div>
        <p className="text-sm leading-relaxed" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F', opacity: 0.75 }}>
          Need Help? You're in a Safe Space.
        </p>
        <p className="text-xs mt-1.5" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F', opacity: 0.6 }}>
          We're here to guide and support you every step of the way.
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {/* How SafeSpace Helps */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="relative overflow-hidden rounded-2xl p-6 border border-gray-200/60 bg-gradient-to-br from-white to-gray-50/50"
          style={{
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)'
          }}
        >
          <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-primary-500 via-primary-400 to-primary-500" />
          <h3 className="font-semibold mb-4 text-lg relative z-10" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
            How SafeSpace Helps
          </h3>
          <div className="grid grid-cols-2 gap-4 relative z-10">
            {[
              {
                icon: (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                ),
                text: 'Journal your thoughts'
              },
              {
                icon: (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                ),
                text: 'AI insights & patterns'
              },
              {
                icon: (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                ),
                text: 'Empathetic chat support'
              },
              {
                icon: (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ),
                text: 'Professional connection'
              }
            ].map((step, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + idx * 0.08 }}
                className="flex flex-col items-center gap-2 p-3 rounded-xl hover:bg-white/60 transition-colors"
              >
                <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-primary-50 text-primary-600">
                  {step.icon}
                </div>
                <span className="text-xs text-center font-medium leading-tight" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F', opacity: 0.8 }}>
                  {step.text}
                </span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* FAQ Accordion */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold mb-4" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
            Frequently Asked Questions
          </h3>
          {faqCategories.map((category, catIdx) => (
            <motion.div
              key={category.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + catIdx * 0.05 }}
              className="border border-gray-200/60 rounded-xl overflow-hidden bg-white shadow-sm hover:shadow-md transition-shadow duration-300"
            >
              <motion.button
                onClick={() => toggleCategory(category.id)}
                className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-gray-50/80 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-inset group"
                aria-expanded={openCategory === category.id}
              >
                <div className="flex items-center gap-3">
                  <div className="text-primary-500 group-hover:text-primary-600 transition-colors">{category.icon}</div>
                  <span className="font-semibold text-sm group-hover:text-primary-600 transition-colors" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                    {category.title}
                  </span>
                </div>
                <motion.svg
                  className="w-5 h-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  animate={{ rotate: openCategory === category.id ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </motion.svg>
              </motion.button>

              <AnimatePresence>
                {openCategory === category.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                    className="overflow-hidden"
                  >
                    <div className="px-5 pb-4 space-y-4 bg-gradient-to-b from-gray-50/80 to-white">
                      {category.questions.map((faq, faqIdx) => (
                        <motion.div
                          key={faqIdx}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: faqIdx * 0.1 }}
                          className="pt-4 border-t border-gray-200 first:border-t-0 first:pt-0"
                        >
                          <h4 className="font-semibold text-sm mb-2" style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}>
                            {faq.q}
                          </h4>
                          <div className="space-y-2">
                            {(() => {
                              const questionId = `${category.id}-${faqIdx}`
                              const isExpanded = expandedAnswers.has(questionId)
                              const hasMore = faq.short && faq.full && faq.short !== faq.full
                              const displayText = isExpanded ? faq.full : (faq.short || faq.full || faq.a || '')
                              
                              return (
                                <>
                                  <AnimatePresence mode="wait">
                                    <motion.p
                                      key={isExpanded ? 'full' : 'short'}
                                      initial={{ opacity: 0 }}
                                      animate={{ opacity: 1 }}
                                      exit={{ opacity: 0 }}
                                      transition={{ duration: 0.2 }}
                                      className="text-sm leading-relaxed" 
                                      style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F', opacity: 0.7 }}
                                    >
                                      {displayText}
                                    </motion.p>
                                  </AnimatePresence>
                                  {hasMore && (
                                    <motion.button
                                      onClick={() => toggleAnswer(questionId)}
                                      className="flex items-center gap-1.5 text-xs font-medium text-primary-600 hover:text-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1 rounded px-2 py-1 -ml-2"
                                      whileHover={{ scale: 1.02 }}
                                      whileTap={{ scale: 0.98 }}
                                    >
                                      <span>{isExpanded ? 'Show less' : 'Read more'}</span>
                                      <motion.svg
                                        className="w-3.5 h-3.5"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                        animate={{ rotate: isExpanded ? 180 : 0 }}
                                        transition={{ duration: 0.2 }}
                                      >
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
                                      </motion.svg>
                                    </motion.button>
                                  )}
                                </>
                              )
                            })()}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>

        {/* Emergency Notice */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-gradient-to-br from-amber-50/80 to-amber-100/40 border border-amber-200/60 rounded-2xl p-5 shadow-sm"
        >
          <div className="flex items-start gap-3">
            <svg className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <h4 className="font-semibold text-sm mb-1" style={{ fontFamily: "'Inter', sans-serif", color: '#92400E' }}>
                Emergency & Safety
              </h4>
              <p className="text-sm leading-relaxed" style={{ fontFamily: "'Inter', sans-serif", color: '#92400E', opacity: 0.9 }}>
                If you're in immediate danger or experiencing a mental health crisis, please contact your local emergency services immediately. In Pakistan, you can reach emergency services at 15 or 1122. SafeSpace is here to support you, but for immediate emergencies, professional emergency services are the right resource.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Footer Spacing */}
        <div className="h-6" />
      </div>
    </div>
  )
}

export default HelpDrawer

