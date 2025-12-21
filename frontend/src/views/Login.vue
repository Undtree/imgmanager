<template>
  <!-- 1. 最外层容器：负责背景色和居中定位 (留出边缘空间) -->
  <div class="min-h-screen flex items-center justify-center p-4 sm:p-6 lg:p-8 bg-gray-100 dark:bg-gray-950 transition-colors duration-300">
    
    <!-- 2. 悬浮卡片容器：圆角、阴影、溢出隐藏 -->
    <div class="flex w-full max-w-[1440px] h-[85vh] min-h-[600px] bg-white dark:bg-gray-900 rounded-3xl shadow-2xl overflow-hidden ring-1 ring-gray-900/5 dark:ring-white/10">
      
      <!-- 3. 左侧：表单区域 (固定宽度) -->
      <div class="w-full lg:w-[480px] xl:w-[550px] flex flex-col justify-center px-8 md:px-12 relative z-10 bg-white dark:bg-gray-900 transition-colors duration-300">
        
        <!-- 主题切换按钮 (绝对定位在卡片左上角) -->
        <div class="absolute top-8 left-8">
           <el-dropdown @command="handleThemeCommand" trigger="click">
            <el-button circle plain size="default" class="!border-gray-200 dark:!border-gray-700">
              <el-icon class="text-base text-gray-600 dark:text-gray-300">
                <Moon v-if="themeStore.theme === 'dark'" />
                <Sunny v-else-if="themeStore.theme === 'light'" />
                <Monitor v-else />
              </el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="light"><el-icon><Sunny /></el-icon> 浅色模式</el-dropdown-item>
                <el-dropdown-item command="dark"><el-icon><Moon /></el-icon> 深色模式</el-dropdown-item>
                <el-dropdown-item command="auto"><el-icon><Monitor /></el-icon> 跟随系统</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <div class="w-full max-w-sm mx-auto">
          <!-- Logo 与 标题 -->
          <div class="mb-10 text-center lg:text-left">
            <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white mb-3 tracking-tight">
              欢迎来到 <br/>
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">ImageManager</span>
            </h1>
          </div>

          <!-- Tabs -->
          <el-tabs v-model="activeTab" class="custom-tabs mb-8">
            <el-tab-pane label="登录" name="login" />
            <el-tab-pane label="注册" name="register" />
          </el-tabs>

          <!-- 登录表单 -->
          <div v-if="activeTab === 'login'" class="animate-fade-in">
            <el-form :model="loginForm" size="large" @keyup.enter="onLogin">
              <el-form-item class="mb-5">
                <el-input 
                  v-model="loginForm.username" 
                  placeholder="用户名 / 邮箱" 
                  :prefix-icon="User"
                  class="custom-input"
                />
              </el-form-item>
              <el-form-item class="mb-2">
                <el-input 
                  v-model="loginForm.password" 
                  type="password" 
                  placeholder="密码" 
                  show-password 
                  :prefix-icon="Lock"
                  class="custom-input"
                />
              </el-form-item>
              <!-- 忘记密码链接 (装饰用) -->
              <div class="flex justify-end mb-6">
                <a href="#" class="text-xs text-blue-600 hover:text-blue-500 hover:underline">忘记密码?</a>
              </div>

              <el-button type="primary" class="w-full !h-12 !text-base !font-semibold !rounded-xl shadow-lg shadow-blue-600/20 hover:!shadow-blue-600/40 transition-all active:scale-[0.98]" @click="onLogin" :loading="loading">
                立即登录
              </el-button>
            </el-form>
          </div>

          <!-- 注册表单 -->
          <div v-else class="animate-fade-in">
            <el-form :model="regForm" size="large" @keyup.enter="onRegister">
              <el-form-item class="mb-5">
                <el-input v-model="regForm.username" placeholder="设置用户名" :prefix-icon="User" class="custom-input" />
              </el-form-item>
              <el-form-item class="mb-5">
                <el-input v-model="regForm.email" placeholder="电子邮箱" :prefix-icon="Message" class="custom-input" />
              </el-form-item>
              <el-form-item class="mb-8">
                <el-input v-model="regForm.password" type="password" placeholder="设置密码 (6位以上)" show-password :prefix-icon="Lock" class="custom-input" />
              </el-form-item>
              <el-button type="success" class="w-full !h-12 !text-base !font-semibold !rounded-xl shadow-lg shadow-green-600/20 hover:!shadow-green-600/40 transition-all active:scale-[0.98]" @click="onRegister" :loading="loading">
                创建账号
              </el-button>
            </el-form>
          </div>

          <!-- 底部版权 -->
          <div class="mt-10 text-center text-xs text-gray-400 dark:text-gray-600">
            &copy; 2025 ImageManager Project.
          </div>
        </div>
      </div>

      <!-- 4. 右侧：动态画报 (响应式隐藏：移动端不显示) -->
      <div class="hidden lg:block flex-1 relative bg-gray-100 dark:bg-gray-800 overflow-hidden">
        <!-- 轮播图层 -->
        <transition-group name="zoom-fade">
          <div 
            v-for="(img, index) in slideshowImages" 
            :key="img.id"
            v-show="currentSlide === index"
            class="absolute inset-0 w-full h-full"
          >
            <img 
              :src="img.img_url" 
              class="w-full h-full object-cover transition-transform duration-[8000ms] ease-linear scale-100 hover:scale-110" 
              style="transform: scale(1.05);"
            />
            <!-- 渐变遮罩: 从下往上变黑，保证文字可读 -->
            <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-80"></div>
            
            <!-- 图片信息浮层 -->
            <div class="absolute bottom-12 left-12 right-12 text-white animate-slide-up">
              <div class="inline-block px-3 py-1 mb-4 text-xs font-bold tracking-wider uppercase bg-white/20 backdrop-blur-md rounded-full border border-white/30">
                {{ img.category?.name || 'Featured' }}
              </div>
              <h3 class="text-4xl font-bold mb-4 leading-tight drop-shadow-lg truncate">
                {{ img.camera_model || 'Capture the Moment' }}
              </h3>
              
              <div class="flex items-center justify-between pt-6 border-t border-white/20">
                <div class="flex items-center space-x-3">
                   <el-avatar :size="40" class="border-2 border-white/50 bg-gray-500 text-white font-bold">
                     {{ img.uploader_name?.charAt(0).toUpperCase() }}
                   </el-avatar>
                   <div>
                     <div class="text-sm font-medium text-white">By {{ img.uploader_name }}</div>
                     <div class="text-xs text-gray-400">{{ formatDate(img.upload_time) }}</div>
                   </div>
                </div>
                <div v-if="img.location" class="flex items-center text-sm text-gray-300 bg-black/30 px-3 py-1.5 rounded-lg backdrop-blur-sm">
                  <el-icon class="mr-1"><Location /></el-icon> {{ img.location }}
                </div>
              </div>
            </div>
          </div>
        </transition-group>

        <!-- 空状态占位 -->
        <div v-if="slideshowImages.length === 0" class="absolute inset-0 flex items-center justify-center bg-gray-50 dark:bg-gray-800 text-gray-400">
           <div class="text-center">
             <el-icon size="64" class="mb-4 text-gray-300 dark:text-gray-600"><Picture /></el-icon>
             <p>Loading Gallery...</p>
           </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/themes'
import { login, register } from '@/api/auth'
import { getImages } from '@/api/image'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Sunny, Moon, Monitor, Location, Picture } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const activeTab = ref('login')
const loading = ref(false)
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

const loginForm = reactive({ username: '', password: '' })
const regForm = reactive({ username: '', email: '', password: '' })

const slideshowImages = ref([])
const currentSlide = ref(0)
let slideInterval = null

// 日期格式化
const formatDate = (date) => dayjs(date).format('YYYY-MM-DD')

onMounted(async () => {
  themeStore.initTheme()
  try {
    const res = await getImages({ page_size: 5, ordering: '-upload_time' })
    const list = Array.isArray(res.data) ? res.data : (res.data.results || [])
    
    // URL处理
    slideshowImages.value = list.map(img => ({
      ...img,
      img_url: img.img_url.startsWith('http') ? img.img_url : `http://127.0.0.1:8000${img.img_url}`
    }))

    if (slideshowImages.value.length > 1) {
      slideInterval = setInterval(() => {
        currentSlide.value = (currentSlide.value + 1) % slideshowImages.value.length
      }, 6000) // 6秒切换
    }
  } catch (e) {
    console.log('Error loading slideshow', e)
  }
})

onUnmounted(() => {
  if (slideInterval) clearInterval(slideInterval)
})

const onLogin = async () => {
  if (!loginForm.username || !loginForm.password) return ElMessage.warning('请输入账号密码')
  try {
    loading.value = true
    const res = await login(loginForm)
    await userStore.setToken(res.data.access)
    ElMessage.success('登录成功~')
    router.push('/')
  } catch (err) {
    ElMessage.error('登录失败: 请检查账号密码')
  } finally {
    loading.value = false
  }
}

const onRegister = async () => {
  if (!regForm.username || !regForm.email || !regForm.password) {
    return ElMessage.warning('请填写完整的注册信息')
  }

  try {
    loading.value = true
    await register(regForm)
    
    ElMessage.success({
      message: '注册成功，感谢您的支持！',
      duration: 3000
    })
    
    // 切换到登录 Tab 并自动填入用户名
    activeTab.value = 'login'
    loginForm.username = regForm.username
    // 可选：清空密码框
    regForm.password = '' 

  } catch (err) {
    if (err.response && err.response.data) {
      const errors = err.response.data
      
      // 优先级判断：先看用户名，再看邮箱，最后看密码
      if (errors.username) {
        // 后端通常返回数组，如 ["用户名已存在"]
        ElMessage.error('该用户名已被占用')
      } 
      else if (errors.email) {
        ElMessage.error('该邮箱已被注册')
      } 
      else if (errors.password) {
        // 密码错误可能包含具体原因（如"太短"、"太简单"），直接展示后端的提示
        ElMessage.error(`密码格式错误：${errors.password[0]}`)
      } 
      else if (errors.non_field_errors) {
        // 其他通用错误
        ElMessage.error(errors.non_field_errors[0])
      } 
      else {
        // 兜底错误
        ElMessage.error('注册遇到未知问题，请稍后重试')
      }
    } else {
      // 网络连不上后端的情况
      ElMessage.error('服务器连接失败，请检查网络')
    }
  } finally {
    loading.value = false
  }
}

const handleThemeCommand = (cmd) => themeStore.setTheme(cmd)
</script>

<style scoped>
/* Element UI 输入框样式覆盖，使其更现代 */
:deep(.custom-input .el-input__wrapper) {
  padding: 8px 15px;
  border-radius: 12px;
  background-color: #f3f4f6; /* gray-100 */
  box-shadow: none !important;
  transition: all 0.3s;
}
:deep(.dark .custom-input .el-input__wrapper) {
  background-color: #1f2937; /* gray-800 */
}

/* 聚焦时的效果 */
:deep(.custom-input .el-input__wrapper.is-focus) {
  background-color: #fff;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important; /* blue ring */
}
:deep(.dark .custom-input .el-input__wrapper.is-focus) {
  background-color: #111827;
}

/* Tabs 样式优化 */
:deep(.el-tabs__nav-wrap::after) {
  height: 2px;
  background-color: #f3f4f6;
}
:deep(.dark .el-tabs__nav-wrap::after) {
  background-color: #374151;
}
:deep(.el-tabs__item) {
  font-size: 16px;
  padding-bottom: 12px;
}
:deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 3px;
}

/* 动画效果 */
.zoom-fade-enter-active,
.zoom-fade-leave-active {
  transition: opacity 1.5s ease, transform 1.5s ease;
}
.zoom-fade-enter-from {
  opacity: 0;
  transform: scale(1.1);
}
.zoom-fade-leave-to {
  opacity: 0;
}

.animate-slide-up {
  animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>