import api from './axios'

export const chatAPI = {
  getOrCreateSession: () => api.post('/chat/sessions/'),
  getSessions: () => api.get('/chat/sessions/'),
  sendMessage: (sessionId, content) => api.post(`/chat/sessions/${sessionId}/message/`, { content }),
  getMessages: (sessionId) => api.get(`/chat/sessions/${sessionId}/messages/`),
}

