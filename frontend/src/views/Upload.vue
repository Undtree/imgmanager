<template>
  <NavBar />
  <div class="max-w-2xl mx-auto p-6 bg-white mt-8 rounded shadow">
    <h1 class="text-2xl font-bold mb-6">上传图片</h1>
    
    <el-form label-position="top">
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
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadImage } from '@/api/image'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const file = ref(null)
const tags = ref([])
const isPublic = ref(true)
const uploading = ref(false)

const handleFileChange = (uploadFile) => {
  file.value = uploadFile.raw
}

const submitUpload = async () => {
  if (!file.value) return ElMessage.warning('请选择图片')
  
  uploading.value = true
  const formData = new FormData()
  formData.append('img_url', file.value)
  formData.append('is_public', isPublic.value)
  // 必须将数组中的每个标签单独 append，后端用 ListField 处理
  // 或者如果不生效，可以在后端改为接收逗号分隔字符串
  tags.value.forEach(tag => {
    formData.append('tag_names', tag) 
  })

  try {
    await uploadImage(formData)
    ElMessage.success('上传成功')
    router.push('/')
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}
</script>