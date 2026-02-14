<template>
  <div class="app-container">
    <!-- IP警告条 -->
    <el-alert
      :title="`您的身份识别码：${userIp}（IP变动数据无法关联）`"
      type="warning"
      :closable="false"
      show-icon
      class="ip-alert"
    />
    
    <!-- 路由视图 -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const userIp = ref('')

// 获取用户IP
onMounted(async () => {
  try {
    // 这里简化处理，实际项目中可以通过API获取
    // 或者从后端返回的响应中获取
    userIp.value = '127.0.0.1' // 模拟IP
  } catch (error) {
    console.error('Failed to get user IP:', error)
    userIp.value = 'Unknown'
  }
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  padding-top: 60px;
}

.ip-alert {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  margin: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
