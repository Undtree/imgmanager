<template>
  <div class="h-screen flex flex-col bg-[#141414] text-white overflow-hidden">
    <!-- 顶部工具栏 -->
    <div class="h-16 bg-[#1f1f1f] flex justify-between items-center px-6 shrink-0 border-b border-[#333]">
      <div class="flex items-center space-x-4">
        <el-button link @click="$router.back()" class="!text-gray-400 hover:!text-white">
          <el-icon class="mr-1"><ArrowLeft /></el-icon> 返回
        </el-button>
        <span class="text-lg font-medium tracking-wide">编辑工作台</span>
      </div>
      <el-button type="primary" size="large" @click="saveEdit" :loading="saving" class="!px-8">
        保存更改
      </el-button>
    </div>

    <div class="flex-1 flex overflow-hidden">
      
      <!-- 左侧：画布区域 -->
      <div class="flex-1 flex flex-col relative bg-[#141414]">
        <!-- 绑定 Style -->
        <div class="flex-1 flex flex-col relative bg-[#141414]" :style="{ '--img-filter': filterString }" >
          <!-- 图片容器 -->
          <div class="flex-1 p-8 flex items-center justify-center overflow-hidden">
            <!-- 
              图片本身不需要加 bg-checkered。
              CropperJS 会初始化并把图片包裹在一个容器里，
              我们只需要确保 Cropper 的 CSS 正确加载，它自带透明背景样式。
            -->
            <img ref="imageRef" :src="imgUrl" class="max-w-full hidden" v-if="imgUrl"/>
          </div>
          
          <!-- 底部悬浮工具栏 -->
          <div class="h-20 bg-[#1f1f1f] border-t border-[#333] flex items-center justify-center space-x-6 shrink-0 z-10">
            <el-tooltip content="向左旋转" placement="top">
              <el-button circle size="large" @click="rotate(-90)" class="tool-btn"><el-icon><RefreshLeft /></el-icon></el-button>
            </el-tooltip>
            <el-tooltip content="向右旋转" placement="top">
              <el-button circle size="large" @click="rotate(90)" class="tool-btn"><el-icon><RefreshRight /></el-icon></el-button>
            </el-tooltip>
            
            <div class="w-px h-8 bg-[#444] mx-2"></div>
            
            <span class="text-xs text-gray-500 font-bold mr-2">比例</span>
            <el-radio-group v-model="aspectRatio" size="small" @change="setAspectRatio" class="ratio-group">
              <el-radio-button :label="NaN">自由</el-radio-button>
              <el-radio-button :label="1">1:1</el-radio-button>
              <el-radio-button :label="4/3">4:3</el-radio-button>
              <el-radio-button :label="16/9">16:9</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </div>

      <!-- 右侧：属性编辑 (侧边栏) -->
      <div class="w-96 bg-[#1f1f1f] border-l border-[#333] flex flex-col shrink-0">
        <el-tabs v-model="activeTab" class="custom-tabs h-full flex flex-col" stretch>
          
          <!-- Tab 1: 调色功能 -->
          <el-tab-pane label="色彩调整" name="adjust" class="h-full overflow-y-auto">
            <div class="p-6 space-y-8">
              
              <!-- 亮度 -->
              <div class="filter-item">
                <div class="flex justify-between mb-2 text-sm text-gray-400">
                  <span>亮度</span>
                  <span>{{ filters.brightness }}%</span>
                </div>
                <el-slider v-model="filters.brightness" :min="0" :max="200" :format-tooltip="val => val + '%'" />
              </div>

              <!-- 对比度 -->
              <div class="filter-item">
                <div class="flex justify-between mb-2 text-sm text-gray-400">
                  <span>对比度</span>
                  <span>{{ filters.contrast }}%</span>
                </div>
                <el-slider v-model="filters.contrast" :min="0" :max="200" :format-tooltip="val => val + '%'" />
              </div>

              <!-- 饱和度 -->
              <div class="filter-item">
                <div class="flex justify-between mb-2 text-sm text-gray-400">
                  <span>饱和度</span>
                  <span>{{ filters.saturate }}%</span>
                </div>
                <el-slider v-model="filters.saturate" :min="0" :max="200" :format-tooltip="val => val + '%'" />
              </div>
              
              <!-- 重置按钮 -->
              <div class="pt-4 text-center">
                 <el-button text bg size="small" @click="resetFilters">重置所有参数</el-button>
              </div>

            </div>
          </el-tab-pane>

          <!-- Tab 2: 属性编辑 (原有的表单) -->
          <el-tab-pane label="属性信息" name="info" class="h-full overflow-y-auto">
            <div class="p-6 space-y-8">
              <el-form label-position="top" class="dark-form">
                <el-form-item label="所属相册">
                  <el-select
                    v-model="form.category"
                    filterable
                    allow-create
                    default-first-option
                    placeholder="搜索或创建相册"
                    class="w-full"
                    size="large"
                  >
                    <el-option
                      v-for="item in categories"
                      :key="item.id"
                      :label="item.name"
                      :value="item.name"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item label="标签">
                  <el-select
                    v-model="form.tags"
                    multiple
                    filterable
                    allow-create
                    default-first-option
                    :reserve-keyword="false"
                    placeholder="输入标签并回车"
                    class="w-full"
                    size="large"
                  >
                    <!-- 用户输入创建 -->
                  </el-select>
                </el-form-item>

                <el-form-item label="隐私设置">
                  <div class="bg-[#2a2a2a] rounded-lg p-4 flex items-center justify-between border border-[#333]">
                    <div class="flex items-center">
                      <el-icon class="mr-2 text-gray-400" size="16"><component :is="form.is_public ? 'View' : 'Hide'" /></el-icon>
                      <span class="text-sm text-gray-200">{{ form.is_public ? '公开可见' : '私密图片' }}</span>
                    </div>
                    <el-switch 
                      v-model="form.is_public" 
                      style="--el-switch-on-color: #10b981;"
                    />
                  </div>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'
import { getImageDetail, updateImage, getCategories } from '@/api/image'
import { ElMessage } from 'element-plus'
import { ArrowLeft, RefreshLeft, RefreshRight, View, Hide } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// UI State
const imageRef = ref(null)
const imgUrl = ref('')
const saving = ref(false)
const aspectRatio = ref(NaN)
const activeTab = ref('adjust') 
let cropper = null

// Data State
const categories = ref([])
const form = reactive({
  category: '',
  tags: [],
  is_public: true
})

const filters = reactive({
  brightness: 100,
  contrast: 100,
  saturate: 100
})

const filterString = computed(() => {
  return `brightness(${filters.brightness}%) contrast(${filters.contrast}%) saturate(${filters.saturate}%)`
})

const resetFilters = () => {
  filters.brightness = 100
  filters.contrast = 100
  filters.saturate = 100
}

onMounted(async () => {
  const id = route.params.id
  try {
    const [detailRes, catRes] = await Promise.all([
      getImageDetail(id),
      getCategories()
    ])

    // 填充数据
    const data = detailRes.data
    imgUrl.value = data.img_url
    form.category = data.category_name || ''
    if (data.tags && data.tags.length > 0) {
      form.tags = data.tags.map(t => (typeof t === 'object' ? t.name : t))
    } else {
      form.tags = []
    }
    form.is_public = data.is_public

    categories.value = Array.isArray(catRes.data) ? catRes.data : (catRes.data.results || [])

    // 初始化 Cropper
    setTimeout(() => {
      if (imageRef.value) {
        cropper = new Cropper(imageRef.value, {
          viewMode: 1, // 限制裁剪框在图片内
          dragMode: 'move', // 允许拖动图片
          background: true, // 显示自带的棋盘格背景
          autoCropArea: 0.9,
          restore: false,
          guides: true,
          center: true,
          highlight: false,
          cropBoxMovable: true,
          cropBoxResizable: true,
          toggleDragModeOnDblclick: false,
        })
      }
    }, 200)

  } catch (e) {
    ElMessage.error('加载失败')
    router.push('/')
  }
})

// Cropper Actions
const rotate = (deg) => cropper?.rotate(deg)
const setAspectRatio = (ratio) => {
  aspectRatio.value = ratio
  cropper?.setAspectRatio(ratio)
}

const applyFiltersToCanvas = (sourceCanvas) => {
  // 如果没有做任何修改，直接返回原 Canvas
  if (filters.brightness === 100 && filters.contrast === 100 && filters.saturate === 100) {
    return sourceCanvas
  }

  // 创建一个新 Canvas
  const canvas = document.createElement('canvas')
  canvas.width = sourceCanvas.width
  canvas.height = sourceCanvas.height
  const ctx = canvas.getContext('2d')

  // 设置滤镜 (Canvas API 支持 filter 字符串，格式与 CSS 几乎一样)
  ctx.filter = filterString.value
  
  // 将裁剪后的图片画上去（带滤镜）
  ctx.drawImage(sourceCanvas, 0, 0)
  
  return canvas
}

// 保存逻辑
const saveEdit = () => {
  if (!cropper) return
  saving.value = true
  
  cropper.getCroppedCanvas({
    imageSmoothingEnabled: true,
    imageSmoothingQuality: 'high',
  }).toBlob(async (blob) => {
    
    const formData = new FormData()
    formData.append('img_url', blob, 'edited.jpg')
    formData.append('is_public', form.is_public ? 'True' : 'False')
    
    if (form.category) formData.append('category_upload', form.category)
    form.tags.forEach(tag => formData.append('tag_names', tag))

    try {
      await updateImage(route.params.id, formData)
      ElMessage.success('保存成功')
      router.back()
    } catch(e) {
      ElMessage.error('保存失败')
    } finally {
      saving.value = false
    }
  }, 'image/jpeg', 0.95)
}

onUnmounted(() => {
  cropper?.destroy()
})
</script>

<style scoped>
/* 定制 Cropper 样式 */
:deep(.cropper-view-box img),
:deep(.cropper-canvas img) {
  filter: var(--img-filter, none);
  transition: filter 0.1s; /* 稍微加一点过渡让滑块更顺滑 */
}

:deep(.cropper-bg) {
  background-image: linear-gradient(45deg, #eee 25%, transparent 25%),
    linear-gradient(-45deg, #eee 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #eee 75%),
    linear-gradient(-45deg, transparent 75%, #eee 75%);
  background-size: 20px 20px;
}

/* 按钮样式微调 */
.tool-btn {
  background-color: #333 !important;
  border: none !important;
  color: #ccc !important;
}
.tool-btn:hover {
  background-color: #444 !important;
  color: white !important;
}

/* 强制覆盖 Element Plus 暗黑样式 */
.dark-form :deep(.el-form-item__label) {
  color: #a3a3a3 !important;
  font-weight: 500;
}

/* 输入框深色适配 */
.dark-form :deep(.el-input__wrapper),
.dark-form :deep(.el-textarea__inner),
.dark-form :deep(.el-select__wrapper) {
  background-color: #2a2a2a !important;
  border: 1px solid #333 !important;
  box-shadow: none !important;
  color: white !important;
  transition: all 0.2s;
}

/* 聚焦时的高亮 */
.dark-form :deep(.el-input__wrapper.is-focus),
.dark-form :deep(.el-select__wrapper.is-focused) {
  border-color: #409eff !important;
}

/* 选中项文字颜色 */
.dark-form :deep(.el-select__selected-item) {
  color: #fff !important;
}

/* Radio Button Group 定制 */
.ratio-group :deep(.el-radio-button__inner) {
  background-color: #2a2a2a;
  border-color: #333;
  color: #aaa;
}
.ratio-group :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
  box-shadow: none;
}
</style>