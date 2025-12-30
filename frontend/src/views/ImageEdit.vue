<template>
  <div class="h-screen flex flex-col bg-gray-900">
    <!-- 顶部工具栏 -->
    <div class="h-14 bg-black flex justify-between items-center px-4 text-white">
      <el-button type="text" @click="$router.back()" class="text-white">取消</el-button>
      <span>编辑图片</span>
      <el-button type="primary" @click="saveEdit" :loading="saving">保存覆盖</el-button>
    </div>

    <!-- 中间画布区域 -->
    <div class="flex-1 overflow-hidden relative bg-black flex items-center justify-center">
      <img ref="imageRef" :src="imgUrl" class="max-w-full block" v-if="imgUrl"/>
    </div>

    <!-- 底部控制栏 -->
    <div class="h-40 bg-gray-800 p-4 text-white">
      <div class="flex space-x-4 mb-4 justify-center">
        <el-button circle @click="rotate(-90)">↺</el-button>
        <el-button circle @click="rotate(90)">↻</el-button>
        <el-button round @click="setAspectRatio(16/9)">16:9</el-button>
        <el-button round @click="setAspectRatio(4/3)">4:3</el-button>
        <el-button round @click="setAspectRatio(1)">1:1</el-button>
        <el-button round @click="setAspectRatio(NaN)">自由</el-button>
      </div>
      
      <!-- 滤镜 (模拟) -->
      <div class="text-center text-sm text-gray-400">
        滤镜功能仅做演示，后端保存为裁剪后结果
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'
import { getImageDetail, updateImage } from '@/api/image'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const imageRef = ref(null)
const imgUrl = ref('')
const saving = ref(false)
let cropper = null

onMounted(async () => {
  // 1. 获取原图链接
  const res = await getImageDetail(route.params.id)
  imgUrl.value = res.data.img_url // 注意：跨域图片可能会导致 Canvas 污染，后端需配 CORS

  // 2. 初始化 Cropper
  // 必须等待 DOM 更新且图片加载完成，简单起见用 setTimeout 或 @load
  setTimeout(() => {
    cropper = new Cropper(imageRef.value, {
      viewMode: 1,
      dragMode: 'move',
      background: false,
    })
  }, 200)
})

const rotate = (deg) => cropper?.rotate(deg)
const setAspectRatio = (ratio) => cropper?.setAspectRatio(ratio)

const saveEdit = () => {
  if (!cropper) return
  saving.value = true
  
  // 导出 Canvas
  cropper.getCroppedCanvas().toBlob(async (blob) => {
    const formData = new FormData()
    // 覆盖原图字段 'img_url'，或者后端有专门接口
    formData.append('img_url', blob, 'edited.jpg')
    
    try {
      await updateImage(route.params.id, formData)
      ElMessage.success('编辑保存成功')
      router.back()
    } catch(e) {
      ElMessage.error('保存失败')
    } finally {
      saving.value = false
    }
  }, 'image/jpeg', 0.8)
}

onUnmounted(() => {
  cropper?.destroy()
})
</script>