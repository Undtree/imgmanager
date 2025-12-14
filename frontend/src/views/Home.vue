<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <NavBar />
    
    <div class="container mx-auto px-4 py-6">
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
    <div class="fixed right-6 bottom-8 md:hidden z-40">
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
const images = ref([]) // 初始化为空数组
const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    const params = { 
      search: route.query.search,
      ordering: '-upload_time'
    }
    const res = await getImages(params)
    
    // === 修复开始 ===
    let rawData = []

    // 1. 判断后端返回格式
    if (Array.isArray(res.data)) {
      // 情况A: 后端直接返回数组 (你的当前情况)
      rawData = res.data
    } else if (res.data && Array.isArray(res.data.results)) {
      // 情况B: 后端返回分页对象 (标准 DRF 分页)
      rawData = res.data.results
    }
    
    // 2. 处理图片数据 (确保 URL 格式正确，防止 null 报错)
    images.value = rawData.map(img => ({
        ...img,
        // 如果 tags 是 null，给一个空数组防止 .length 报错
        tags: img.tags || [], 
        // 确保 URL 存在
        img_url: img.img_url || '',
        thumb_url: img.thumb_url || img.img_url || ''
    }))
    // === 修复结束 ===

  } catch (error) {
    console.error("加载图片失败:", error)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

watch(() => route.query.search, loadData)
</script>