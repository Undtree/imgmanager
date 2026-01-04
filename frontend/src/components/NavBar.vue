<template>
  <header class="sticky top-0 z-50 bg-white border-b shadow-sm transition-colors duration-300 dark:bg-gray-800 dark:border-gray-700">
    <div class="container mx-auto px-4 h-16 flex items-center justify-between">
      <!-- Logo -->
      <router-link to="/" class="text-xl font-bold text-blue-600">
        ImageManager
      </router-link>

      <!-- PC端 搜索 & 菜单 -->
      <div class="hidden md:flex items-center space-x-4 flex-1 justify-end">
        <!-- 主题切换下拉菜单 -->
        <el-dropdown @command="handleThemeCommand">
          <el-button circle plain>
            <el-icon>
              <!-- 根据当前状态显示不同图标 -->
              <Moon v-if="themeStore.theme === 'dark'" />
              <Sunny v-else-if="themeStore.theme === 'light'" />
              <Monitor v-else />
            </el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="light" :class="{ 'text-blue-500': themeStore.theme === 'light' }">
                <el-icon><Sunny /></el-icon> 日间模式
              </el-dropdown-item>
              <el-dropdown-item command="dark" :class="{ 'text-blue-500': themeStore.theme === 'dark' }">
                <el-icon><Moon /></el-icon> 夜间模式
              </el-dropdown-item>
              <el-dropdown-item command="auto" :class="{ 'text-blue-500': themeStore.theme === 'auto' }">
                <el-icon><Monitor /></el-icon> 跟随系统
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索标签、地点..." 
          class="w-64"
          @keyup.enter="handleSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        
        <template v-if="userStore.token">
          <!-- 1. 优化上传按钮：圆角 + 图标 -->
          <el-button type="primary" icon="Plus" @click="$router.push('/upload')">上传图片</el-button>

          <!-- 2. 优化用户信息：胶囊式布局 -->
          <el-dropdown trigger="click" class="ml-4">
            <!-- 外层容器：圆角边框 + 悬停变色 -->
            <div class="flex items-center gap-2 cursor-pointer pl-1 pr-3 py-1 rounded-full border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600 transition-all duration-300 group">
              
              <!-- 头像：使用首字母 + 渐变背景 -->
              <el-avatar 
                :size="32" 
                class="bg-gradient-to-br from-blue-500 to-indigo-600 text-white text-sm font-bold shadow-sm group-hover:scale-105 transition-transform"
              >
                {{ userStore.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              
              <!-- 用户名：加粗 -->
              <span class="text-sm font-medium text-gray-700 dark:text-gray-200 max-w-[100px] truncate">
                {{ userStore.username }}
              </span>
              
              <!-- 下拉箭头：颜色变淡 -->
              <el-icon class="text-gray-400 group-hover:text-gray-600 transition-colors"><ArrowDown /></el-icon>
            </div>

            <!-- 下拉菜单内容 -->
            <template #dropdown>
              <el-dropdown-menu class="!p-2 min-w-[160px]">
                <!-- 头部欢迎语 (可选) -->
                <div class="px-4 py-2 text-xs text-gray-400 border-b border-gray-100 dark:border-gray-700 mb-1">
                  已登录为 {{ userStore.username }}
                </div>
                
                <el-dropdown-item icon="User" @click="$router.push('/profile')">
                  个人中心
                </el-dropdown-item>
                
                <!-- 分割线 -->
                <el-dropdown-item divided icon="SwitchButton" @click="handleLogout" class="!text-red-500 hover:!bg-red-50 dark:hover:!bg-red-900/20">
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <router-link to="/login" class="text-blue-600">登录 / 注册</router-link>
        </template>
      </div>

      <!-- 移动端汉堡菜单 -->
      <button class="md:hidden text-gray-600 dark:text-gray-300 focus:outline-none p-2" @click="mobileMenuOpen = !mobileMenuOpen">
        <el-icon size="24">
          <component :is="mobileMenuOpen ? Close : Menu" />
        </el-icon>
      </button>
    </div>

    <!-- 移动端下拉菜单 -->
    <div v-show="mobileMenuOpen" class="md:hidden border-t dark:border-gray-800 bg-white dark:bg-[#1f1f1f] shadow-xl absolute w-full left-0 z-40 transition-all duration-300 origin-top">
      <div class="p-4 space-y-5">
        
        <!-- 移动端搜索 -->
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索标签、描述..." 
          size="large"
          class="mobile-search"
          @keyup.enter="handleSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>

        <template v-if="userStore.token">
          <!-- 用户信息卡片 -->
          <div class="flex items-center justify-between bg-gray-50 dark:bg-[#2a2a2a] p-3 rounded-lg border border-gray-100 dark:border-gray-700">
            <div class="flex items-center space-x-3">
              <el-avatar :size="40" class="bg-blue-500 text-white font-bold">
                {{ userStore.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <div>
                <div class="text-sm font-bold text-gray-800 dark:text-white">{{ userStore.username }}</div>
                <div class="text-xs text-gray-500 dark:text-gray-400">已登录</div>
              </div>
            </div>
            <!-- 移动端主题切换 -->
             <el-button circle size="small" @click="toggleTheme" class="!bg-transparent !border-gray-300 dark:!border-gray-600">
                <el-icon class="text-gray-600 dark:text-gray-300">
                  <Moon v-if="themeStore.theme === 'dark'" />
                  <Sunny v-else />
                </el-icon>
             </el-button>
          </div>

          <!-- 操作按钮组 -->
          <div class="grid grid-cols-2 gap-3">
            <el-button type="primary" size="large" icon="Plus" class="!w-full" @click="$router.push('/upload')">
              上传图片
            </el-button>
            <el-button size="large" icon="SwitchButton" plain type="danger" class="!w-full" @click="handleLogout">
              退出
            </el-button>
          </div>
        </template>

        <template v-else>
           <el-button type="primary" class="w-full" size="large" @click="$router.push('/login')">立即登录</el-button>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/themes'
import { Search, ArrowDown, Menu, Sunny, Moon, Monitor, SwitchButton, Plus, User } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()
const searchKeyword = ref('')
const mobileMenuOpen = ref(false)

// 处理下拉菜单点击
const handleThemeCommand = (command) => {
  themeStore.setTheme(command)
}

const toggleTheme = () => {
  const next = themeStore.theme === 'dark' ? 'light' : 'dark'
  themeStore.setTheme(next)
}

const handleSearch = () => {
  router.push({ path: '/', query: { q: searchKeyword.value } })
  mobileMenuOpen.value = false
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* 搜索框深色模式适配 */
.search-input :deep(.el-input__wrapper) {
  background-color: #f3f4f6;
  box-shadow: none;
}
.dark .search-input :deep(.el-input__wrapper) {
  background-color: #2a2a2a;
}
.dark .search-input :deep(.el-input__inner) {
  color: white;
}

/* 移动端搜索框样式 */
.mobile-search :deep(.el-input__wrapper) {
  background-color: #f9fafb;
  border-radius: 8px;
  box-shadow: none;
  border: 1px solid #e5e7eb;
}
.dark .mobile-search :deep(.el-input__wrapper) {
  background-color: #2a2a2a;
  border-color: #444;
}
.dark .mobile-search :deep(.el-input__inner) {
  color: white;
}
</style>