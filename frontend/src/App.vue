<script setup>
import { RouterView } from 'vue-router'
import { useThemeStore } from '@/stores/themes'

const themeStore = useThemeStore()
themeStore.initTheme()
</script>

<template>
  <!-- 
    这里的 class 负责处理 App 内部的背景和文字颜色，添加平滑过渡动画
  -->
  <div class="min-h-screen transition-colors duration-300 bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-200">
    <RouterView />
  </div>
</template>

<style>
/* 
  使用 CSS 变量来控制 body 背景 
  这样可以确保滚动条轨道、页面回弹区域的颜色也是正确的
*/
:root {
  --app-bg-color: #f9fafb; /* 对应 Tailwind 的 gray-50 */
}

/* 当 html 标签上有 dark 类时，修改变量值 */
:root.dark {
  --app-bg-color: #111827; /* 对应 Tailwind 的 gray-900 */
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Noto Sans SC', Roboto, 'Helvetica Neue', Arial, sans-serif;
  
  /* 使用变量，并添加过渡动画 */
  background-color: var(--app-bg-color);
  transition: background-color 0.3s ease;
}
</style>