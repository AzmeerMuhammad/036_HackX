import api from './axios'

export const professionalsAPI = {
  list: () => api.get('/professionals/list/'),
  apply: (data) => api.post('/professionals/apply/', data),
  getEscalations: () => api.get('/professionals/escalations/'),
  getEscalationDetail: (id) => api.get(`/professionals/escalations/${id}/`),
  submitVerdict: (id, data) => api.post(`/professionals/escalations/${id}/verdict/`, data),
  myEscalations: () => api.get('/professionals/escalations/mine/'),
}

