<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <!-- 路由出口：所有页面（Home, Login等）都会渲染在这里 -->
  <RouterView />
</template>

<style>
/* 全局样式重置 */
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Noto Sans SC', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #f9fafb; /* bg-gray-50 */
}
</style>