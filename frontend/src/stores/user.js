import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

export const useUserStore = defineStore('user', () => {
  // === 1. 状态 State ===
  const token = ref(localStorage.getItem('access_token') || '')
  // 尝试从本地读取上次的用户信息，避免刷新页面时用户名闪烁
  const userInfo = ref(JSON.parse(localStorage.getItem('user_info') || 'null'))

  // === 2. 计算属性 Computed ===
  // 这样 NavBar 依然可以通过 userStore.username 拿到名字
  const username = computed(() => {
    return userInfo.value?.username || userInfo.value?.email || '用户'
  })

  // === 3. 动作 Actions ===

  async function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('access_token', newToken)
    
    // 拿到 Token 后，立刻自动去后端拉取最新的用户信息
    await fetchUserInfo()
  }

  // 调用你的 /auth/me 接口
  async function fetchUserInfo() {
    if (!token.value) return
    try {
      const res = await request.get('/auth/me/') 
      userInfo.value = res.data
      // 持久化用户信息
      localStorage.setItem('user_info', JSON.stringify(res.data))
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取失败（比如 token 过期），考虑是否要自动登出
      // logout() 
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
  }

  return { 
    token, 
    userInfo, 
    username, 
    setToken, 
    fetchUserInfo, 
    logout 
  }
})