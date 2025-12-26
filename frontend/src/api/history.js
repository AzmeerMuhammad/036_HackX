import api from './axios'

export const historyAPI = {
  generate: () => api.post('/history/generate/'),
  getPDF: (snapshotId) => api.get(`/history/pdf/${snapshotId}/`, { responseType: 'blob' }),
}

