import axios from 'axios'
import { useUserStore } from '@/stores/user'
import router from '@/router' // 引入路由，以便跳转
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api', // Django 地址
  timeout: 10000 // 请求超时时间
})

// === 请求拦截器 ===
service.interceptors.request.use(
  config => {
    // 每次请求前，从 Pinia (或 localStorage) 获取最新 Token
    // 注意：这里不能在顶层获取 store，必须在函数内部
    const userStore = useUserStore()
    const token = userStore.token
    
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token
    }
    return config
  },
  error => Promise.reject(error)
)

// === 响应拦截器 ===
service.interceptors.response.use(
  response => {
    return response
  },
  error => {
    const userStore = useUserStore()
    
    // 如果后端返回 401 (未授权/Token过期)
    if (error.response && error.response.status === 401) {
      
      // 1. 如果当前已经是在登录页，就不要一直弹窗了
      if (router.currentRoute.value.path !== '/login') {
        ElMessage.error('登录已过期，请重新登录')
        
        // 2. 执行登出清理 (清除 localStorage)
        userStore.logout()
        
        // 3. 强制跳转回登录页
        router.push('/login')
      }
    } else {
      // 处理其他错误 (403, 500 等)
      ElMessage.error(error.response?.data?.detail || '请求失败')
    }
    
    return Promise.reject(error)
  }
)

export default service
