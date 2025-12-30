<template>
  <NavBar />
  <div v-if="image" class="max-w-6xl mx-auto p-4 md:p-8 grid grid-cols-1 md:grid-cols-3 gap-8">
    
    <!-- 左侧：大图展示 -->
    <div class="md:col-span-2">
      <div class="bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center">
        <img :src="image.img_url" class="max-w-full max-h-[80vh] object-contain" />
      </div>
      
      <!-- 操作按钮栏 -->
      <div class="mt-4 flex space-x-4" v-if="isOwner">
        <el-button type="primary" icon="Edit" @click="openCropper">裁剪/编辑</el-button>
        <el-popconfirm title="确定删除吗?" @confirm="handleDelete">
          <template #reference>
            <el-button type="danger" icon="Delete">删除</el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <!-- 右侧：EXIF 信息 -->
    <div class="bg-white p-6 rounded-lg shadow border h-fit">
      <h2 class="text-xl font-bold mb-4">详细信息</h2>
      
      <div class="space-y-4 text-sm text-gray-700">
        <div class="flex items-center">
          <el-icon class="mr-2"><User /></el-icon>
          <span class="font-bold mr-2">上传者:</span> {{ image.uploader_name }}
        </div>
        
        <div class="border-t pt-4">
          <h3 class="font-bold mb-2 text-gray-900">拍摄参数 (EXIF)</h3>
          <div class="grid grid-cols-2 gap-y-2">
            <div><span class="text-gray-500">设备:</span> {{ image.camera_model || '未知' }}</div>
            <div><span class="text-gray-500">时间:</span> {{ formatDate(image.shoot_time) }}</div>
            <div><span class="text-gray-500">ISO:</span> {{ image.iso || '-' }}</div>
            <div><span class="text-gray-500">光圈:</span> {{ image.f_stop ? 'f/'+image.f_stop : '-' }}</div>
            <div><span class="text-gray-500">快门:</span> {{ image.exposure_time || '-' }}</div>
            <div><span class="text-gray-500">地点:</span> {{ image.location || '无位置信息' }}</div>
          </div>
        </div>

        <div class="border-t pt-4">
          <h3 class="font-bold mb-2">标签</h3>
          <div class="flex flex-wrap gap-2">
            <el-tag v-for="tag in image.tags" :key="tag.id">{{ tag.name }}</el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 裁剪弹窗 -->
  <el-dialog v-model="cropperVisible" title="图片裁剪" width="90%" :destroy-on-close="true">
    <div class="h-[400px] w-full bg-gray-900">
      <img ref="cropperImgRef" :src="image?.img_url" class="block max-w-full" />
    </div>
    <template #footer>
      <el-button @click="cropperVisible = false">取消</el-button>
      <el-button type="primary" @click="saveCrop" :loading="saving">保存修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getImageDetail, deleteImage, updateImage } from '@/api/image'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const image = ref(null)
const isOwner = computed(() => userStore.userInfo?.username === image.value?.uploader_name)

// 获取详情
const loadDetail = async () => {
  const res = await getImageDetail(route.params.id)
  image.value = res.data
}

const handleDelete = async () => {
  await deleteImage(image.value.id)
  ElMessage.success('删除成功')
  router.push('/')
}

const formatDate = (str) => {
  if (!str) return '未知'
  return str.replace('T', ' ').split('.')[0]
}

// --- 裁剪逻辑 ---
const cropperVisible = ref(false)
const cropperImgRef = ref(null)
let cropper = null
const saving = ref(false)

const openCropper = async () => {
  cropperVisible.value = true
  await nextTick()
  if (cropperImgRef.value) {
    cropper = new Cropper(cropperImgRef.value, {
      aspectRatio: NaN, // 自由比例
      viewMode: 1
    })
  }
}

const saveCrop = () => {
  saving.value = true
  cropper.getCroppedCanvas().toBlob(async (blob) => {
    const formData = new FormData()
    // 必须传文件名，否则后端可能无法识别
    formData.append('img_url', blob, 'cropped.jpg') 
    
    try {
      await updateImage(image.value.id, formData)
      ElMessage.success('编辑成功')
      cropperVisible.value = false
      loadDetail() // 重新获取新图
    } catch (e) {
      ElMessage.error('保存失败')
    } finally {
      saving.value = false
    }
  }, 'image/jpeg')
}

onMounted(loadDetail)
</script>