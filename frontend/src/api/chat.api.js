import api from './axiosInstance'

export const askCloudOpt = (question, awsContext) =>
  api.post('/api/chat/', {
    question,
    aws_context: awsContext,
  })