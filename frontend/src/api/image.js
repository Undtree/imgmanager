import request from '@/utils/request'

export function getImages(params) {
  return request.get('/images/', { params })
}

export function getImageDetail(id) {
  return request.get(`/images/${id}/`)
}

export function getCategories() {
  return request.get('/categories/')
}

export function createCategory(name) {
  return request.post('/categories/', { name })
}

export function uploadImage(formData) {
  return request.post('/images/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 用于更新图片（如裁剪后覆盖）
export function updateImage(id, formData) {
  return request.patch(`/images/${id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function deleteImage(id) {
  return request.delete(`/images/${id}/`)
}