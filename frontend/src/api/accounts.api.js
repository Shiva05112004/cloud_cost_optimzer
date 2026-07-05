import api from './axiosInstance'

export const connectAccount = (data) =>
  api.post('/api/accounts/connect', data)

export const listAccounts = () =>
  api.get('/api/accounts/')

export const getConnectionStatus = () =>
  api.get('/api/accounts/status')