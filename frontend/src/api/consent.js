import api from './axios'

export const consentAPI = {
  grant: (professionalId) => api.post('/consent/grant/', { professional_id: professionalId }),
  status: () => api.get('/consent/status/'),
}

