import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// 引入 Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 引入 Element Plus 图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 引入 Tailwind (在之前的步骤中配置过)
import './assets/main.css' 

const app = createApp(App)

// 1. 注册 Pinia (状态管理)
app.use(createPinia())

// 2. 注册 Router (路由)
app.use(router)

// 3. 注册 Element Plus
app.use(ElementPlus)

// 4. 注册所有图标 (方便全局使用)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')