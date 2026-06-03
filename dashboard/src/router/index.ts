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
    meta: { pageTitle: 'Dashboard', icon: 'mdi-view-dashboard', breadcrumb: 'Pages / Dashboard' }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: AnalyticsView,
    meta: { pageTitle: 'Analytics', icon: 'mdi-chart-bar', breadcrumb: 'Pages / Analytics' }
  },
  {
    path: '/billing',
    name: 'Billing',
    component: BillingView,
    meta: { pageTitle: 'Billing', icon: 'mdi-credit-card', breadcrumb: 'Pages / Billing' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { pageTitle: 'Profile', icon: 'mdi-account', breadcrumb: 'Pages / Profile' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { pageTitle: 'Settings', icon: 'mdi-cog', breadcrumb: 'Pages / Settings' }
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
