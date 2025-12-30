<template>
  <NavBar />
  <div class="max-w-2xl mx-auto p-6 mt-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg transition-colors duration-300">
    <h1 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">上传图片</h1>
    
    <el-form label-position="top">
      <!-- 1. 相册选择 -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">选择或创建相册</label>
        <el-select
          v-model="selectedCategory"
          filterable
          allow-create
          default-first-option
          placeholder="请选择相册，或直接输入名称新建"
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
      </div>
      
      <!-- 2. 图片选择 -->
      <el-form-item label="选择图片">
        <el-upload
          class="upload-demo w-full"
          drag
          action="#"
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
          list-type="picture"
          ref="uploadRef"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">拖拽或点击上传</div>
        </el-upload>
      </el-form-item>

      <!-- 3. 标签输入 (含 AI 按钮) -->
      <el-form-item>
        <template #label>
          <div class="flex items-center justify-between">
            <span>标签 (输入后回车)</span>
            <!-- AI 识别按钮 -->
            <el-button 
              type="primary" 
              link 
              size="small" 
              @click="handleAIAnalyze" 
              :loading="aiLoading"
              :disabled="!file"
            >
              <el-icon class="mr-1"><MagicStick /></el-icon>
              AI 智能识别
            </el-button>
          </div>
        </template>
        
        <el-select
          v-model="tags"
          multiple
          filterable
          allow-create
          default-first-option
          :reserve-keyword="false" 
          placeholder="例如: 风景, 海边"
          class="w-full"
          size="large"
        >
          <!-- 
            一旦选中/创建了选项，就把输入框里的文字清空。
          -->
        </el-select>
      </el-form-item>

      <!-- 4. 是否公开 -->
      <el-form-item>
        <el-checkbox v-model="isPublic" class="!text-gray-700 dark:!text-gray-300">设为公开可见</el-checkbox>
      </el-form-item>

      <el-button type="primary" class="w-full mt-4 !h-12 !text-lg" @click="submitUpload" :loading="uploading">
        开始上传
      </el-button>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { UploadFilled, MagicStick } from '@element-plus/icons-vue' // 引入 MagicStick 图标
import { uploadImage, getCategories, analyzeImage } from '@/api/image' // 引入 analyzeImage
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const uploadRef = ref(null)

// 表单数据
const file = ref(null)
const tags = ref([]) 
const selectedCategory = ref('') 
const isPublic = ref(true)
const categories = ref([]) 

const uploading = ref(false)
const aiLoading = ref(false) // AI 识别中的 Loading 状态

// 获取相册列表
onMounted(async () => {
  try {
    const res = await getCategories()
    categories.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (e) {
    console.error('获取相册失败', e)
  }
})

const handleFileChange = (uploadFile) => {
  file.value = uploadFile.raw
}

const handleExceed = (files) => {
  uploadRef.value.clearFiles()
  const file = files[0]
  uploadRef.value.handleStart(file)
}

// AI 识别逻辑
const handleAIAnalyze = async () => {
  if (!file.value) {
    return ElMessage.warning('请先选择一张图片')
  }

  aiLoading.value = true
  const formData = new FormData()
  formData.append('img_url', file.value) // 注意字段名要和后端对应

  try {
    const res = await analyzeImage(formData)
    const suggestedTags = res.data.suggested_tags || []
    
    if (suggestedTags.length === 0) {
      ElMessage.info('AI 未能识别出明显的物体')
    } else {
      // 合并标签并去重
      suggestedTags.forEach(tag => {
        if (!tags.value.includes(tag)) {
          tags.value.push(tag)
        }
      })
      ElMessage.success(`AI 识别成功，添加了 ${suggestedTags.length} 个标签`)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('AI 识别服务暂不可用')
  } finally {
    aiLoading.value = false
  }
}

// 提交上传
const submitUpload = async () => {
  if (!file.value) return ElMessage.warning('请选择图片')
  
  uploading.value = true
  const formData = new FormData()
  
  formData.append('img_url', file.value)
  formData.append('is_public', isPublic.value ? 'True' : 'False')
  
  if (selectedCategory.value) {
    formData.append('upload_category', selectedCategory.value)
  }

  tags.value.forEach(tag => {
    formData.append('tag_names', tag) 
  })

  try {
    await uploadImage(formData)
    ElMessage.success('上传成功')
    router.push('/')
  } catch (error) {
    console.error(error)
    ElMessage.error('上传失败: ' + (error.response?.data?.detail || '未知错误'))
  } finally {
    uploading.value = false
  }
}
</script>