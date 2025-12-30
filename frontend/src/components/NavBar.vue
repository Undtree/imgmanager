<template>
  <header class="sticky top-0 z-50 bg-white border-b shadow-sm">
    <div class="container mx-auto px-4 h-16 flex items-center justify-between">
      <!-- Logo -->
      <router-link to="/" class="text-xl font-bold text-blue-600">
        ImageManager
      </router-link>

      <!-- PC端 搜索 & 菜单 -->
      <div class="hidden md:flex items-center space-x-4 flex-1 justify-end">
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索标签、地点..." 
          class="w-64"
          @keyup.enter="handleSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        
        <template v-if="userStore.token">
          <el-button type="primary" @click="$router.push('/upload')">上传图片</el-button>
          <el-dropdown>
            <span class="cursor-pointer text-gray-700 ml-2">
              {{ userStore.username }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <router-link to="/login" class="text-blue-600">登录 / 注册</router-link>
        </template>
      </div>

      <!-- 移动端汉堡菜单 -->
      <button class="md:hidden" @click="mobileMenuOpen = !mobileMenuOpen">
        <el-icon size="24"><Menu /></el-icon>
      </button>
    </div>

    <!-- 移动端下拉菜单 -->
    <div v-if="mobileMenuOpen" class="md:hidden bg-white border-t p-4 space-y-3">
      <el-input v-model="searchKeyword" placeholder="搜索..." @keyup.enter="handleSearch" />
      <div v-if="userStore.token" class="flex flex-col space-y-2">
        <div class="font-bold">{{ userStore.username }}</div>
        <el-button type="primary" class="w-full" @click="$router.push('/upload')">上传</el-button>
        <el-button type="danger" plain class="w-full" @click="handleLogout">退出</el-button>
      </div>
      <div v-else>
        <router-link to="/login" class="block py-2 text-center bg-gray-100 rounded">登录</router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Search, ArrowDown, Menu } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const searchKeyword = ref('')
const mobileMenuOpen = ref(false)

const handleSearch = () => {
  router.push({ path: '/', query: { search: searchKeyword.value } })
  mobileMenuOpen.value = false
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>