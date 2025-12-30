import request from '@/utils/request'

export function login(data) {
  return request.post('/auth/login/', data) // 获取 JWT
}

export function register(data) {
  return request.post('/auth/register/', data)
}