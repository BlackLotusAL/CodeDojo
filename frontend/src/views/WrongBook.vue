<template>
  <div class="wrong-book-container">
    <el-card class="wrong-book-card">
      <template #header>
        <div class="card-header">
          <span>错题本</span>
          <el-button @click="exportToMarkdown">导出为Markdown</el-button>
        </div>
      </template>
      
      <!-- 筛选区 -->
      <div class="filter-section">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="24" :md="12" :lg="8">
            <el-form-item label="科目">
              <el-select v-model="subjectFilter" placeholder="请选择科目" @change="handleFilterChange">
                <el-option label="全部" value="" />
                <el-option label="算法" value="1" />
                <el-option label="语言" value="2" />
                <el-option label="规范" value="3" />
                <el-option label="设计" value="4" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="12" :lg="8">
            <el-form-item label="掌握状态">
              <el-select v-model="masteredFilter" placeholder="请选择掌握状态" @change="handleFilterChange">
                <el-option label="全部" value="" />
                <el-option label="已掌握" value="true" />
                <el-option label="未掌握" value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="24" :lg="8" class="filter-actions">
            <el-button type="primary" @click="resetFilters">重置筛选</el-button>
            <el-button @click="refreshWrongBook">刷新</el-button>
          </el-col>
        </el-row>
      </div>
      
      <!-- 错题列表 -->
      <el-table
        :data="filteredWrongQuestions"
        style="width: 100%"
      >
        <el-table-column prop="question_id" label="题号" width="180">
          <template #default="scope">
            <el-tag :type="getLevelType(scope.row.level)">{{ scope.row.question_id }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template #default="scope">
            <el-tag :type="getLevelType(scope.row.level)">{{ getLevelName(scope.row.level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="subject" label="科目" width="100">
          <template #default="scope">
            <span>{{ getSubjectName(scope.row.subject) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="题型" width="100">
          <template #default="scope">
            <el-tag size="small">{{ getTypeName(scope.row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="题干">
          <template #default="scope">
            <div class="question-content">{{ scope.row.content }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="wrong_count" label="错误次数" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.wrong_count >= 3 ? 'danger' : ''">
              {{ scope.row.wrong_count }}
              <span v-if="scope.row.wrong_count >= 3">（难）</span>
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="mastered" label="掌握状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.mastered ? 'success' : 'info'">
              {{ scope.row.mastered ? '已掌握' : '未掌握' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button
              v-if="!scope.row.mastered"
              type="success"
              size="small"
              @click="eliminateWrongQuestion(scope.row.id)"
            >
              消灭
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="showQuestionDetail(scope.row)"
            >
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 详情对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="`错题详情 - ${selectedQuestion.question_id || ''}`"
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
          <div class="detail-item">
            <span class="detail-label">错误次数：</span>
            <span>{{ selectedQuestion.wrong_count }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">掌握状态：</span>
            <el-tag :type="selectedQuestion.mastered ? 'success' : 'info'">
              {{ selectedQuestion.mastered ? '已掌握' : '未掌握' }}
            </el-tag>
          </div>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

// 筛选条件
const subjectFilter = ref('')
const masteredFilter = ref('')

// 数据
const wrongQuestions = ref([])
const selectedQuestion = ref({})
const dialogVisible = ref(false)

// 计算筛选后的错题列表
const filteredWrongQuestions = computed(() => {
  return wrongQuestions.value.filter(question => {
    // 科目筛选
    if (subjectFilter.value && question.subject.toString() !== subjectFilter.value) {
      return false
    }
    
    // 掌握状态筛选
    if (masteredFilter.value && question.mastered.toString() !== masteredFilter.value) {
      return false
    }
    
    return true
  })
})

// 获取错题本数据
const getWrongBook = async () => {
  try {
    const data = await api.getWrongBook()
    wrongQuestions.value = data.wrong_questions
  } catch (error) {
    console.error('Failed to get wrong book:', error)
    ElMessage.error('获取错题本失败')
  }
}

// 处理筛选条件变化
const handleFilterChange = () => {
  // 筛选逻辑在computed中处理
}

// 重置筛选
const resetFilters = () => {
  subjectFilter.value = ''
  masteredFilter.value = ''
}

// 刷新错题本
const refreshWrongBook = () => {
  getWrongBook()
}

// 消灭错题
const eliminateWrongQuestion = async (wrongId) => {
  try {
    await api.eliminateWrongQuestion(wrongId)
    ElMessage.success('错题消灭成功')
    // 刷新错题本
    getWrongBook()
  } catch (error) {
    console.error('Failed to eliminate wrong question:', error)
    ElMessage.error('消灭错题失败')
  }
}

// 查看错题详情
const showQuestionDetail = (question) => {
  selectedQuestion.value = question
  dialogVisible.value = true
}

// 导出为Markdown
const exportToMarkdown = () => {
  if (filteredWrongQuestions.value.length === 0) {
    ElMessage.warning('没有错题可导出')
    return
  }
  
  let markdownContent = '# 错题本\n\n'
  
  filteredWrongQuestions.value.forEach((question, index) => {
    markdownContent += `## 第 ${index + 1} 题\n`
    markdownContent += `- 题号：${question.question_id}\n`
    markdownContent += `- 级别：${getLevelName(question.level)}\n`
    markdownContent += `- 科目：${getSubjectName(question.subject)}\n`
    markdownContent += `- 题型：${getTypeName(question.type)}\n`
    markdownContent += `- 错误次数：${question.wrong_count}\n`
    markdownContent += `- 掌握状态：${question.mastered ? '已掌握' : '未掌握'}\n\n`
    markdownContent += `### 题干\n${question.content}\n\n`
    
    if (question.options) {
      markdownContent += `### 选项\n`
      for (const [key, option] of Object.entries(question.options)) {
        markdownContent += `- ${key}：${option}\n`
      }
      markdownContent += '\n'
    }
    
    markdownContent += `### 答案\n${question.answer}\n\n`
    
    if (question.explanation) {
      markdownContent += `### 解析\n${question.explanation}\n\n`
    }
    
    markdownContent += '---\n\n'
  })
  
  // 创建Blob对象
  const blob = new Blob([markdownContent], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  
  // 创建下载链接
  const link = document.createElement('a')
  link.href = url
  link.download = `错题本_${new Date().toISOString().slice(0, 10)}.md`
  link.click()
  
  // 释放URL对象
  URL.revokeObjectURL(url)
  
  ElMessage.success('导出成功')
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

// 初始化
onMounted(() => {
  getWrongBook()
})
</script>

<style scoped>
.wrong-book-container {
  padding: 20px;
}

.wrong-book-card {
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

.filter-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
