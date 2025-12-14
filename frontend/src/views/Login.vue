<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 px-4">
    <el-card class="w-full max-w-md">
      <el-tabs v-model="activeTab" class="demo-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" label-position="top">
            <el-form-item label="用户名">
              <el-input v-model="loginForm.username" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input type="password" v-model="loginForm.password" show-password />
            </el-form-item>
            <el-button type="primary" class="w-full" @click="onLogin" :loading="loading">登录</el-button>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="注册" name="register">
          <el-form :model="regForm" label-position="top">
            <el-form-item label="用户名 (唯一)">
              <el-input v-model="regForm.username" />
            </el-form-item>
            <el-form-item label="邮箱 (唯一)">
              <el-input v-model="regForm.email" />
            </el-form-item>
            <el-form-item label="密码 (>6位)">
              <el-input type="password" v-model="regForm.password" />
            </el-form-item>
            <el-button type="success" class="w-full" @click="onRegister" :loading="loading">注册</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { login, register } from '@/api/auth'
import { ElMessage } from 'element-plus'

const activeTab = ref('login')
const loading = ref(false)
const router = useRouter()
const userStore = useUserStore()

const loginForm = reactive({ username: '', password: '' })
const regForm = reactive({ username: '', email: '', password: '' })

const onLogin = async () => {
  try {
    loading.value = true
    const res = await login(loginForm)

    userStore.setToken(res.data.access, loginForm.username)
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (err) {
    console.error('前端处理发生崩溃:', err)
    
    // 如果是网络错误(response存在)，才提示检查密码
    if (err.response) {
       ElMessage.error(err.response.data.detail || '登录失败: 请检查用户名或密码')
    } else {
       // 否则提示代码错误
       ElMessage.error('程序错误: ' + err.message)
    }
  } finally {
    loading.value = false
  }
}

const onRegister = async () => {
  try {
    loading.value = true
    await register(regForm)
    
    ElMessage.success('注册成功，请登录')
    
    // 注册成功后，自动填充登录表单，防止手误或填充失败
    loginForm.username = regForm.username
    loginForm.password = regForm.password 
    
    activeTab.value = 'login'
  } catch (err) {
    // 打印具体错误以便调试
    console.error(err) 
    ElMessage.error(err.response?.data?.detail || '注册失败: 用户名或邮箱可能已存在')
  } finally {
    loading.value = false
  }
}
</script>