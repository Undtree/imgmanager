<template>
  <NavBar />
  <div class="max-w-2xl mx-auto p-6 mt-8 rounded shadow">
    <h1 class="text-2xl font-bold mb-6">上传图片</h1>
    
    <el-form label-position="top">
      <!-- 相册选择 -->
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
          @change="handleCategoryChange"
        >
          <el-option
            v-for="item in categories"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </div>
      
      <!-- 图片选择 -->
      <el-form-item label="选择图片">
        <el-upload
          class="upload-demo w-full"
          drag
          action="#"
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          list-type="picture"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">拖拽或点击上传</div>
        </el-upload>
      </el-form-item>

      <!-- 标签输入 -->
      <el-form-item label="标签 (输入后回车)">
        <el-select
          v-model="tags"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="例如: 风景, 海边"
          class="w-full"
        >
        </el-select>
      </el-form-item>

      <!-- 是否公开 -->
      <el-form-item>
        <el-checkbox v-model="isPublic">设为公开可见</el-checkbox>
      </el-form-item>

      <el-button type="primary" class="w-full mt-4" @click="submitUpload" :loading="uploading">
        开始上传
      </el-button>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadImage, getCategories } from '@/api/image' // 引入 getCategories
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const uploadRef = ref(null)

// 表单数据
const file = ref(null)
const tags = ref([]) // 数组，例如 ['风景', '夏天']
const selectedCategory = ref('') // 字符串，例如 '我的生活'
const isPublic = ref(true)
const categories = ref([]) // 后端返回的列表

const uploading = ref(false)

// 获取已有的相册列表
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

const submitUpload = async () => {
  if (!file.value) return ElMessage.warning('请选择图片')
  
  uploading.value = true
  const formData = new FormData()
  
  formData.append('img_url', file.value)
  // Convert boolean to string for FormData (Python handles 'true'/'false' usually, but '1'/'0' or proper parsing is safer)
  // Django's default BooleanField handles JS 'true'/'false' strings well in FormData
  formData.append('is_public', isPublic.value ? 'True' : 'False')
  
  // 发送相册名称
  if (selectedCategory.value) {
    formData.append('upload_category', selectedCategory.value)
  }

  // 发送标签列表
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