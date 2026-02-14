import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/Dashboard.vue'),
      meta: { title: '仪表盘' }
    },
    {
      path: '/question-bank',
      name: 'QuestionBank',
      component: () => import('../views/QuestionBank.vue'),
      meta: { title: '题库' }
    },
    {
      path: '/exam',
      name: 'Exam',
      component: () => import('../views/Exam.vue'),
      meta: { title: '考试' }
    },
    {
      path: '/wrong-book',
      name: 'WrongBook',
      component: () => import('../views/WrongBook.vue'),
      meta: { title: '错题本' }
    },
    {
      path: '/rankings',
      name: 'Rankings',
      component: () => import('../views/Rankings.vue'),
      meta: { title: '排行榜' }
    }
  ]
})

// 路由标题设置
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '在线刷题系统'} - 在线刷题系统`
  next()
})

export default router
