import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('Response error:', error)
    return Promise.reject(error)
  }
)

// API接口定义
export default {
  // 仪表盘
  getDashboard: () => api.get('/dashboard'),
  
  // 题库
  getQuestions: (params) => api.get('/questions', { params }),
  
  // 考试
  startExam: (data) => api.post('/exam/start', data),
  saveAnswer: (sessionId, data) => api.post(`/exam/${sessionId}/answer`, data),
  submitExam: (sessionId) => api.post(`/exam/${sessionId}/submit`),
  
  // 错题本
  getWrongBook: (params) => api.get('/wrongbook', { params }),
  eliminateWrongQuestion: (wrongId) => api.post(`/wrongbook/${wrongId}/eliminate`),
  
  // 排行榜
  getRankings: (params) => api.get('/rankings', { params }),
  
  // 管理端
  importQuestions: (formData) => api.post('/admin/questions/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  migrateUserData: (data) => api.post('/admin/migrate', data)
}
