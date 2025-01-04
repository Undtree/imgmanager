<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20 transition-colors duration-300">
    <NavBar />
    
    <div class="container mx-auto px-4 py-8 max-w-4xl">
      <!-- 个人信息卡片 -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
        
        <!-- 左侧：头像 -->
        <div class="shrink-0">
          <el-avatar :size="100" class="bg-gradient-to-br from-blue-500 to-indigo-600 text-white text-4xl font-bold shadow-lg">
            {{ userInfo.username?.charAt(0).toUpperCase() }}
          </el-avatar>
        </div>

        <!-- 右侧：详细信息 -->
        <div class="flex-1 text-center md:text-left space-y-4 w-full">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">{{ userInfo.username }}</h1>
            <p class="text-gray-500 dark:text-gray-400 flex items-center justify-center md:justify-start">
              <el-icon class="mr-1"><Message /></el-icon> {{ userInfo.email }}
            </p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
            <div class="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-xl">
              <div class="text-xs text-gray-500 dark:text-gray-400 uppercase font-bold">用户 ID</div>
              <div class="text-lg font-mono text-gray-800 dark:text-gray-200">#{{ userInfo.id }}</div>
            </div>
            <div class="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-xl">
              <div class="text-xs text-gray-500 dark:text-gray-400 uppercase font-bold">加入时间</div>
              <div class="text-lg text-gray-800 dark:text-gray-200">{{ formatDate(userInfo.date_joined) }}</div>
            </div>
          </div>
          
          <div class="pt-4 flex justify-center md:justify-start gap-3">
             <el-button @click="$router.push('/')">返回首页</el-button>
             <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NavBar from '@/components/NavBar.vue'
import { Message } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

// 从 Store 中获取完整用户信息
const userInfo = computed(() => userStore.userInfo || { username: userStore.username })

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY年MM月DD日') : '未知'
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>