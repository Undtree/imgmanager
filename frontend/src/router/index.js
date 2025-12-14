import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
// 引入页面组件
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Detail from '../views/Detail.vue'
import Upload from '../views/Upload.vue'
import ImageEdit from '../views/ImageEdit.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { 
      path: '/', 
      component: Home,
      meta: { requiresAuth: true } // 首页改为需要登录
    },
    { 
      path: '/login', 
      component: Login,
      meta: { guestOnly: false }
    },
    { 
      path: '/detail/:id', 
      component: Detail,
      meta: { requiresAuth: true } // 详情页通常也保护起来
    },
    { 
      path: '/upload', 
      component: Upload, 
      meta: { requiresAuth: true } 
    },
    { 
      path: '/edit/:id', 
      component: ImageEdit, 
      meta: { requiresAuth: true } 
    },
  ]
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const isAuthenticated = !!userStore.token

  // 1. 如果页面需要登录，且用户未登录 -> 踢到登录页
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } 
  // 2. 如果页面是“游客专用”（如登录页），且用户已登录 -> 踢回首页
  //    这样避免了用户登录后手贱输入 /login 又看到登录框
  else if (to.meta.guestOnly && isAuthenticated) {
    next('/')
  }
  // 3. 其他情况 -> 放行
  else {
    next()
  }
})

export default router