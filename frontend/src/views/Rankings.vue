<template>
  <div class="rankings-container">
    <el-card class="rankings-card">
      <template #header>
        <div class="card-header">
          <span>排行榜</span>
        </div>
      </template>
      
      <!-- 排行榜类型切换 -->
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <!-- 综合榜 -->
        <el-tab-pane label="综合榜" name="overall">
          <div class="ranking-content">
            <el-table :data="rankingsData" style="width: 100%">
              <el-table-column prop="rank" label="排名" width="80">
                <template #default="scope">
                  <el-badge v-if="scope.row.rank <= 3" :value="scope.row.rank" :type="getRankingBadgeType(scope.row.rank)" />
                  <span v-else>{{ scope.row.rank }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="nickname" label="昵称" width="180" />
              <el-table-column prop="total_score" label="得分" width="100" />
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="text" @click="showUserDetails(scope.row)">查看详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="rankingsData.length === 0" class="empty-rankings">
              暂无排行数据
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 级别榜 -->
        <el-tab-pane label="级别榜" name="level">
          <div class="ranking-filters">
            <el-form-item label="级别">
              <el-radio-group v-model="levelFilter" @change="handleLevelFilterChange">
                <el-radio label="entry">入门级</el-radio>
                <el-radio label="work">进阶级</el-radio>
                <el-radio label="pro">专家级</el-radio>
              </el-radio-group>
            </el-form-item>
          </div>
          <div class="ranking-content">
            <el-table :data="rankingsData" style="width: 100%">
              <el-table-column prop="rank" label="排名" width="80">
                <template #default="scope">
                  <el-badge v-if="scope.row.rank <= 3" :value="scope.row.rank" :type="getRankingBadgeType(scope.row.rank)" />
                  <span v-else>{{ scope.row.rank }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="nickname" label="昵称" width="180" />
              <el-table-column prop="total_score" label="得分" width="100" />
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="text" @click="showUserDetails(scope.row)">查看详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="rankingsData.length === 0" class="empty-rankings">
              暂无排行数据
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 科目榜 -->
        <el-tab-pane label="科目榜" name="subject">
          <div class="ranking-filters">
            <el-form-item label="科目">
              <el-select v-model="subjectFilter" placeholder="请选择科目" @change="handleSubjectFilterChange">
                <el-option label="语言" value="2" />
                <el-option label="规范" value="3" />
                <el-option label="设计" value="4" />
              </el-select>
            </el-form-item>
          </div>
          <div class="ranking-content">
            <el-table :data="rankingsData" style="width: 100%">
              <el-table-column prop="rank" label="排名" width="80">
                <template #default="scope">
                  <el-badge v-if="scope.row.rank <= 3" :value="scope.row.rank" :type="getRankingBadgeType(scope.row.rank)" />
                  <span v-else>{{ scope.row.rank }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="nickname" label="昵称" width="180" />
              <el-table-column prop="total_score" label="得分" width="100" />
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="text" @click="showUserDetails(scope.row)">查看详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="rankingsData.length === 0" class="empty-rankings">
              暂无排行数据
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <!-- 用户详情对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="`用户详情 - ${selectedUser.nickname || ''}`"
        width="60%"
      >
        <div v-if="selectedUser" class="user-details">
          <el-form :model="selectedUser" label-width="80px">
            <el-form-item label="昵称">
              <el-input v-model="selectedUser.nickname" disabled />
            </el-form-item>
            <el-form-item label="IP地址">
              <el-input v-model="selectedUser.user_ip" disabled />
            </el-form-item>
            <el-form-item label="得分">
              <el-input v-model="selectedUser.total_score" disabled />
            </el-form-item>
          </el-form>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

// 状态
const activeTab = ref('overall')
const levelFilter = ref('entry')
const subjectFilter = ref('2')
const rankingsData = ref([])
const selectedUser = ref({})
const dialogVisible = ref(false)

// 获取排行榜数据
const getRankings = async () => {
  try {
    let params = { type: activeTab.value }
    
    if (activeTab.value === 'level') {
      params.level = levelFilter.value
    } else if (activeTab.value === 'subject') {
      params.subject = subjectFilter.value
    }
    
    const data = await api.getRankings(params)
    rankingsData.value = data.rankings
  } catch (error) {
    console.error('Failed to get rankings:', error)
    ElMessage.error('获取排行榜数据失败')
  }
}

// 处理标签页切换
const handleTabChange = () => {
  getRankings()
}

// 处理级别筛选变化
const handleLevelFilterChange = () => {
  getRankings()
}

// 处理科目筛选变化
const handleSubjectFilterChange = () => {
  getRankings()
}

// 查看用户详情
const showUserDetails = (user) => {
  selectedUser.value = user
  dialogVisible.value = true
}

// 获取排名徽章类型
const getRankingBadgeType = (rank) => {
  switch (rank) {
    case 1: return 'danger'
    case 2: return 'warning'
    case 3: return 'success'
    default: return 'info'
  }
}

// 初始化
onMounted(() => {
  getRankings()
})
</script>

<style scoped>
.rankings-container {
  padding: 20px;
}

.rankings-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ranking-filters {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.ranking-content {
  min-height: 400px;
}

.empty-rankings {
  text-align: center;
  padding: 40px 0;
  color: #909399;
}

.user-details {
  padding: 20px 0;
}
</style>
