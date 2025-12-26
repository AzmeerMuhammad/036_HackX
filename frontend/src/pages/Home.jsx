import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { motion } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'

const Home = () => {
  const { user } = useAuth()

  return (
    <Layout>
      <div className="text-center">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold text-gray-900 mb-4"
        >
          Welcome to SafeSpace
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-lg text-gray-600 mb-8"
        >
          Your secure AI-powered mental health journaling platform
        </motion.p>

        <div className="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto mt-12">
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link
              to="/journal/new"
              className="block p-8 bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow border-2 border-transparent hover:border-primary-500"
            >
              <div className="text-4xl mb-4">📔</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">Journal</h2>
              <p className="text-gray-600">Record your thoughts and feelings</p>
            </Link>
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link
              to="/chat"
              className="block p-8 bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow border-2 border-transparent hover:border-primary-500"
            >
              <div className="text-4xl mb-4">💬</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">Chat</h2>
              <p className="text-gray-600">Talk to our supportive chatbot</p>
            </Link>
          </motion.div>
        </div>

        <div className="mt-8 flex justify-center space-x-4 flex-wrap gap-2">
          <Link
            to="/journal/history"
            className="px-6 py-2 bg-white text-primary-600 rounded-lg hover:bg-primary-50 transition-colors shadow-sm"
          >
            Journal History
          </Link>
          <Link
            to="/insights"
            className="px-6 py-2 bg-white text-primary-600 rounded-lg hover:bg-primary-50 transition-colors shadow-sm"
          >
            7-Day Insights
          </Link>
          <Link
            to="/professionals"
            className="px-6 py-2 bg-white text-primary-600 rounded-lg hover:bg-primary-50 transition-colors shadow-sm"
          >
            Professionals
          </Link>
          <Link
            to="/history/share"
            className="px-6 py-2 bg-white text-primary-600 rounded-lg hover:bg-primary-50 transition-colors shadow-sm"
          >
            Share History
          </Link>
        </div>
      </div>
    </Layout>
  )
}

export default Home

