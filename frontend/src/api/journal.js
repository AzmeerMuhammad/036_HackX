import api from './axios'

export const journalAPI = {
  create: (data) => {
    const formData = new FormData()
    formData.append('text', data.text)
    if (data.checkin_mood) formData.append('checkin_mood', data.checkin_mood)
    if (data.checkin_intensity !== undefined) formData.append('checkin_intensity', data.checkin_intensity)
    if (data.voice_file) formData.append('voice_file', data.voice_file)
    return api.post('/journal/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  list: () => api.get('/journal/'),
  get: (id) => api.get(`/journal/${id}/`),
  delete: (id) => api.delete(`/journal/${id}/`),
}

