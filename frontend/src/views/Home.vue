<template>
  <div class="min-h-screen pb-20">
    <NavBar />
    
    <div class="container mx-auto px-2 md:px-6 py-4 md:py-8 max-w-[1600px]">
      <!-- 顶部切换 -->
      <div class="flex justify-center mb-6">
        <el-radio-group v-model="activeTab" size="large" @change="handleTabChange">
          <el-radio-button label="my">我的照片</el-radio-button>
          <el-radio-button label="explore">漫游广场</el-radio-button>
        </el-radio-group>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="py-20 flex justify-center">
        <el-skeleton animated :count="3" class="w-full grid grid-cols-3 gap-4" />
      </div>

      <!-- 空状态 -->
      <div v-else-if="images.length === 0" class="text-center py-20">
        <el-empty description="暂无图片，快去上传一张吧！">
          <el-button type="primary" @click="$router.push('/upload')">立即上传</el-button>
        </el-empty>
      </div>

      <!-- 使用 Waterfall 组件 -->
      <Waterfall v-else :images="images" />
    </div>

    <!-- 移动端 FAB 上传按钮 -->
    <div class="fixed left-6 bottom-8 md:hidden z-40">
      <button 
        @click="router.push('/upload')"
        class="w-14 h-14 bg-blue-600 text-white rounded-full shadow-xl flex items-center justify-center hover:bg-blue-700 active:scale-90 transition transform duration-200">
        <el-icon size="24"><Plus /></el-icon>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import Waterfall from '@/components/Waterfall.vue'
import { getImages } from '@/api/image'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const activeTab = ref('my') 
const images = ref([]) // 初始化为空数组
const loading = ref(false)

const getFullUrl = (url) => {
  if (!url) return ''
  // 如果已经是完整链接 (http开头)，直接返回
  if (url.startsWith('http')) return url
  // 如果已经包含了 /media/，直接返回
  if (url.startsWith('/media/')) return url
  // 否则，手动补上 /media/ 前缀
  // 注意：如果你的 url 开头有 / (如 /thumbs/...)，要处理一下
  const cleanUrl = url.startsWith('/') ? url.slice(1) : url
  return `/media/${cleanUrl}`
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      q: route.query.q || route.query.search || '', 
      ordering: '-upload_time'
    }

    if (activeTab.value === 'my') {
      params.only_my = true
    }

    const res = await getImages(params)
    
    let rawData = []

    // 判断后端返回格式
    if (Array.isArray(res.data)) {
      // 情况A: 后端直接返回数组 (你的当前情况)
      rawData = res.data
    } else if (res.data && Array.isArray(res.data.results)) {
      // 情况B: 后端返回分页对象 (标准 DRF 分页)
      rawData = res.data.results
    }
    
    // 处理图片数据 (确保 URL 格式正确，防止 null 报错)
    images.value = rawData.map(img => ({
        ...img,
        tags: img.tags || [], 
        // 使用 getFullUrl 处理路径
        img_url: getFullUrl(img.img_url),
        thumb_url: getFullUrl(img.thumb_url || img.img_url)
    }))

  } catch (error) {
    console.error("加载图片失败:", error)
  } finally {
    loading.value = false
  }
}

const handleTabChange = () => {
  loadData()
}

onMounted(loadData)

watch(() => route.query, loadData, { deep: true })
</script>