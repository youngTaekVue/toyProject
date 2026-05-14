import { createRouter, createWebHistory } from 'vue-router'
import HomeDashboard from '@/views/HomeDashboard.vue'
import DailyInfoWeather from '@/views/daily-info/DailyInfoWeather.vue'
import DailyInfoRealEstate from '@/views/daily-info/DailyInfoRealEstate.vue'
import AppInfoOverview from '@/views/app-info/AppInfoOverview.vue'
import AppInfoUserAnalytics from '@/views/app-info/AppInfoUserAnalytics.vue'
import AppInfoDownloadsTraffic from '@/views/app-info/AppInfoDownloadsTraffic.vue'
import AppInfoPerformance from '@/views/app-info/AppInfoPerformance.vue'

// 기존 라우트들
import AnalyticsView from '@/views/AnalyticsView.vue'
import BillingView from '@/views/BillingView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SettingsView from '@/views/SettingsView.vue'

const routes = [
  {
    path: '/',
    redirect: '/home', // 기본 경로를 홈 대시보드로 리다이렉트
  },
  {
    path: '/home',
    name: 'Home',
    component: HomeDashboard,
  },
  {
    path: '/daily-info/weather',
    name: 'DailyInfoWeather',
    component: DailyInfoWeather,
  },
  {
    path: '/daily-info/real-estate',
    name: 'DailyInfoRealEstate',
    component: DailyInfoRealEstate,
  },
  {
    path: '/app-info/overview',
    name: 'AppInfoOverview',
    component: AppInfoOverview,
  },
  {
    path: '/app-info/user-analytics',
    name: 'AppInfoUserAnalytics',
    component: AppInfoUserAnalytics,
  },
  {
    path: '/app-info/downloads-traffic',
    name: 'AppInfoDownloadsTraffic',
    component: AppInfoDownloadsTraffic,
  },
  {
    path: '/app-info/performance',
    name: 'AppInfoPerformance',
    component: AppInfoPerformance,
  },
  // 기존 라우트 유지 (필요에 따라 조정)
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
