<template>
  <div class="question-bank-container">
    <el-card class="question-bank-card">
      <template #header>
        <div class="card-header">
          <span>题库</span>
        </div>
      </template>
      
      <!-- 筛选区 -->
      <div class="filter-section">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="24" :md="12" :lg="8">
            <el-form-item label="级别-科目">
              <el-cascader
                v-model="cascaderValue"
                :options="levelSubjectOptions"
                :props="cascaderProps"
                placeholder="请选择级别和科目"
                @change="handleCascaderChange"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="12" :lg="8">
            <el-form-item label="题型">
              <el-select v-model="typeFilter" placeholder="请选择题型" @change="handleFilterChange">
                <el-option label="全部" value="" />
                <el-option label="单选题" value="single" />
                <el-option label="多选题" value="multiple" />
                <el-option label="判断题" value="judge" />
                <el-option label="主观题" value="subjective" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="24" :lg="8" class="filter-actions">
            <el-button type="primary" @click="resetFilters">重置筛选</el-button>
            <el-button @click="refreshQuestions">刷新</el-button>
          </el-col>
        </el-row>
      </div>
      
      <!-- 列表 -->
      <el-table
        :data="questionsData"
        style="width: 100%"
        @row-click="handleRowClick"
      >
        <el-table-column prop="id" label="题号" width="180">
          <template #default="scope">
            <el-tag :type="getLevelType(scope.row.level)">{{ scope.row.id }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="题型" width="100">
          <template #default="scope">
            <el-tag size="small">{{ getTypeName(scope.row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="题干">
          <template #default="scope">
            <div class="question-content">{{ scope.row.content }}</div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalQuestions"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
      
      <!-- 详情对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="`题目详情 - ${selectedQuestion.id || ''}`"
        width="80%"
      >
        <div v-if="selectedQuestion" class="question-detail">
          <div class="detail-item">
            <span class="detail-label">级别：</span>
            <el-tag :type="getLevelType(selectedQuestion.level)">{{ getLevelName(selectedQuestion.level) }}</el-tag>
          </div>
          <div class="detail-item">
            <span class="detail-label">科目：</span>
            <span>{{ getSubjectName(selectedQuestion.subject) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">题型：</span>
            <el-tag size="small">{{ getTypeName(selectedQuestion.type) }}</el-tag>
          </div>
          <div class="detail-item">
            <span class="detail-label">题干：</span>
            <div class="detail-content">{{ selectedQuestion.content }}</div>
          </div>
          <div v-if="selectedQuestion.options" class="detail-item">
            <span class="detail-label">选项：</span>
            <div class="options-list">
              <div v-for="(option, key) in selectedQuestion.options" :key="key" class="option-item">
                {{ key }}. {{ option }}
              </div>
            </div>
          </div>
          <div class="detail-item">
            <span class="detail-label">答案：</span>
            <span class="answer">{{ selectedQuestion.answer }}</span>
          </div>
          <div v-if="selectedQuestion.explanation" class="detail-item">
            <span class="detail-label">解析：</span>
            <div class="detail-content">{{ selectedQuestion.explanation }}</div>
          </div>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

// 筛选条件
const cascaderValue = ref([])
const typeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// 数据
const questionsData = ref([])
const totalQuestions = ref(0)
const selectedQuestion = ref({})
const dialogVisible = ref(false)

// 级联选择器配置
const levelSubjectOptions = ref([
  {
    value: 'entry',
    label: '入门级',
    children: [
      { value: 1, label: '算法' }
    ]
  },
  {
    value: 'work',
    label: '进阶级',
    children: [
      { value: 1, label: '算法' },
      { value: 2, label: '语言' },
      { value: 3, label: '规范' }
    ]
  },
  {
    value: 'pro',
    label: '专家级',
    children: [
      { value: 1, label: '算法' },
      { value: 2, label: '语言' },
      { value: 3, label: '规范' },
      { value: 4, label: '设计' }
    ]
  }
])

const cascaderProps = {
  value: 'value',
  label: 'label',
  children: 'children'
}

// 计算筛选参数
const filterParams = computed(() => {
  const params = {
    page: currentPage.value,
    page_size: pageSize.value
  }
  
  // 级别和科目
  if (cascaderValue.value.length === 2) {
    params.level = cascaderValue.value[0]
    params.subject = cascaderValue.value[1]
  }
  
  // 题型
  if (typeFilter.value) {
    params.type = typeFilter.value
  }
  
  return params
})

// 获取题目列表
const getQuestions = async () => {
  try {
    const data = await api.getQuestions(filterParams.value)
    questionsData.value = data.questions
    totalQuestions.value = data.total
  } catch (error) {
    console.error('Failed to get questions:', error)
  }
}

// 处理级联选择器变化
const handleCascaderChange = () => {
  currentPage.value = 1
  getQuestions()
}

// 处理筛选条件变化
const handleFilterChange = () => {
  currentPage.value = 1
  getQuestions()
}

// 处理分页变化
const handleSizeChange = (size) => {
  pageSize.value = size
  getQuestions()
}

const handleCurrentChange = (current) => {
  currentPage.value = current
  getQuestions()
}

// 重置筛选
const resetFilters = () => {
  cascaderValue.value = []
  typeFilter.value = ''
  currentPage.value = 1
  getQuestions()
}

// 刷新题目列表
const refreshQuestions = () => {
  getQuestions()
}

// 处理行点击，查看详情
const handleRowClick = (row) => {
  selectedQuestion.value = row
  dialogVisible.value = true
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

// 获取科目名称
const getSubjectName = (subject) => {
  const subjectMap = {
    1: '算法',
    2: '语言',
    3: '规范',
    4: '设计'
  }
  return subjectMap[subject] || subject
}

// 获取题型名称
const getTypeName = (type) => {
  const typeMap = {
    single: '单选题',
    multiple: '多选题',
    judge: '判断题',
    subjective: '主观题'
  }
  return typeMap[type] || type
}

// 获取状态标签类型
const getStatusType = (status) => {
  switch (status) {
    case 'correct': return 'success'
    case 'wrong': return 'danger'
    case 'answered': return 'warning'
    default: return 'info'
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'correct': return '正确'
    case 'wrong': return '错误'
    case 'answered': return '已答'
    default: return '未做'
  }
}

// 初始化
onMounted(() => {
  getQuestions()
})
</script>

<style scoped>
.question-bank-container {
  padding: 20px;
}

.question-bank-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.question-content {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pagination-section {
  margin-top: 20px;
  text-align: right;
}

.question-detail {
  padding: 10px 0;
}

.detail-item {
  margin-bottom: 15px;
}

.detail-label {
  font-weight: bold;
  margin-right: 10px;
}

.detail-content {
  margin-top: 5px;
  line-height: 1.5;
}

.options-list {
  margin-top: 5px;
}

.option-item {
  margin-bottom: 5px;
}

.answer {
  font-weight: bold;
  color: #67C23A;
}
</style>
