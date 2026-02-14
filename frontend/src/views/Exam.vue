<template>
  <div class="exam-container">
    <!-- 开始考试表单 -->
    <el-card v-if="!examStarted" class="start-exam-card">
      <template #header>
        <div class="card-header">
          <span>开始考试</span>
        </div>
      </template>
      <el-form :model="examForm" :rules="examRules" ref="examFormRef" label-width="80px">
        <el-form-item label="级别" prop="level">
          <el-select v-model="examForm.level" placeholder="请选择级别">
            <el-option label="入门级" value="entry" />
            <el-option label="进阶级" value="work" />
            <el-option label="专家级" value="pro" />
          </el-select>
        </el-form-item>
        <el-form-item label="科目" prop="subjects">
          <el-select
            v-model="examForm.subjects"
            multiple
            placeholder="请选择科目"
            @change="handleSubjectsChange"
          >
            <el-option
              v-for="subject in availableSubjects"
              :key="subject.value"
              :label="subject.label"
              :value="subject.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="题量" prop="question_count">
          <el-select v-model="examForm.question_count" placeholder="请选题量">
            <el-option label="10题" value="10" />
            <el-option label="30题" value="30" />
            <el-option label="50题" value="50" />
            <el-option label="100题" value="100" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleStartExam">开始考试</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 考试界面 -->
    <el-container v-else class="exam-interface">
      <!-- 左侧边栏 -->
      <el-aside width="200px" class="exam-aside">
        <!-- 倒计时 -->
        <div class="countdown-section">
          <el-statistic
            :value="remainingTime"
            title="剩余时间"
            formatter="formatCountdown"
          />
        </div>
        
        <!-- 题号导航 -->
        <div class="question-nav">
          <h3>题号导航</h3>
          <el-button-group class="question-buttons">
            <el-button
              v-for="(question, index) in examQuestions"
              :key="question.id"
              :type="getQuestionButtonType(index)"
              :plain="currentQuestionIndex === index"
              :icon="getQuestionButtonIcon(index)"
              @click="goToQuestion(index)"
            >
              {{ index + 1 }}
            </el-button>
          </el-button-group>
        </div>
      </el-aside>
      
      <!-- 右侧主内容 -->
      <el-main class="exam-main">
        <div v-if="currentQuestion" class="question-section">
          <h2>第 {{ currentQuestionIndex + 1 }} 题 / 共 {{ examQuestions.length }} 题</h2>
          <el-card class="current-question-card">
            <div class="question-content">
              <h3>{{ currentQuestion.content }}</h3>
              
              <!-- 单选题 -->
              <div v-if="currentQuestion.type === 'single'" class="answer-section">
                <el-radio-group v-model="userAnswers[currentQuestionIndex]" @change="handleAnswerChange">
                  <el-radio
                    v-for="(option, key) in currentQuestion.options"
                    :key="key"
                    :label="key"
                    class="option-item"
                  >
                    {{ key }}. {{ option }}
                  </el-radio>
                </el-radio-group>
              </div>
              
              <!-- 多选题 -->
              <div v-else-if="currentQuestion.type === 'multiple'" class="answer-section">
                <el-checkbox-group v-model="userAnswers[currentQuestionIndex]" @change="handleAnswerChange">
                  <el-checkbox
                    v-for="(option, key) in currentQuestion.options"
                    :key="key"
                    :label="key"
                    class="option-item"
                  >
                    {{ key }}. {{ option }}
                  </el-checkbox>
                </el-checkbox-group>
              </div>
              
              <!-- 判断题 -->
              <div v-else-if="currentQuestion.type === 'judge'" class="answer-section">
                <el-radio-group v-model="userAnswers[currentQuestionIndex]" @change="handleAnswerChange">
                  <el-radio label="正确" class="option-item" />
                  <el-radio label="错误" class="option-item" />
                </el-radio-group>
              </div>
              
              <!-- 主观题 -->
              <div v-else-if="currentQuestion.type === 'subjective'" class="answer-section">
                <el-input
                  v-model="userAnswers[currentQuestionIndex]"
                  type="textarea"
                  :rows="10"
                  placeholder="请输入答案"
                  @input="handleAnswerChange"
                />
              </div>
            </div>
          </el-card>
          
          <!-- 操作栏 -->
          <div class="action-section">
            <el-button @click="markUncertain">标记不确定</el-button>
            <el-button @click="prevQuestion">上一题</el-button>
            <el-button @click="nextQuestion">下一题</el-button>
            <el-button type="danger" @click="confirmSubmit">交卷</el-button>
          </div>
        </div>
      </el-main>
    </el-container>
    
    <!-- 交卷确认对话框 -->
    <el-dialog
      v-model="submitConfirmVisible"
      title="交卷确认"
      width="500px"
    >
      <el-alert
        type="warning"
        :title="`您还有 ${unansweredCount} 道题未作答，确定要交卷吗？`"
        show-icon
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="submitConfirmVisible = false">取消</el-button>
          <el-button type="danger" @click="handleSubmit">确定交卷</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 考试结果对话框 -->
    <el-dialog
      v-model="resultVisible"
      title="考试结果"
      width="80%"
    >
      <div class="exam-result">
        <el-statistic :value="examResult.total_score" title="总分" />
        <h3>各科目正确率</h3>
        <el-table :data="subjectAccuracyData" style="width: 100%">
          <el-table-column prop="subject" label="科目" />
          <el-table-column prop="accuracy" label="正确率" />
        </el-table>
        <h3 v-if="examResult.wrong_questions.length > 0">错题列表</h3>
        <div v-if="examResult.wrong_questions.length > 0" class="wrong-questions-list">
          <el-card
            v-for="(question, index) in examResult.wrong_questions"
            :key="index"
            class="wrong-question-card"
          >
            <h4>题目：{{ question.question_id }}</h4>
            <p>{{ question.content }}</p>
            <p class="user-answer">你的答案：{{ question.user_answer }}</p>
            <p class="correct-answer">正确答案：{{ question.correct_answer }}</p>
            <p v-if="question.explanation" class="explanation">解析：{{ question.explanation }}</p>
          </el-card>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="resultVisible = false; resetExam">返回</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import api from '../api'

// 考试状态
const examStarted = ref(false)
const examForm = ref({
  level: 'entry',
  subjects: [],
  question_count: 50
})
const examRules = {
  level: [{ required: true, message: '请选择级别', trigger: 'change' }],
  subjects: [{ required: true, message: '请选择至少一个科目', trigger: 'change' }],
  question_count: [{ required: true, message: '请选题量', trigger: 'change' }]
}
const examFormRef = ref(null)

// 可用科目（根据级别动态变化）
const availableSubjects = ref([
  { label: '算法', value: 1 },
  { label: '语言', value: 2 },
  { label: '规范', value: 3 },
  { label: '设计', value: 4 }
])

// 考试数据
const examQuestions = ref([])
const userAnswers = ref([])
const uncertainQuestions = ref([])
const currentQuestionIndex = ref(0)
const sessionId = ref('')
const timeLimit = ref(0)
const remainingTime = ref(0)
const timer = ref(null)

// 交卷和结果
const submitConfirmVisible = ref(false)
const resultVisible = ref(false)
const examResult = ref({
  total_score: 0,
  subject_accuracy: {},
  wrong_questions: []
})

// 处理科目变化（根据级别过滤可用科目）
const handleSubjectsChange = () => {
  // 这里可以根据级别的变化过滤可用科目
  // 简化处理，保持所有科目可用
}

// 开始考试
const handleStartExam = async () => {
  if (!examFormRef.value) return
  
  await examFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const response = await api.startExam({
          level: examForm.value.level,
          subjects: examForm.value.subjects,
          question_count: parseInt(examForm.value.question_count)
        })
        
        sessionId.value = response.session_id
        examQuestions.value = response.questions
        timeLimit.value = response.time_limit
        remainingTime.value = response.time_limit
        
        // 初始化用户答案
        userAnswers.value = new Array(examQuestions.value.length).fill('')
        uncertainQuestions.value = new Array(examQuestions.value.length).fill(false)
        
        // 开始倒计时
        startTimer()
        
        examStarted.value = true
      } catch (error) {
        ElMessage.error('开始考试失败，请重试')
        console.error('Failed to start exam:', error)
      }
    }
  })
}

// 开始倒计时
const startTimer = () => {
  timer.value = setInterval(() => {
    remainingTime.value--
    if (remainingTime.value <= 0) {
      clearInterval(timer.value)
      // 时间到，自动交卷
      handleSubmit()
    }
  }, 1000)
}

// 格式化倒计时
const formatCountdown = (value) => {
  const minutes = Math.floor(value / 60)
  const seconds = value % 60
  return `${minutes}分${seconds}秒`
}

// 获取当前题目
const currentQuestion = computed(() => {
  return examQuestions.value[currentQuestionIndex.value]
})

// 获取题目按钮类型
const getQuestionButtonType = (index) => {
  if (userAnswers.value[index]) {
    return 'success'
  }
  if (uncertainQuestions.value[index]) {
    return 'warning'
  }
  return 'default'
}

// 获取题目按钮图标
const getQuestionButtonIcon = (index) => {
  if (uncertainQuestions.value[index]) {
    return 'Warning'
  }
  return ''
}

// 跳转到指定题目
const goToQuestion = (index) => {
  currentQuestionIndex.value = index
}

// 上一题
const prevQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

// 下一题
const nextQuestion = () => {
  if (currentQuestionIndex.value < examQuestions.value.length - 1) {
    currentQuestionIndex.value++
  }
}

// 标记不确定
const markUncertain = () => {
  uncertainQuestions.value[currentQuestionIndex.value] = !uncertainQuestions.value[currentQuestionIndex.value]
}

// 处理答案变化
const handleAnswerChange = () => {
  // 自动保存答案
  saveAnswer()
}

// 保存答案
const saveAnswer = async () => {
  if (!sessionId.value || !currentQuestion) return
  
  try {
    await api.saveAnswer(sessionId.value, {
      question_id: currentQuestion.value.id,
      user_answer: userAnswers.value[currentQuestionIndex.value]
    })
  } catch (error) {
    console.error('Failed to save answer:', error)
  }
}

// 未答题目数量
const unansweredCount = computed(() => {
  return userAnswers.value.filter(answer => !answer).length
})

// 确认交卷
const confirmSubmit = () => {
  submitConfirmVisible.value = true
}

// 交卷
const handleSubmit = async () => {
  if (!sessionId.value) return
  
  try {
    const response = await api.submitExam(sessionId.value)
    examResult.value = response
    resultVisible.value = true
    
    // 清除定时器
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }
  } catch (error) {
    ElMessage.error('交卷失败，请重试')
    console.error('Failed to submit exam:', error)
  } finally {
    submitConfirmVisible.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (examFormRef.value) {
    examFormRef.value.resetFields()
  }
}

// 重置考试
const resetExam = () => {
  examStarted.value = false
  examQuestions.value = []
  userAnswers.value = []
  uncertainQuestions.value = []
  currentQuestionIndex.value = 0
  sessionId.value = ''
  timeLimit.value = 0
  remainingTime.value = 0
  if (timer.value) {
    clearInterval(timer.value)
    timer.value = null
  }
}

// 科目正确率数据（用于表格展示）
const subjectAccuracyData = computed(() => {
  const data = []
  for (const [subject, accuracy] of Object.entries(examResult.value.subject_accuracy)) {
    data.push({
      subject: getSubjectName(subject),
      accuracy: `${accuracy}%`
    })
  }
  return data
})

// 获取科目名称
const getSubjectName = (subject) => {
  const subjectMap = {
    '1': '算法',
    '2': '语言',
    '3': '规范',
    '4': '设计'
  }
  return subjectMap[subject] || subject
}

// 清理定时器
onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }
})
</script>

<style scoped>
.exam-container {
  padding: 20px;
}

.start-exam-card {
  max-width: 600px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.exam-interface {
  height: calc(100vh - 120px);
  border: 1px solid #eaeaea;
  border-radius: 4px;
}

.exam-aside {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

.countdown-section {
  margin-bottom: 30px;
  text-align: center;
}

.question-nav {
  margin-top: 30px;
}

.question-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 10px;
}

.question-buttons .el-button {
  width: 40px;
  height: 40px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.exam-main {
  padding: 20px;
  overflow-y: auto;
}

.question-section {
  max-width: 800px;
  margin: 0 auto;
}

.current-question-card {
  margin: 20px 0;
}

.question-content h3 {
  margin-bottom: 20px;
  line-height: 1.5;
}

.answer-section {
  margin-top: 20px;
}

.option-item {
  margin-bottom: 10px;
  display: block;
}

.action-section {
  margin-top: 30px;
  display: flex;
  justify-content: space-between;
}

.exam-result {
  padding: 20px 0;
}

.exam-result h3 {
  margin: 20px 0 10px 0;
}

.wrong-questions-list {
  margin-top: 20px;
}

.wrong-question-card {
  margin-bottom: 15px;
}

.user-answer {
  color: #F56C6C;
}

.correct-answer {
  color: #67C23A;
}

.explanation {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.dialog-footer {
  text-align: center;
  width: 100%;
}
</style>
