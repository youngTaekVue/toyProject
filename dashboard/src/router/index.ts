import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue' // AppLayout 컴포넌트 import

import HomeDashboard from '@/views/HomeDashboard.vue'
import DailyInfoWeather from '@/views/daily-info/DailyInfoWeather.vue'
import DailyInfoRealEstate from '@/views/daily-info/DailyInfoRealEstate.vue'
import AppInfoOverview from '@/views/app-info/AppInfoOverview.vue'
import AppInfoUserAnalytics from '@/views/app-info/AppInfoUserAnalytics.vue'
import AppInfoDownloadsTraffic from '@/views/app-info/AppInfoDownloadsTraffic.vue'
import AppInfoPerformance from '@/views/app-info/AppInfoPerformance.vue'

// Accountbook Views
import AccountbookDashboard from '@/views/accountbook/Dashboard.vue'
import AccountbookTransactions from '@/views/accountbook/Transactions.vue'
import AccountbookSpending from '@/views/accountbook/Spending.vue'
import AccountbookFinancialStatus from '@/views/accountbook/FinancialStatus.vue'
import AccountbookSettings from '@/views/accountbook/Settings.vue'
import AccountbookLogs from '@/views/accountbook/Logs.vue'

// 기존 라우트들
import AnalyticsView from '@/views/AnalyticsView.vue'
import BillingView from '@/views/BillingView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SettingsView from '@/views/SettingsView.vue'

const routes = [
  {
    path: '/',
    component: AppLayout, // 모든 페이지를 감싸는 레이아웃 컴포넌트
    redirect: '/home', // 기본 경로를 홈 대시보드로 리다이렉트
    children: [
      {
        path: 'home',
        name: 'Home',
        component: HomeDashboard,
        meta: { pageTitle: '대시보드', breadcrumb: '홈' }, // AppLayout에 전달할 메타 정보
      },
      {
        path: 'daily-info/weather',
        name: 'DailyInfoWeather',
        component: DailyInfoWeather,
        meta: { pageTitle: '오늘의 날씨', breadcrumb: '일일 정보 / 날씨' },
      },
      {
        path: 'daily-info/real-estate',
        name: 'DailyInfoRealEstate',
        component: DailyInfoRealEstate,
        meta: { pageTitle: '부동산 정보', breadcrumb: '일일 정보 / 부동산' },
      },
      {
        path: 'app-info/overview',
        name: 'AppInfoOverview',
        component: AppInfoOverview,
        meta: { pageTitle: '앱 개요', breadcrumb: '앱 정보 / 개요' },
      },
      {
        path: 'app-info/user-analytics',
        name: 'AppInfoUserAnalytics',
        component: AppInfoUserAnalytics,
        meta: { pageTitle: '사용자 분석', breadcrumb: '앱 정보 / 사용자 분석' },
      },
      {
        path: 'app-info/downloads-traffic',
        name: 'AppInfoDownloadsTraffic',
        component: AppInfoDownloadsTraffic,
        meta: { pageTitle: '다운로드 및 트래픽', breadcrumb: '앱 정보 / 다운로드' },
      },
      {
        path: 'app-info/performance',
        name: 'AppInfoPerformance',
        component: AppInfoPerformance,
        meta: { pageTitle: '성능', breadcrumb: '앱 정보 / 성능' },
      },
      // Accountbook Routes
      {
        path: 'accountbook', // 부모 라우트의 자식이므로 '/' 없이 경로 지정
        name: 'Accountbook',
        redirect: '/accountbook/dashboard',
        meta: { pageTitle: '가계부', breadcrumb: '가계부', icon: 'mdi-book-open-variant' }, // 메타 정보 추가 (메뉴 생성에 활용)
        children: [
          {
            path: 'dashboard',
            name: 'AccountbookDashboard',
            component: AccountbookDashboard,
            meta: { pageTitle: '가계부 대시보드', breadcrumb: '가계부 / 대시보드' },
          },
          {
            path: 'transactions',
            name: 'AccountbookTransactions',
            component: AccountbookTransactions,
            meta: { pageTitle: '가계부 내역', breadcrumb: '가계부 / 내역' },
          },
          {
            path: 'spending',
            name: 'AccountbookSpending',
            component: AccountbookSpending,
            meta: { pageTitle: '월별 지출 관리', breadcrumb: '가계부 / 지출' },
          },
          {
            path: 'financial-status',
            name: 'AccountbookFinancialStatus',
            component: AccountbookFinancialStatus,
            meta: { pageTitle: '자산 조회', breadcrumb: '가계부 / 자산' },
          },
          {
            path: 'settings',
            name: 'AccountbookSettings',
            component: AccountbookSettings,
            meta: { pageTitle: '가계부 시스템 설정', breadcrumb: '가계부 / 설정' },
          },
          {
            path: 'logs',
            name: 'AccountbookLogs',
            component: AccountbookLogs,
            meta: { pageTitle: '가계부 로그 조회', breadcrumb: '가계부 / 로그' },
          },
        ],
      },
      // 기존 라우트 유지 (필요에 따라 조정)
      {
        path: 'analytics',
        name: 'Analytics',
        component: AnalyticsView,
        meta: { pageTitle: '분석', breadcrumb: '분석' },
      },
      {
        path: 'billing',
        name: 'Billing',
        component: BillingView,
        meta: { pageTitle: '결제', breadcrumb: '결제' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: ProfileView,
        meta: { pageTitle: '프로필', breadcrumb: '프로필' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: SettingsView,
        meta: { pageTitle: '설정', breadcrumb: '설정' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 라우트 변경 시 AppLayout의 props를 업데이트하기 위한 네비게이션 가드 추가
router.beforeEach((to, from, next) => {
  // AppLayout이 pageTitle과 breadcrumb prop을 받도록 설정되어 있다면
  // 여기서 meta 정보를 활용하여 AppLayout의 데이터를 업데이트할 수 있습니다.
  // 하지만 AppLayout은 현재 props를 통해 직접 데이터를 받는 구조이므로,
  // 이 부분은 AppLayout 컴포넌트 자체에서 $route.meta를 watch하거나
  // 상위 컴포넌트에서 props를 동적으로 바인딩해야 합니다.
  // 현재 AppLayout은 slot으로 페이지 내용을 받으므로,
  // 각 페이지 컴포넌트에서 AppLayout을 직접 사용하는 방식으로 변경하거나
  // AppLayout의 props를 동적으로 업데이트하는 로직이 필요합니다.

  // 임시로 AppLayout의 props를 업데이트하는 로직은 생략하고,
  // AppLayout에서 $route.meta를 직접 참조하도록 가정합니다.
  next();
});


export default router