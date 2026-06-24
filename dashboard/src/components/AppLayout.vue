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
          <ul>
            <li><router-link to="/dashboard" active-class="active"><v-icon>mdi-view-dashboard</v-icon> <span>Dashboard</span></router-link></li>
            <li><router-link to="/analytics" active-class="active"><v-icon>mdi-chart-bar</v-icon> <span>Analytics</span></router-link></li>
            <li><router-link to="/billing" active-class="active"><v-icon>mdi-wallet</v-icon> <span>Billing</span></router-link></li>
            <li>
              <a @click="toggleDropdown" :class="{ 'active': isDropdownOpen }" class="collapsible-activator">
                <v-icon>mdi-menu-down</v-icon> <span>Dropdown</span>
              </a>
              <ul v-if="isDropdownOpen" class="collapsible-submenu">
                <li><router-link to="/dropdown/subitem1" active-class="active"><span>Sub-item 1</span></router-link></li>
                <li><router-link to="/dropdown/subitem2" active-class="active"><span>Sub-item 2</span></router-link></li>
              </ul>
              <ul v-if="isDropdownOpen" class="collapsible-submenu">
                <li><router-link to="/health/healthDashboard" active-class="active"><span>healthDashboard</span></router-link></li>
              </ul>
            </li>
            <li><router-link to="/profile" active-class="active"><v-icon>mdi-account-circle</v-icon> <span>Profile</span></router-link></li>
            <li><router-link to="/settings" active-class="active"><v-icon>mdi-cog</v-icon> <span>Settings</span></router-link></li>
          </ul>
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

      <!-- Slot for page-specific content -->
      <router-view></router-view>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router'; // useRoute 임포트

const route = useRoute(); // route 객체 가져오기

const isDropdownOpen = ref(false);

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value;
};
</script>

<style scoped lang="scss">
// Import global variables - MUST BE THE VERY FIRST LINE
@use '../styles/settings.scss' as *;

/* Import Premium Font */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* Removed global styles for html, body, and * from here.
   These should be in a global stylesheet (e.g., src/assets/main.css)
   or in a non-scoped style block in App.vue. */

.dashboard-container {
  display: flex;
  width: 100vw;
  height: 100vh;
}

/* Sidebar Styles - Fixed Height 100% */
.sidebar {
  width: 260px;
  height: 100%;
  background: $sidebar-bg;
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.3);
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex-shrink: 0;
  z-index: 10;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 30px;
}

.logo-icon {
  width: 30px; /* Reduced size */
  height: 30px; /* Reduced size */
  background: $accent-gradient;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px; /* Reduced icon size */
}

.sidebar-header h2 {
  font-size: 16px; /* Reduced from 18px */
  font-weight: 700;
  letter-spacing: -0.5px;
}

.sidebar-nav ul {
  list-style: none;
}

.sidebar-nav li {
  margin-bottom: 6px; /* Reduced margin */
}

.sidebar-nav a {
  display: flex;
  align-items: center;
  padding: 10px 14px; /* Reduced padding */
  text-decoration: none;
  color: $secondary-text;
  border-radius: 10px; /* Reduced border-radius */
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 14px; /* Explicitly set font size */
}

.sidebar-nav a i {
  width: 28px; /* Reduced size */
  font-size: 16px; /* Reduced size */
}

.sidebar-nav a.active, .sidebar-nav a:hover, .sidebar-nav .collapsible-activator:hover {
  background: #fff;
  color: $primary-text;
  box-shadow: 4px 4px 10px $shadow-dark;
}

.sidebar-nav a.active i, .sidebar-nav .collapsible-activator:hover i {
  background: $accent-gradient;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Collapsible Menu Specific Styles */
.collapsible-activator {
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 10px 14px;
  text-decoration: none;
  color: $secondary-text;
  border-radius: 10px;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 14px;
}

.collapsible-activator i {
  transition: transform 0.3s ease;
}

.collapsible-activator.active i {
  transform: rotate(180deg);
}

.collapsible-submenu {
  list-style: none;
  padding-left: 30px; /* Indent sub-items */
  margin-top: 5px;
  margin-bottom: 5px;
}

.collapsible-submenu li a {
  padding: 8px 14px; /* Adjust padding for sub-items */
  font-size: 13px; /* Slightly smaller font for sub-items */
  color: $secondary-text;
}

.collapsible-submenu li a:hover, .collapsible-submenu li a.active {
  background: #f0f2f5; /* Lighter background for sub-item hover/active */
  color: $primary-text;
  box-shadow: none; /* Remove shadow for sub-items */
}


/* Sidebar Help Box */
.help-box {
  background: $accent-gradient;
  border-radius: 14px; /* Reduced border-radius */
  padding: 18px; /* Reduced padding */
  color: white;
  text-align: center;
}

.help-icon {
  width: 36px; /* Reduced size */
  height: 36px; /* Reduced size */
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px; /* Reduced border-radius */
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px; /* Reduced margin */
  font-size: 16px; /* Reduced icon size */
}

.help-box h3 { font-size: 14px; /* Reduced from 16px */ margin-bottom: 3px; }
.help-box p { font-size: 11px; /* Reduced from 12px */ opacity: 0.8; margin-bottom: 14px; }

.documentation-btn {
  width: 100%;
  padding: 9px; /* Reduced padding */
  border: none;
  border-radius: 7px; /* Reduced border-radius */
  background: white;
  color: #252f40;
  font-weight: 700;
  font-size: 11px; /* Reduced from 12px */
  cursor: pointer;
}

/* Main Content - Scrollable */
.main-content {
  flex-grow: 1;
  height: 100%;
  overflow-y: auto;
  padding: 25px 35px; /* Reduced padding */
  background-color: $bg-color;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px; /* Reduced margin */
}

.breadcrumb { font-size: 11px; /* Reduced from 12px */ color: $secondary-text; margin-bottom: 3px; }
.main-header h1 { font-size: 22px; /* Reduced from 24px */ font-weight: 700; }

.header-actions {
  display: flex;
  gap: 15px; /* Reduced gap */
  align-items: center;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-wrapper i {
  position: absolute;
  left: 12px; /* Reduced left position */
  color: $secondary-text;
  font-size: 14px; /* Reduced icon size */
}

.search-wrapper .neumorphic-input {
  padding: 10px 10px 10px 35px; /* Reduced padding */
  width: 220px; /* Reduced width */
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 10px; /* Reduced border-radius */
  outline: none;
  font-size: 13px; /* Explicitly set font size */
}

.accent-btn {
  background: $accent-gradient;
  color: white;
  border: none;
  padding: 10px 20px; /* Reduced padding */
  border-radius: 10px; /* Reduced border-radius */
  font-weight: 700;
  font-size: 13px; /* Explicitly set font size */
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3); /* Adjusted shadow color */
}

.icon-actions { display: flex; gap: 8px; /* Reduced gap */ }
.icon-btn {
  width: 36px; /* Reduced size */
  height: 36px; /* Reduced size */
  border-radius: 50%;
  border: none;
  background: transparent;
  color: $secondary-text;
  cursor: pointer;
  font-size: 16px; /* Reduced icon size */
}

/* Neumorphic Cards */
.neumorphic-card {
  background: #fff;
  border-radius: 14px; /* Reduced border-radius */
  box-shadow: 0 15px 20px 0 rgba(0,0,0,0.04); /* Adjusted shadow */
  padding: 18px; /* Reduced padding */
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); /* Adjusted for flexibility */
  gap: 20px; /* Reduced gap */
  margin-bottom: 25px; /* Reduced margin */
}

.summary-cards .card {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-cards h3, .summary-cards h4 { /* Added h4 for new dashboard cards */
  font-size: 13px; /* Reduced from 14px */
  color: $secondary-text;
  margin-bottom: 4px;
}
.card-value { font-size: 18px; /* Reduced from 20px */ font-weight: 700; }
.growth-positive { color: #28a745; /* Green */ font-size: 12px; /* Reduced from 14px */ margin-left: 4px; }
.growth-negative { color: #dc3545; /* Red */ font-size: 12px; /* Reduced from 14px */ margin-left: 4px; }

.card-icon {
  width: 44px; /* Reduced size */
  height: 44px; /* Reduced size */
  background: $accent-gradient;
  border-radius: 10px; /* Reduced border-radius */
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px; /* Reduced icon size */
}

/* Layout Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px; /* Reduced gap */
}

.charts-section {
  display: flex;
  flex-direction: column;
  gap: 20px; /* Reduced gap */
}

.chart-placeholder {
  height: 200px; /* Reduced height */
  background: #f8f9fa;
  border-radius: 10px; /* Reduced border-radius */
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  padding: 15px; /* Reduced padding */
}

/* Project Table */
.project-table table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px; /* Reduced margin */
}

.project-table th {
  text-align: left;
  font-size: 11px; /* Reduced from 12px */
  text-transform: uppercase;
  color: $secondary-text;
  padding: 10px 0; /* Reduced padding */
  border-bottom: 1px solid #f0f0f0;
}

.project-table td {
  padding: 12px 0; /* Reduced padding */
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px; /* Reduced from 14px */
}

.company-cell { display: flex; align-items: center; gap: 8px; /* Reduced gap */ font-weight: 600; }
.company-cell img { border-radius: 5px; /* Reduced border-radius */ width: 20px; height: 20px; } /* Reduced image size */

.badge {
  padding: 3px 10px; /* Reduced padding */
  border-radius: 7px; /* Reduced border-radius */
  font-size: 10px; /* Reduced from 11px */
  font-weight: 700;
}
.badge-success { background: #e6f7e9; color: #2dce89; }
.badge-warning { background: #fff5e6; color: #fb6340; }

.progress-bar-container {
  width: 90px; /* Reduced width */
  height: 5px; /* Reduced height */
  background: #f0f2f5;
  border-radius: 8px; /* Reduced border-radius */
}
.progress-bar {
  height: 100%;
  background: $accent-gradient;
  border-radius: 8px; /* Reduced border-radius */
}

/* Timeline */
.timeline {
  margin-top: 15px; /* Reduced margin */
}
.timeline-item {
  display: flex;
  gap: 12px; /* Reduced gap */
  margin-bottom: 15px; /* Reduced margin */
  position: relative;
}
.timeline-item i { font-size: 14px; /* Reduced size */ margin-top: 3px; }
.timeline-content p { font-size: 13px; /* Reduced from 14px */ font-weight: 600; }
.timeline-content span { font-size: 11px; /* Reduced from 12px */ color: $secondary-text; }

/* New Dashboard Section Specific Styles */
.dashboard-container h2 {
  font-size: 20px; /* Reduced from default */
  font-weight: 700;
  margin-bottom: 20px;
}

.dashboard-container h3 {
  font-size: 16px; /* Reduced from default */
  font-weight: 600;
  margin-bottom: 15px;
  margin-top: 30px; /* Added margin for separation */
}

/* RESPONSIVE */
@media (max-width: 1200px) {
  .summary-cards { grid-template-columns: repeat(2, 1fr); }
  .main-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .dashboard-container { flex-direction: column; }
  .sidebar { width: 100%; height: auto; }
  .main-content { padding: 15px; }
  .summary-cards { grid-template-columns: 1fr; }
  .header-actions { flex-direction: column; align-items: stretch; }
  .search-wrapper .neumorphic-input { width: 100%; }
}
</style>