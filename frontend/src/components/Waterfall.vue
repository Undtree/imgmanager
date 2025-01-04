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
.masonry-wrapper {
  width: 100%;
  margin: 0 auto;
}

.masonry-container {
  /* 默认（移动端）设置：更紧凑的间距 */
  column-count: 2;
  column-gap: 12px; /* 移动端间距缩小到 12px，让图片更大 */
}

@media (min-width: 640px) {
  /* 平板竖屏 / 大屏手机 */
  .masonry-container {
    column-count: 2;
    column-gap: 16px; /* 稍微拉开间距 */
  }
}

@media (min-width: 768px) {
  /* iPad / 笔记本小屏 */
  .masonry-container {
    column-count: 3;
    column-gap: 20px;
  }
}

@media (min-width: 1024px) {
  /* 普通桌面显示器 */
  .masonry-container {
    column-count: 4;
    column-gap: 24px; /* PC 端享受大间距 */
  }
}

@media (min-width: 1440px) {
  /* 大屏显示器 */
  .masonry-container {
    column-count: 5;
    column-gap: 24px;
  }
}

@media (min-width: 1920px) {
  /* 超宽屏 */
  .masonry-container {
    column-count: 6;
    column-gap: 24px;
  }
}

.image-card-wrapper {
  /* 防止卡片在列之间被截断 */
  break-inside: avoid;
  /* 底部间距与列间距保持一致或稍大 */
  margin-bottom: 10px; /* 移动端 */
  
  /* 这里的 z-index 和 position 保证悬浮效果 */
  position: relative;
  z-index: 1;
  transition: z-index 0s step-end; /* 悬浮结束后立即降低层级 */
}

@media (min-width: 768px) {
  .image-card-wrapper {
    margin-bottom: 24px; /* PC 端增大底部间距 */
  }
  .image-card-wrapper:hover {
    z-index: 10;
    transition: z-index 0s step-start; /* 悬浮开始时立即提高层级 */
  }
}

/* 卡片样式 */
.image-card {
  border-radius: 8px; /* 移动端圆角稍小 */
  overflow: hidden;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); /* 移动端阴影极轻，提升性能 */
  transition: all 0.3s ease;
  will-change: transform;
}

@media (min-width: 768px) {
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
}
</style>