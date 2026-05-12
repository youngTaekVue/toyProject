import { createRouter, createWebHistory } from 'vue-router'
import AppDashboard from '@/views/AppDashboard.vue'
import AnalyticsView from '@/views/AnalyticsView.vue'
import BillingView from '@/views/BillingView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SettingsView from '@/views/SettingsView.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard', // 기본 경로를 대시보드로 리다이렉트
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: AppDashboard,
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: AnalyticsView,
  },
  {
    path: '/billing',
    name: 'Billing',
    component: BillingView,
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
