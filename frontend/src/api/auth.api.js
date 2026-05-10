import api from './axiosInstance'

export const registerUser = (data) =>
  api.post('/api/auth/register', data)

export const loginUser = (email, password) => {
  const form = new FormData()
  form.append('username', email)
  form.append('password', password)
  return api.post('/api/auth/login', form)
}

export const getMe = () =>
  api.get('/api/auth/me')