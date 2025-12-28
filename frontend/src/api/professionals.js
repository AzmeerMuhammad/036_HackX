import api from './axios'

export const professionalsAPI = {
  list: () => api.get('/professionals/list/'),
  apply: (data) => api.post('/professionals/apply/', data),
  getProfile: () => api.get('/professionals/profile/'),
  updateProfile: (data) => api.put('/professionals/profile/', data),
  verify: (formData) => api.post('/professionals/verify/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  getPatientSummary: (patientId) => api.get(`/professionals/patients/${patientId}/summary/`),
  getPatients: () => api.get('/professionals/patients/'),
  getEscalations: () => api.get('/professionals/escalations/'),
  getEscalationDetail: (id) => api.get(`/professionals/escalations/${id}/`),
  submitVerdict: (id, data) => api.post(`/professionals/escalations/${id}/verdict/`, data),
  myEscalations: () => api.get('/professionals/escalations/mine/'),
  // SOP Management
  getSOPs: () => api.get('/professionals/sops/'),
  createSOP: (data) => api.post('/professionals/sops/', data),
  updateSOP: (id, data) => api.put(`/professionals/sops/${id}/`, data),
  deleteSOP: (id) => api.delete(`/professionals/sops/${id}/`),
}

