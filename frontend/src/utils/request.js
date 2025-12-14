import axios from 'axios'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api', // Django 地址
  timeout: 5000
})

// 请求拦截器：携带 Token
service.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers['Authorization'] = 'Bearer ' + token
  }
  return config
}, error => Promise.reject(error))

export default service