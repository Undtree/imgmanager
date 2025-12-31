import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 模式：'light' | 'dark' | 'auto'
  const theme = ref(localStorage.getItem('theme') || 'auto')

  // 监听系统主题变化的媒体查询对象
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

  // 核心应用逻辑
  const applyTheme = () => {
    const isDark = 
      theme.value === 'dark' || 
      (theme.value === 'auto' && mediaQuery.matches)

    // 操作 DOM Class
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // 切换主题动作
  const setTheme = (newTheme) => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    applyTheme()
  }

  // 初始化监听
  const initTheme = () => {
    applyTheme()
    // 监听系统设置变化（当处于 auto 模式时自动响应）
    mediaQuery.addEventListener('change', () => {
      if (theme.value === 'auto') applyTheme()
    })
  }

  return { theme, setTheme, initTheme }
})