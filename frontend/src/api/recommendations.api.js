import api from './axiosInstance'

export const getRecommendations = (roleArn = null) =>
  api.get('/api/recommendations/', {
    params: roleArn ? { role_arn: roleArn } : {},
  })