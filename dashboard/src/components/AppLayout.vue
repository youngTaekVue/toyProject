<template>
  <div class="dashboard-container">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div>
        <div class="sidebar-header">
          <div class="logo-icon"><v-icon>mdi-flash</v-icon></div>
          <h2>SOFT UI PRO</h2>
        </div>
        <nav class="sidebar-nav">
          <v-list nav dense>
            <template v-for="item in mainMenuItems" :key="item.path">
              <v-list-group
                v-if="item.children && item.children.length > 0"
                :value="item.path"
                :opened="item.path === '/accountbook' ? true : undefined"
              >
                <template v-slot:activator="{ props }">
                  <v-list-item
                    v-bind="props"
                    :prepend-icon="item.icon"
                    :title="item.title"
                    active-class="active"
                  ></v-list-item>
                </template>
                <v-list-item
                  v-for="child in item.children"
                  :key="child.path"
                  :to="child.path"
                  :prepend-icon="child.icon"
                  :title="child.title"
                  active-class="active"
                ></v-list-item>
              </v-list-group>
              <v-list-item
                v-else
                :to="item.path"
                :prepend-icon="item.icon"
                :title="item.title"
                active-class="active"
              ></v-list-item>
            </template>
          </v-list>
        </nav>
      </div>

      <div class="sidebar-footer">
        <div class="help-box">
          <div class="help-icon"><v-icon>mdi-star</v-icon></div>
          <h3>Upgrade to PRO</h3>
          <p>Check our documentation</p>
          <button class="documentation-btn">GET STARTED</button>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="main-content">
      <header class="main-header">
        <div class="header-title">
          <p class="breadcrumb">{{ route.meta.breadcrumb }}</p>
          <h1>{{ route.meta.pageTitle }}</h1>
        </div>
        <div class="header-actions">
          <div class="search-wrapper">
            <v-icon>mdi-magnify</v-icon>
            <input type="text" placeholder="Type here..." class="neumorphic-input">
          </div>
          <button class="neumorphic-btn accent-btn"><v-icon>mdi-plus</v-icon> NEW POST</button>
          <div class="icon-actions">
            <button class="icon-btn"><v-icon>mdi-bell</v-icon></button>
            <button class="icon-btn"><v-icon>mdi-cog</v-icon></button>
          </div>
        </div>
      </header>

      <!-- Router view for page-specific content -->
      <router-view />

    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'; // useRoute, useRouter 훅 import
import { computed } from 'vue';

const route = useRoute(); // 현재 라우트 객체 가져오기
const router = useRouter(); // 라우터 인스턴스 가져오기

interface MenuItem {
  title: string;
  icon?: string;
  path: string;
  children?: MenuItem[];
}

const mainMenuItems = computed<MenuItem[]>(() => {
  // '/' 경로의 자식 라우트들을 가져옵니다.
  // router.options.routes는 최상위 라우트 배열을 반환합니다.
  // AppLayout이 '/' 경로의 component로 설정되어 있으므로, 그 children을 찾아야 합니다.
  const appLayoutParentRoute = router.options.routes.find(r => r.path === '/');
  const appLayoutRoutes = appLayoutParentRoute?.children || [];

  return appLayoutRoutes
    .filter(r => r.meta && r.meta.pageTitle && !r.redirect) // meta.pageTitle이 있고 redirect가 아닌 라우트만 필터링
    .map(r => {
      // 자식 라우트가 있는 경우 (예: accountbook)
      if (r.children && r.children.length > 0) {
        // 자식 라우트 중 meta.pageTitle이 있는 것만 필터링하고 매핑
        const children = r.children
          .filter(child => child.meta && child.meta.pageTitle)
          .map(child => ({
            title: child.meta.pageTitle as string,
            icon: child.meta.icon as string,
            path: `/${r.path}/${child.path}` // 자식 링크의 전체 경로
          }));

        // 자식 라우트가 하나라도 있으면 그룹으로 처리
        if (children.length > 0) {
          return {
            title: r.meta.pageTitle as string,
            icon: r.meta.icon as string,
            path: `/${r.path}`, // 그룹의 기본 경로 (클릭 시 리다이렉트될 경로)
            children: children
          };
        }
      }
      // 자식 라우트가 없거나, 필터링 후 자식 라우트가 없는 경우 단일 링크로 처리
      return {
        title: r.meta.pageTitle as string,
        icon: r.meta.icon as string,
        path: `/${r.path}` // 단일 링크의 전체 경로
      };
    })
    .filter(item => item !== null); // null이 될 수 있는 항목 제거 (필터링된 자식이 없는 그룹)
});
</script>

<style scoped>
/* Import Premium Font */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root {
  --bg-color: #F8F9FA;
  --sidebar-bg: rgba(255, 255, 255, 0.8);
  --card-bg: #F8F9FA;
  --accent-gradient: linear-gradient(310deg, #007bff 0%, #00c6ff 100%); /* Blue gradient */
  --shadow-dark: #d1d9e6;
  --shadow-light: #ffffff;
  --primary-text: #252f40;
  --secondary-text: #67748e;
}

/* Base Styles (Mobile First) */
.dashboard-container {
  display: flex;
  flex-direction: column; /* Stack sidebar and main content vertically on small screens */
  min-height: 100vh; /* Use min-height for content flexibility */
  width: 100vw;
}

/* Sidebar Styles */
.sidebar {
  width: 100%; /* Full width on mobile */
  height: auto; /* Auto height on mobile */
  background: var(--sidebar-bg);
  backdrop-filter: blur(10px);
  padding: 16px; /* Smaller padding for mobile */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex-shrink: 0;
  z-index: 10;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3); /* Separator for mobile */
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px; /* Adjusted gap */
  padding-bottom: 16px; /* Adjusted padding */
  justify-content: center; /* Center header on mobile */
}

.logo-icon {
  width: 28px;
  height: 28px;
  background: var(--accent-gradient);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
}

.sidebar-header h2 {
  font-size: clamp(14px, 1.5vw, 16px); /* Responsive typography */
  font-weight: 700;
  letter-spacing: -0.5px;
}

.sidebar-nav {
  /* Vuetify v-list will handle most styling, but keep some base */
  margin-top: 10px;
}

/* Custom styles for active/hover states for v-list-item */
.sidebar-nav .v-list-item {
  padding: 8px 10px; /* Adjusted padding */
  text-decoration: none;
  color: var(--secondary-text);
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: clamp(10px, 1.2vw, 14px); /* Responsive typography */
  text-align: left; /* Align text left for Vuetify list items */
  margin-bottom: 6px;
}

.sidebar-nav .v-list-item--active,
.sidebar-nav .v-list-item:hover {
  background: #fff;
  color: var(--primary-text);
  box-shadow: 2px 2px 5px var(--shadow-dark);
}

.sidebar-nav .v-list-item--active .v-icon {
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Adjust icon styling within v-list-item */
.sidebar-nav .v-list-item .v-icon {
  font-size: 14px; /* Match original icon size */
  margin-right: 8px; /* Space between icon and text */
}

/* Adjust title styling within v-list-item */
.sidebar-nav .v-list-item .v-list-item__title {
  font-size: inherit; /* Inherit from parent v-list-item */
  font-weight: inherit;
}

/* Adjust for v-list-group activator */
.sidebar-nav .v-list-group__activator .v-list-item {
  margin-bottom: 0; /* Remove extra margin for group activator */
}


/* Sidebar Help Box */
.sidebar-footer {
  display: none; /* Hidden on mobile by default */
}

.help-box {
  background: var(--accent-gradient);
  border-radius: 10px;
  padding: 14px;
  color: white;
  text-align: center;
  margin-top: 20px;
}

.help-icon {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 8px;
  font-size: 14px;
}

.help-box h3 { font-size: clamp(12px, 1.2vw, 14px); margin-bottom: 2px; }
.help-box p { font-size: clamp(10px, 1vw, 11px); opacity: 0.8; margin-bottom: 12px; }

.documentation-btn {
  width: 100%;
  padding: 8px;
  border: none;
  border-radius: 6px;
  background: white;
  color: #252f40;
  font-weight: 700;
  font-size: clamp(10px, 1vw, 11px);
  cursor: pointer;
}

/* Main Content */
.main-content {
  flex-grow: 1;
  overflow-y: auto;
  padding: 16px; /* Smaller padding for mobile */
  background-color: #F8F9FA;
}

.main-header {
  display: flex;
  flex-direction: column; /* Stack header elements on mobile */
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 10px; /* Gap between title and actions */
}

.breadcrumb { font-size: clamp(10px, 1vw, 11px); color: var(--secondary-text); margin-bottom: 2px; }
.main-header h1 { font-size: clamp(18px, 2.5vw, 22px); font-weight: 700; }

.header-actions {
  display: flex;
  flex-direction: column; /* Stack actions on mobile */
  gap: 10px;
  align-items: stretch; /* Stretch items to full width */
  width: 100%;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%; /* Full width on mobile */
}

.search-wrapper i {
  position: absolute;
  left: 10px;
  color: var(--secondary-text);
  font-size: 14px;
}

.search-wrapper .neumorphic-input {
  padding: 8px 8px 8px 30px;
  width: 100%; /* Full width on mobile */
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 8px;
  outline: none;
  font-size: clamp(12px, 1.2vw, 13px);
}

.accent-btn {
  background: var(--accent-gradient);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: clamp(12px, 1.2vw, 13px);
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 123, 255, 0.3);
  width: 100%; /* Full width on mobile */
}

.icon-actions {
  display: flex;
  gap: 6px;
  justify-content: center; /* Center icons on mobile */
  width: 100%;
}
.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--secondary-text);
  cursor: pointer;
  font-size: 14px;
}

/* Neumorphic Cards */
.neumorphic-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 15px 0 rgba(0,0,0,0.03);
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.summary-cards {
  display: grid;
  grid-template-columns: 1fr; /* Single column on mobile */
  gap: 16px;
  margin-bottom: 20px;
}

.summary-cards .card {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-cards h3, .summary-cards h4 {
  font-size: clamp(12px, 1.2vw, 13px);
  color: var(--secondary-text);
  margin-bottom: 3px;
}
.card-value { font-size: clamp(16px, 2vw, 18px); font-weight: 700; }
.growth-positive { color: #28a745; font-size: clamp(10px, 1vw, 12px); margin-left: 4px; }
.growth-negative { color: #dc3545; font-size: clamp(10px, 1vw, 12px); margin-left: 4px; }

.card-icon {
  width: 40px;
  height: 40px;
  background: var(--accent-gradient);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

/* Layout Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1fr; /* Single column on mobile */
  gap: 16px;
}

.charts-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-placeholder {
  height: 180px;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  padding: 12px;
}

/* Project Table */
.project-table {
  overflow-x: auto; /* Enable horizontal scroll for tables on small screens */
}
.project-table table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
  min-width: 600px; /* Ensure table doesn't get too squished */
}

.project-table th {
  text-align: left;
  font-size: clamp(10px, 1vw, 11px);
  text-transform: uppercase;
  color: var(--secondary-text);
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.project-table td {
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: clamp(12px, 1.2vw, 13px);
}

.company-cell { display: flex; align-items: center; gap: 6px; font-weight: 600; }
.company-cell img {
  border-radius: 4px;
  width: 20px;
  height: 20px;
  max-width: 100%; /* Responsive image */
  height: auto; /* Responsive image */
  object-fit: cover; /* Responsive image */
}

.badge {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: clamp(9px, 0.9vw, 10px);
  font-weight: 700;
}
.badge-success { background: #e6f7e9; color: #2dce89; }
.badge-warning { background: #fff5e6; color: #fb6340; }

.progress-bar-container {
  width: 80px;
  height: 4px;
  background: #f0f2f5;
  border-radius: 6px;
}
.progress-bar {
  height: 100%;
  background: var(--accent-gradient);
  border-radius: 6px;
}

/* Timeline */
.timeline {
  margin-top: 12px;
}
.timeline-item {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  position: relative;
}
.timeline-item i { font-size: 12px; margin-top: 2px; }
.timeline-content p { font-size: clamp(12px, 1.2vw, 13px); font-weight: 600; }
.timeline-content span { font-size: clamp(10px, 1vw, 11px); color: var(--secondary-text); }

/* New Dashboard Section Specific Styles */
.dashboard-section {
  margin-top: 30px;
}

.dashboard-section h2 {
  font-size: clamp(18px, 2vw, 20px);
  font-weight: 700;
  margin-bottom: 16px;
}

.dashboard-section h3 {
  font-size: clamp(14px, 1.5vw, 16px);
  font-weight: 600;
  margin-bottom: 12px;
  margin-top: 20px;
}

/* --- Media Queries (Mobile-First) --- */

/* sm (640px 이상): 모바일 가로 모드 및 소형 화면 */
@media (min-width: 640px) {
  .sidebar-nav ul {
    justify-content: flex-start; /* Align nav items to start */
    gap: 12px;
  }
  .sidebar-nav a {
    flex-direction: row; /* Icon and text side-by-side */
    padding: 10px 14px;
    text-align: left;
  }
  .sidebar-nav a span {
    margin-top: 0;
    margin-left: 8px; /* Space between icon and text */
  }

  .summary-cards {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); /* Two columns or more */
  }
  .main-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
  .header-actions {
    flex-direction: row;
    align-items: center;
    width: auto;
  }
  .search-wrapper {
    width: auto;
  }
  .search-wrapper .neumorphic-input {
    width: 200px; /* Restore specific width */
  }
  .accent-btn {
    width: auto;
  }
  .icon-actions {
    width: auto;
  }
}

/* md (768px 이상): 태블릿 (세로 모드) */
@media (min-width: 768px) {
  .dashboard-container {
    flex-direction: row; /* Sidebar and main content side-by-side */
  }
  .sidebar {
    width: 260px; /* Fixed width sidebar */
    height: 100vh; /* Full height */
    border-right: 1px solid rgba(255, 255, 255, 0.3);
    border-bottom: none; /* Remove bottom border */
    padding: 24px; /* Restore larger padding */
  }
  .sidebar-header {
    justify-content: flex-start; /* Align header to start */
    padding-bottom: 30px;
  }
  .sidebar-nav ul {
    flex-direction: column; /* Stack nav items vertically */
    gap: 6px;
  }
  .sidebar-nav a {
    flex-direction: row;
    padding: 10px 14px;
  }
  .sidebar-nav a span {
    margin-left: 12px;
  }
  .sidebar-footer {
    display: block; /* Show help box */
  }
  .main-content {
    padding: 25px 35px; /* Restore larger padding */
  }
  .main-grid {
    grid-template-columns: 1.5fr 1fr; /* Two columns for main grid */
  }
}

/* lg (1024px 이상): 노트북 및 태블릿 (가로 모드) */
@media (min-width: 1024px) {
  /* Further refinements for larger screens if needed */
}

/* xl (1280px 이상): 기본 데스크탑 모니터 */
@media (min-width: 1280px) {
  /* Further refinements for larger screens if needed */
}

/* 2xl (1536px 이상): 대형 모니터 및 고해상도 디스플레이 */
@media (min-width: 1536px) {
  /* Further refinements for very large screens if needed */
}
</style>
