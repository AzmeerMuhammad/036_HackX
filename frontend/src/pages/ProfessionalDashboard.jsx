import { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import { professionalsAPI } from '../api/professionals'
import { motion } from 'framer-motion'

const ProfessionalDashboard = () => {
  const [escalations, setEscalations] = useState([])
  const [selectedTicket, setSelectedTicket] = useState(null)
  const [verdict, setVerdict] = useState('')
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadEscalations()
  }, [])

  const loadEscalations = async () => {
    try {
      const response = await professionalsAPI.getEscalations()
      setEscalations(response.data)
    } catch (err) {
      if (err.response?.status === 403) {
        alert('You are not a verified professional')
      }
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
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Professional Dashboard</h1>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Pending Escalations</h2>
            {escalations.length === 0 ? (
              <div className="bg-white rounded-xl shadow-md p-8 text-center">
                <p className="text-gray-600">No pending escalations.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {escalations.map((ticket) => (
                  <motion.div
                    key={ticket.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-xl shadow-md p-6 cursor-pointer hover:shadow-lg transition-shadow"
                    onClick={() => loadTicketDetail(ticket.id)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="font-semibold text-gray-900">Ticket #{ticket.id}</div>
                        <div className="text-sm text-gray-600">
                          User: {ticket.user.display_name}
                        </div>
                      </div>
                      <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">
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

          <div>
            {selectedTicket ? (
              <div className="bg-white rounded-xl shadow-md p-6">
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
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Verdict *
                      </label>
                      <select
                        value={verdict}
                        onChange={(e) => setVerdict(e.target.value)}
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                      >
                        <option value="">Select verdict</option>
                        <option value="consult_required">Consult Required</option>
                        <option value="monitor">Monitor</option>
                        <option value="no_action">No Action</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Professional Notes
                      </label>
                      <textarea
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        rows={4}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                        placeholder="Add your notes..."
                      />
                    </div>
                    <div className="flex space-x-4">
                      <button
                        type="submit"
                        disabled={submitting}
                        className="flex-1 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
                      >
                        {submitting ? 'Submitting...' : 'Submit Verdict'}
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedTicket(null)
                          setVerdict('')
                          setNotes('')
                        }}
                        className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
                      >
                        Close
                      </button>
                    </div>
                  </form>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-md p-8 text-center">
                <p className="text-gray-600">Select a ticket to review</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default ProfessionalDashboard

