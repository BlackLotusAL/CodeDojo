<template>
  <div class="dashboard-container">
    <el-card class="dashboard-card">
      <template #header>
        <div class="card-header">
          <span>学习概览</span>
        </div>
      </template>
      
      <!-- 统计行 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-statistic :value="dashboardData.total_answers" title="累计刷题数" />
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-statistic :value="dashboardData.accuracy" title="客观题正确率" suffix="%" />
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-statistic :value="dashboardData.consecutive_days" title="连续学习天数" />
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-progress
            type="dashboard"
            :percentage="dashboardData.accuracy"
            :color="getAccuracyColor(dashboardData.accuracy)"
          />
        </el-col>
      </el-row>
      
      <!-- 级别进度 -->
      <el-row :gutter="20" class="level-progress-row">
        <el-col :xs="24" :sm="24" :md="8" :lg="8" v-for="(percentage, level) in dashboardData.level_completion" :key="level">
          <el-card class="level-card">
            <template #header>
              <div class="level-header">
                <el-tag :type="getLevelType(level)">{{ getLevelName(level) }}</el-tag>
              </div>
            </template>
            <el-progress
              :percentage="percentage"
              :color="getLevelColor(level)"
              :stroke-width="15"
            />
            <div class="level-percentage">{{ percentage }}%</div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 最近活动 -->
      <el-card class="activity-card">
        <template #header>
          <div class="card-header">
            <span>最近活动</span>
          </div>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="(activity, index) in dashboardData.recent_activities"
            :key="index"
            :timestamp="formatTime(activity.created_at)"
            :type="getActivityType(activity.is_correct)"
          >
            <div class="activity-content">
              <span>题目: {{ activity.question_id }}</span>
              <span class="activity-answer">答案: {{ activity.user_answer }}</span>
              <span class="activity-status" :class="getActivityStatusClass(activity.is_correct)">
                {{ getActivityStatusText(activity.is_correct) }}
              </span>
            </div>
          </el-timeline-item>
        </el-timeline>
        <div v-if="dashboardData.recent_activities.length === 0" class="empty-activity">
          暂无活动记录
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const dashboardData = ref({
  user_info: {
    ip: '',
    nickname: '',
    is_admin: false,
    default_level: 'entry'
  },
  total_answers: 0,
  accuracy: 0,
  consecutive_days: 0,
  level_completion: {
    entry: 0,
    work: 0,
    pro: 0
  },
  recent_activities: []
})

// 获取仪表盘数据
onMounted(async () => {
  try {
    const data = await api.getDashboard()
    dashboardData.value = data
  } catch (error) {
    console.error('Failed to get dashboard data:', error)
  }
})

// 格式化时间
const formatTime = (timeString) => {
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN')
}

// 获取级别标签类型
const getLevelType = (level) => {
  switch (level) {
    case 'entry': return 'success'
    case 'work': return 'primary'
    case 'pro': return 'danger'
    default: return 'info'
  }
}

// 获取级别名称
const getLevelName = (level) => {
  switch (level) {
    case 'entry': return '入门级'
    case 'work': return '进阶级'
    case 'pro': return '专家级'
    default: return level
  }
}

// 获取级别颜色
const getLevelColor = (level) => {
  switch (level) {
    case 'entry': return '#67C23A'
    case 'work': return '#409EFF'
    case 'pro': return '#9254DE'
    default: return '#409EFF'
  }
}

// 获取正确率颜色
const getAccuracyColor = (accuracy) => {
  if (accuracy >= 80) return '#67C23A'
  if (accuracy >= 60) return '#E6A23C'
  return '#F56C6C'
}

// 获取活动类型
const getActivityType = (isCorrect) => {
  if (isCorrect === true) return 'success'
  if (isCorrect === false) return 'danger'
  return 'info'
}

// 获取活动状态文本
const getActivityStatusText = (isCorrect) => {
  if (isCorrect === true) return '正确'
  if (isCorrect === false) return '错误'
  return '已作答'
}

// 获取活动状态类
const getActivityStatusClass = (isCorrect) => {
  if (isCorrect === true) return 'status-correct'
  if (isCorrect === false) return 'status-wrong'
  return 'status-answered'
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-row {
  margin-bottom: 30px;
}

.level-progress-row {
  margin-bottom: 30px;
}

.level-card {
  margin-bottom: 20px;
}

.level-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.level-percentage {
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.activity-card {
  margin-top: 20px;
}

.activity-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.activity-answer {
  margin-left: 20px;
}

.activity-status {
  margin-left: 20px;
  font-weight: bold;
}

.status-correct {
  color: #67C23A;
}

.status-wrong {
  color: #F56C6C;
}

.status-answered {
  color: #409EFF;
}

.empty-activity {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}
</style>
