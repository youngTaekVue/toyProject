import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue' // AppLayout 임포트
import AppDashboard from '@/views/AppDashboard.vue'
import AnalyticsView from '@/views/AnalyticsView.vue'
import BillingView from '@/views/BillingView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SettingsView from '@/views/SettingsView.vue'
import Subitem1View from '@/views/accountBook/Subitem1View.vue'
import Subitem2View from '@/views/accountBook/Subitem2View.vue'
import HealthDashboard from '@/views/health/HealthDashboard.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
    component: AppLayout, // AppLayout을 최상위 레이아웃 컴포넌트로 사용
    children: [ // 모든 실제 페이지 뷰를 AppLayout의 자식으로 정의
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
        path: '/dropdown/subitem1',
        name: 'Subitem1',
        component: Subitem1View,
        meta: { pageTitle: 'Sub-item 1', icon: 'mdi-circle-small', breadcrumb: 'Pages / Dropdown / Sub-item 1' }
      },
      {
        path: '/dropdown/subitem2',
        name: 'Subitem2',
        component: Subitem2View,
        meta: { pageTitle: 'Sub-item 2', icon: 'mdi-circle-small', breadcrumb: 'Pages / Dropdown / Sub-item 2' }
      },
      {
        path: '/health/healthDashboard',
        name: 'healthDashboard',
        component: HealthDashboard,
        meta: { pageTitle: 'Sub-item 1', icon: 'mdi-circle-small', breadcrumb: 'Pages / Dropdown / Sub-item 1' }
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
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router