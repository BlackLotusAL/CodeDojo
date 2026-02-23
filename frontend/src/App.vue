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
    
    <!-- 导航栏 -->
    <el-menu
      :default-active="activeMenu"
      class="el-menu-demo main-nav"
      mode="horizontal"
      router
    >
      <el-menu-item index="/dashboard">仪表盘</el-menu-item>
      <el-menu-item index="/question-bank">题库</el-menu-item>
      <el-menu-item index="/exam">考试</el-menu-item>
      <el-menu-item index="/wrong-book">错题本</el-menu-item>
      <el-menu-item index="/rankings">排行榜</el-menu-item>
    </el-menu>
    
    <!-- 路由视图 -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const userIp = ref('')

// 计算当前激活的菜单
const activeMenu = computed(() => {
  return route.path
})

// 获取用户IP
onMounted(async () => {
  try {
    // 尝试通过API获取用户真实IP
    const response = await axios.get('/api/get-ip')
    userIp.value = response.data.ip
  } catch (error) {
    console.error('Failed to get user IP from API, using fallback method:', error)
    // 备用方案：使用第三方服务获取IP
    try {
      const response = await axios.get('https://api.ipify.org?format=json')
      userIp.value = response.data.ip
    } catch (fallbackError) {
      console.error('Fallback method also failed, using default IP:', fallbackError)
      userIp.value = '127.0.0.1' // 默认值
    }
  }
})
</script>

<style scoped>
.app-container {
  height: auto;
  padding-top: 110px;
}

.ip-alert {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  margin: 0;
  border-radius: 0;
  border: none;
  height: 50px;
  display: flex;
  align-items: center;
}

.main-nav {
  position: fixed;
  top: 50px;
  left: 0;
  right: 0;
  z-index: 999;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin: 0;
  border-radius: 0;
  border: none;
  min-height: 60px;
  padding: 0;
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
