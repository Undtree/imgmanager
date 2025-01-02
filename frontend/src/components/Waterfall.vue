<template>
  <div class="masonry-container">
    <div 
      v-for="img in images" 
      :key="img.id" 
      class="image-card-wrapper"
      @click="goToDetail(img.id)"
    >
      <div class="image-card group">
        <!-- 图片主体 -->
        <div class="relative overflow-hidden">
          <img 
            :src="img.thumb_url || img.img_url" 
            class="w-full block transition-all duration-700 ease-out group-hover:scale-110 group-hover:brightness-105" 
            loading="lazy" 
          />
          
          <!-- 悬停遮罩：改为底部渐变，不遮挡主体，只提示 -->
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
            <span class="text-white text-sm font-bold translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
              查看详情 <el-icon class="align-middle"><Right /></el-icon>
            </span>
          </div>
        </div>

        <!-- 信息条 -->
        <div class="p-3 bg-white dark:bg-gray-800 transition-colors duration-300 border-t border-gray-50 dark:border-gray-700">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm font-bold text-gray-800 dark:text-gray-100 truncate flex-1">
              {{ img.category_name || '默认相册' }}
            </span>
            <span v-if="img.camera_model" class="text-xs text-gray-400 dark:text-gray-500 scale-90 origin-right truncate max-w-[45%] bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded">
              {{ img.camera_model }}
            </span>
          </div>
          
          <div class="text-xs text-gray-500 dark:text-gray-400 flex items-center justify-between">
            <div class="flex items-center">
              <el-icon><Clock /></el-icon>
              <span class="ml-1">{{ formatDate(img.upload_time) }}</span>
            </div>
            <div v-if="Array.isArray(img.tags) && img.tags.length > 0" class="bg-blue-50 text-blue-500 dark:bg-blue-100 text-blue-400 font-medium px-1.5 rounded">
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
import { Clock, Right } from '@element-plus/icons-vue' // 记得引入 Right 图标
import dayjs from 'dayjs'

const props = defineProps({
  images: {
    type: Array,
    default: () => []
  }
})

const router = useRouter()
const goToDetail = (id) => router.push(`/detail/${id}`)
const formatDate = (date) => dayjs(date).format('MM-DD HH:mm')
</script>

<style scoped>
/* 核心布局 */
.masonry-container {
  column-count: 2;
  column-gap: 20px; /* 加大一点间距，让悬浮更从容 */
}
@media (min-width: 768px) { .masonry-container { column-count: 3; } }
@media (min-width: 1024px) { .masonry-container { column-count: 4; } }
@media (min-width: 1280px) { .masonry-container { column-count: 5; } }

.image-card-wrapper {
  break-inside: avoid;
  margin-bottom: 20px;
  /* 这里的 z-index 和 position 很重要，保证悬浮时不被遮挡 */
  position: relative;
  z-index: 1;
  transition: z-index 0.3s; 
}
.image-card-wrapper:hover {
  z-index: 10; /* 悬浮时层级最高 */
}

/* 卡片样式 */
.image-card {
  border-radius: 16px; /* 更圆润的角 */
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  will-change: transform, box-shadow;
}

/* 悬停效果：提拉 + 深阴影 */
.image-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
</style>