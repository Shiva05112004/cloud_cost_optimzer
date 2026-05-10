import api from './axiosInstance'

export const getEC2Instances = (roleArn = null) =>
  api.get('/api/resources/ec2', {
    params: roleArn ? { role_arn: roleArn } : {},
  })

export const getCosts = (roleArn = null) =>
  api.get('/api/resources/costs', {
    params: roleArn ? { role_arn: roleArn } : {},
  })