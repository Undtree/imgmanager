<template>
  <div class="masonry-container">
    <div 
      v-for="img in images" 
      :key="img.id" 
      class="image-card-wrapper"
      @click="goToDetail(img.id)"
    >
      <div class="image-card group">
        <!-- 图片主体 (优先显示缩略图) -->
        <div class="relative overflow-hidden">
          <img 
            :src="img.thumb_url || img.img_url" 
            class="w-full block transition-transform duration-500 group-hover:scale-105" 
            loading="lazy" 
          />
          <!-- 悬停遮罩 -->
          <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition duration-300 flex items-center justify-center">
            <span class="text-white opacity-0 group-hover:opacity-100 font-bold tracking-widest border border-white px-4 py-1 rounded-sm">
              VIEW
            </span>
          </div>
        </div>

        <!-- 信息条 -->
        <div class="p-3 bg-white">
          <div class="flex justify-between items-center mb-1">
            <span class="text-sm font-bold text-gray-800 truncate flex-1">
              {{ img.category?.name || '默认相册' }}
            </span>
            <span v-if="img.camera_model" class="text-xs text-gray-400 scale-90 origin-right truncate max-w-[40%]">
              {{ img.camera_model }}
            </span>
          </div>
          
          <div class="text-xs text-gray-500 flex items-center justify-between">
            <div class="flex items-center">
              <el-icon><Clock /></el-icon>
              <span class="ml-1">{{ formatDate(img.upload_time) }}</span>
            </div>
            <!-- 显示标签数量作为小提示 -->
            <div v-if="Array.isArray(img.tags) && img.tags.length > 0" class="bg-blue-50 text-blue-500 px-1.5 rounded">
            #{{ img.tags.length }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Clock } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

// 接收父组件传来的图片数组
const props = defineProps({
  images: {
    type: Array,
    default: () => []
  }
})

const router = useRouter()

const goToDetail = (id) => {
  router.push(`/detail/${id}`)
}

const formatDate = (date) => {
  return dayjs(date).format('MM-DD HH:mm')
}
</script>

<style scoped>
/* 核心瀑布流布局 CSS */
.masonry-container {
  column-count: 2;
  column-gap: 16px; /* 列间距 */
}

/* 响应式断点 (严格对应报告中的设计) */
@media (min-width: 768px) { .masonry-container { column-count: 3; } }
@media (min-width: 1024px) { .masonry-container { column-count: 4; } }
@media (min-width: 1280px) { .masonry-container { column-count: 5; } }

.image-card-wrapper {
  break-inside: avoid; /* 防止卡片被断开 */
  margin-bottom: 16px; /* 行间距 */
}

.image-card {
  @apply rounded-lg overflow-hidden shadow-sm hover:shadow-lg transition-shadow duration-300 cursor-pointer border border-gray-100;
}
</style>