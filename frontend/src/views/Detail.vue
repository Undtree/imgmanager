<template>
  <div class="bg-gray-50 dark:bg-gray-900 min-h-screen transition-colors duration-300">
    <NavBar />
    
    <div class="container mx-auto p-4 md:p-8" v-if="img">
      <!-- 顶部操作栏 -->
      <div class="flex justify-between items-center mb-6">
        <el-button @click="$router.back()" circle icon="ArrowLeft" />
        <div v-if="isOwner" class="space-x-3">
          <!-- [关键修改] 点击跳转到 /edit/:id -->
          <el-button type="primary" :icon="Edit" @click="$router.push(`/edit/${img.id}`)">
            编辑详情 & 裁剪
          </el-button>
          <el-popconfirm title="确定删除这张图片吗？" @confirm="handleDelete">
            <template #reference>
              <el-button type="danger" :icon="Delete" plain>删除</el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- 左侧大图 -->
        <div class="lg:col-span-2 bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-4 flex items-center justify-center border border-gray-100 dark:border-gray-700">
          <!-- 这里使用棋盘格背景，但只在图片透明部分透出来 -->
          <div class="relative bg-checkered rounded-lg overflow-hidden shadow-inner inline-block">
             <img 
              :src="img.img_url" 
              class="max-h-[75vh] w-auto object-contain cursor-zoom-in block" 
              @click="showLightbox = true"
            />
          </div>
        </div>

        <!-- 右侧信息面板 -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 space-y-8 border border-gray-100 dark:border-gray-700 h-fit">
          <!-- 标题区 -->
          <div>
            <div class="text-sm font-bold text-blue-600 mb-2 uppercase tracking-wide">
              {{ img.category_name || '默认相册' }}
            </div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
               图片详情
            </h1>
            <div class="flex items-center space-x-3 text-gray-500 dark:text-gray-400 text-sm">
              <el-avatar :size="32" class="bg-blue-100 text-blue-600 font-bold">
                {{ img.uploader_name?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="font-medium text-gray-700 dark:text-gray-300">{{ img.uploader_name }}</span>
              <span>•</span>
              <span>{{ formatDate(img.upload_time) }}</span>
            </div>
          </div>

          <!-- 标签区 -->
          <div>
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-3">标签</h3>
            <div class="flex flex-wrap gap-2">
               <el-tag 
                v-for="tag in img.tags" 
                :key="tag" 
                effect="plain"
                round
                class="!border-gray-200 dark:!border-gray-600 dark:!bg-gray-700 dark:!text-gray-200"
              >
                # {{ typeof tag === 'object' ? tag.name : tag }}
              </el-tag>
              <span v-if="!img.tags?.length" class="text-gray-400 text-sm italic">暂无标签</span>
            </div>
          </div>

          <!-- EXIF / 信息网格 -->
          <div>
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-3">EXIF 信息</h3>
            <div class="grid grid-cols-2 gap-4">
              <div class="info-card">
                <el-icon><Camera /></el-icon>
                <span class="truncate">{{ img.camera_model || '未知设备' }}</span>
              </div>
              
              <!-- 分辨率信息 -->
              <div class="info-card">
                <el-icon><Picture /></el-icon>
                <span>{{ img.width }} x {{ img.height }} px</span>
              </div>
              
              <div class="info-card flex items-start">
                <el-icon><Location /></el-icon>
                <span class="text-sm leading-snug break-words whitespace-normal text-gray-700 dark:text-gray-300">
                  {{ img.location || '无位置' }}
                </span>
              </div>

              <div class="info-card" title="ISO 感光度">
                <!-- Element Plus 没有专门的 ISO 图标，用 Aim 代替 -->
                <el-icon><Aim /></el-icon>
                <span>ISO {{ img.iso || 'Auto' }}</span>
              </div>
              
              <div class="info-card">
                <el-icon><Timer /></el-icon>
                <span>{{ formatDate(img.shoot_time) || '未知时间' }}</span>
              </div>

               <div class="info-card">
                <el-icon><Files /></el-icon>
                <span>{{ Math.round(img.file_size || 0) }} KB</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 灯箱模式 (全屏查看) -->
    <el-dialog v-model="showLightbox" fullscreen class="lightbox-modal" :show-close="false">
      <div class="w-full h-full flex flex-col" @click="showLightbox = false">
         <div class="flex-1 flex items-center justify-center bg-black/95 backdrop-blur-sm p-4">
             <img :src="img.img_url" class="max-h-full max-w-full shadow-2xl" @click.stop />
         </div>
      </div>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getImageDetail, deleteImage } from '@/api/image'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Edit, Delete, Camera, Picture, Location, Timer, Files, ArrowLeft } from '@element-plus/icons-vue'
import NavBar from '@/components/NavBar.vue'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const img = ref(null)
const showLightbox = ref(false)

const isOwner = computed(() => img.value?.uploader_name === userStore.username)
const formatDate = (d) => d ? dayjs(d).format('YYYY-MM-DD HH:mm') : ''

const loadDetail = async () => {
  try {
    const res = await getImageDetail(route.params.id)
    img.value = res.data
  } catch (e) {
    ElMessage.error('图片加载失败')
    router.push('/')
  }
}

const handleDelete = async () => {
  try {
    await deleteImage(img.value.id)
    ElMessage.success('删除成功')
    router.push('/')
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(loadDetail)
</script>

<style scoped>
.info-card {
  @apply flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-sm text-gray-600 dark:text-gray-300;
}

.bg-checkered {
  background-color: #f3f4f6; /* 浅灰底 */
  background-image: 
    linear-gradient(45deg, #e5e7eb 25%, transparent 25%),
    linear-gradient(-45deg, #e5e7eb 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #e5e7eb 75%),
    linear-gradient(-45deg, transparent 75%, #e5e7eb 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
}
.dark .bg-checkered {
  background-color: #1f2937;
  background-image: 
    linear-gradient(45deg, #374151 25%, transparent 25%),
    linear-gradient(-45deg, #374151 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #374151 75%),
    linear-gradient(-45deg, transparent 75%, #374151 75%);
}
</style>