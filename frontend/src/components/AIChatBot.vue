<template>
  <div class="ai-chat-wrapper z-50">
    <!-- 1. 悬浮唤醒按钮 (Floating Action Button) -->
    <div 
      v-if="!isOpen" 
      class="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 rounded-full shadow-xl flex items-center justify-center cursor-pointer hover:bg-blue-700 transition-all hover:scale-110 z-50"
      @click="toggleChat"
    >
      <el-icon class="text-white text-2xl"><ChatDotRound /></el-icon>
    </div>

    <!-- 2. 对话框主体 -->
    <transition name="el-zoom-in-bottom">
      <div v-if="isOpen" class="fixed bottom-24 right-6 w-[380px] h-[600px] bg-white dark:bg-gray-800 rounded-2xl shadow-2xl flex flex-col border border-gray-200 dark:border-gray-700 overflow-hidden z-50">
        
        <!-- 顶部标题 -->
        <div class="h-14 bg-blue-600 flex items-center justify-between px-4 shrink-0">
          <span class="text-white font-bold flex items-center">
            <el-icon class="mr-2"><MagicStick /></el-icon> AI 智搜助手
          </span>
          <el-icon class="text-white cursor-pointer hover:text-gray-200" @click="toggleChat"><Close /></el-icon>
        </div>

        <!-- 消息列表区 -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900" ref="msgContainer">
          <!-- 欢迎语 -->
          <div class="flex justify-start">
            <div class="bg-white dark:bg-gray-700 p-3 rounded-lg rounded-tl-none shadow-sm max-w-[85%] text-sm text-gray-700 dark:text-gray-200">
              👋 你好！我是你的图片助手。你可以试着问我：<br>
              “去年在海边拍的照片”<br>
              “红色的花朵”<br>
              “截屏图片”
            </div>
          </div>

          <!-- 消息循环 -->
          <div v-for="(msg, index) in messages" :key="index" :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
            <!-- 用户消息 -->
            <div v-if="msg.role === 'user'" class="bg-blue-600 text-white p-3 rounded-lg rounded-tr-none shadow-sm max-w-[85%] text-sm">
              {{ msg.content }}
            </div>

            <!-- AI 消息 (普通文本) -->
            <div v-else-if="msg.type === 'text'" class="bg-white dark:bg-gray-700 p-3 rounded-lg rounded-tl-none shadow-sm max-w-[85%] text-sm text-gray-700 dark:text-gray-200">
              {{ msg.content }}
            </div>

            <!-- AI 消息 (图片结果卡片) -->
            <div v-else-if="msg.type === 'results'" class="w-full">
              <div class="bg-white dark:bg-gray-700 p-2 rounded-lg rounded-tl-none shadow-sm text-sm">
                <p class="mb-2 text-gray-500">找到 {{ msg.data.length }} 张相关图片：</p>
                <div class="grid grid-cols-2 gap-2">
                  <div 
                    v-for="img in msg.data" 
                    :key="img.id" 
                    class="relative aspect-square cursor-pointer group overflow-hidden rounded-md"
                    @click="goToDetail(img.id)"
                  >
                    <img :src="img.url" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"/>
                    <div class="absolute inset-0 bg-black/20 group-hover:bg-black/0 transition-colors"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Loading 状态 -->
          <div v-if="loading" class="flex justify-start">
             <div class="bg-gray-200 dark:bg-gray-700 px-4 py-2 rounded-full text-xs animate-pulse text-gray-500">
               查找中...
             </div>
          </div>
        </div>

        <!-- 底部输入框 -->
        <div class="h-16 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex items-center px-3 shrink-0">
          <input 
            v-model="inputContent"
            @keydown.enter="sendMessage"
            type="text" 
            placeholder="输入描述..." 
            class="flex-1 bg-gray-100 dark:bg-gray-900 border-none outline-none rounded-full px-4 py-2 text-sm text-gray-700 dark:text-white"
          />
          <el-button circle type="primary" class="ml-2" @click="sendMessage" :disabled="!inputContent.trim() || loading">
            <el-icon><Position /></el-icon>
          </el-button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ChatDotRound, Close, Position, MagicStick } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useRouter } from 'vue-router'

const router = useRouter()
const isOpen = ref(false)
const inputContent = ref('')
const loading = ref(false)
const msgContainer = ref(null)

const messages = ref([])

const toggleChat = () => {
  isOpen.value = !isOpen.value
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (msgContainer.value) {
      msgContainer.value.scrollTop = msgContainer.value.scrollHeight
    }
  })
}

const goToDetail = (id) => {
  // 假设你有详情页路由
  router.push(`/detail/${id}`)
}

const sendMessage = async () => {
  const text = inputContent.value.trim()
  if (!text) return

  // 1. 添加用户消息
  messages.value.push({ role: 'user', content: text })
  inputContent.value = ''
  loading.value = true
  scrollToBottom()

  try {
    // 2. 调用后端的 MCP 接口
    // 注意：这里调用的是之前写的 /api/mcp/search
    const res = await request.get('/mcp/search/', { params: { q: text } })
    const results = res.data.results || []

    loading.value = false

    if (results.length > 0) {
      messages.value.push({ 
        role: 'ai', 
        type: 'text', 
        content: `好的，根据"${text}"，我找到了以下内容：` 
      })
      messages.value.push({ 
        role: 'ai', 
        type: 'results', 
        data: results // 包含 url, id, description
      })
    } else {
      messages.value.push({ 
        role: 'ai', 
        type: 'text', 
        content: '抱歉，这里似乎暂时没有相关的图片。你可以换个关键词试试，比如“风景”或“猫”。' 
      })
    }

  } catch (e) {
    loading.value = false
    messages.value.push({ role: 'ai', type: 'text', content: '网络开小差了，请稍后再试。' })
  }
  
  scrollToBottom()
}
</script>

<style scoped>
/* 隐藏滚动条但保留滚动功能 */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 2px;
}
</style>