import { createRouter, createWebHistory } from 'vue-router'
import BasicLayout from '@/layout/BasicLayout.vue'

const routes = [
  {
    path: '/',
    component: BasicLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard/Overview.vue')
      },
      {
        path: 'file-upload',
        name: 'FileUpload',
        component: () => import('@/views/FileManagement/FileUpload.vue')
      }
    ]
  }
]

const router = createRouter({
  // 移除 BASE_URL
  history: createWebHistory(),
  routes
})

export default router