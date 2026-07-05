<template>
    <div class="dashboard-container">
        <!-- Sidebar (Desktop View) -->
        <aside class="sidebar desktop-sidebar">
            <div class="sidebar-top-section">
                <div class="sidebar-header">
                    <div class="logo-icon"><v-icon>mdi-shield-alert</v-icon></div>
                    <h2>Error Monitor</h2>
                </div>
                <nav class="sidebar-nav">
                    <ul>
                        <li>
                            <router-link to="/dashboard" active-class="active">
                                <v-icon>mdi-view-dashboard</v-icon> <span>Dashboard</span>
                            </router-link>
                        </li>
                        <li>
                            <router-link to="/analytics" active-class="active">
                                <v-icon>mdi-chart-bar</v-icon> <span>Analytics</span>
                            </router-link>
                        </li>
                        <li>
                            <router-link to="/billing" active-class="active">
                                <v-icon>mdi-wallet</v-icon> <span>Billing</span>
                            </router-link>
                        </li>
                        <li>
                            <a @click="accountDropdown" :class="{ active: isAccountDropdownOpen }" class="collapsible-activator">
                                <v-icon>mdi-account-circle</v-icon> <span>Accounts</span>
                            </a>
                            <ul v-if="isAccountDropdownOpen" class="collapsible-submenu">
                                <li>
                                    <router-link to="/dropdown/subitem1" active-class="active">
                                        <span>Account Overview</span>
                                    </router-link>
                                </li>
                                <li>
                                    <router-link to="/dropdown/subitem2" active-class="active">
                                        <span>Account Settings</span>
                                    </router-link>
                                </li>
                            </ul>
                        </li>
                        <li>
                            <a @click="healthDropdown" :class="{ active: isHealthOpen }" class="collapsible-activator">
                                <v-icon>mdi-heart-pulse</v-icon> <span>Health</span>
                            </a>
                            <ul v-if="isHealthOpen" class="collapsible-submenu">
                                <li>
                                    <router-link to="/health/healthDashboard" active-class="active">
                                        <span>Health Dashboard</span>
                                    </router-link>
                                </li>
                            </ul>
                        </li>
                        <li>
                            <a @click="statisticsDropdown" :class="{ active: isStatistics }" class="collapsible-activator">
                                <v-icon>mdi-chart-box</v-icon> <span>Reports</span>
                            </a>
                            <ul v-if="isStatistics" class="collapsible-submenu">
                                <li>
                                    <router-link to="/error-statistics" active-class="active">
                                        <v-icon>mdi-alert-circle-outline</v-icon> <span>Error Monitoring</span>
                                    </router-link>
                                </li>
                            </ul>
                        </li>
                        <li>
                            <router-link to="/profile" active-class="active">
                                <v-icon>mdi-account-circle</v-icon> <span>Profile</span>
                            </router-link>
                        </li>
                        <li>
                            <router-link to="/settings" active-class="active">
                                <v-icon>mdi-cog</v-icon> <span>Settings</span>
                            </router-link>
                        </li>
                    </ul>
                </nav>
            </div>
            <div class="sidebar-footer">
                <div class="help-box">
                    <div class="help-icon"><v-icon>mdi-lifebuoy</v-icon></div>
                    <h3>Need assistance?</h3>
                    <p>Find support and guides</p>
                    <button class="documentation-btn">GET HELP</button>
                </div>
            </div>
        </aside>

        <!-- Mobile Navigation Drawer Overlay -->
        <div class="mobile-drawer-overlay" :class="{ open: isMobileDrawerOpen }" @click="isMobileDrawerOpen = false">
            <aside class="sidebar mobile-sidebar" @click.stop>
                <div class="sidebar-top-section">
                    <div class="mobile-drawer-header d-flex justify-space-between align-center mb-4">
                        <div class="sidebar-header pa-0 mb-0 border-none d-flex align-center" style="gap: 12px;">
                            <div class="logo-icon"><v-icon>mdi-shield-alert</v-icon></div>
                            <h2>Error Monitor</h2>
                        </div>
                        <button class="close-drawer-btn" @click="isMobileDrawerOpen = false">
                            <v-icon>mdi-close</v-icon>
                        </button>
                    </div>
                    <nav class="sidebar-nav">
                        <ul>
                            <li>
                                <router-link to="/dashboard" active-class="active" @click="isMobileDrawerOpen = false">
                                    <v-icon>mdi-view-dashboard</v-icon> <span>Dashboard</span>
                                </router-link>
                            </li>
                            <li>
                                <router-link to="/analytics" active-class="active" @click="isMobileDrawerOpen = false">
                                    <v-icon>mdi-chart-bar</v-icon> <span>Analytics</span>
                                </router-link>
                            </li>
                            <li>
                                <router-link to="/billing" active-class="active" @click="isMobileDrawerOpen = false">
                                    <v-icon>mdi-wallet</v-icon> <span>Billing</span>
                                </router-link>
                            </li>
                            <li>
                                <a @click="accountDropdown" :class="{ active: isAccountDropdownOpen }" class="collapsible-activator">
                                    <v-icon>mdi-account-circle</v-icon> <span>Accounts</span>
                                </a>
                                <ul v-if="isAccountDropdownOpen" class="collapsible-submenu">
                                    <li>
                                        <router-link to="/dropdown/subitem1" active-class="active" @click="isMobileDrawerOpen = false">
                                            <span>Account Overview</span>
                                        </router-link>
                                    </li>
                                    <li>
                                        <router-link to="/dropdown/subitem2" active-class="active" @click="isMobileDrawerOpen = false">
                                            <span>Account Settings</span>
                                        </router-link>
                                    </li>
                                </ul>
                            </li>
                            <li>
                                <a @click="healthDropdown" :class="{ active: isHealthOpen }" class="collapsible-activator">
                                    <v-icon>mdi-heart-pulse</v-icon> <span>Health</span>
                                </a>
                                <ul v-if="isHealthOpen" class="collapsible-submenu">
                                    <li>
                                        <router-link to="/health/healthDashboard" active-class="active" @click="isMobileDrawerOpen = false">
                                            <span>Health Dashboard</span>
                                        </router-link>
                                    </li>
                                </ul>
                            </li>
                            <li>
                                <a @click="statisticsDropdown" :class="{ active: isStatistics }" class="collapsible-activator">
                                    <v-icon>mdi-chart-box</v-icon> <span>Reports</span>
                                </a>
                                <ul v-if="isStatistics" class="collapsible-submenu">
                                    <li>
                                        <router-link to="/error-statistics" active-class="active" @click="isMobileDrawerOpen = false">
                                            <v-icon>mdi-alert-circle-outline</v-icon> <span>Error Monitoring</span>
                                        </router-link>
                                    </li>
                                </ul>
                            </li>
                            <li>
                                <router-link to="/profile" active-class="active" @click="isMobileDrawerOpen = false">
                                    <v-icon>mdi-account-circle</v-icon> <span>Profile</span>
                                </router-link>
                            </li>
                            <li>
                                <router-link to="/settings" active-class="active" @click="isMobileDrawerOpen = false">
                                    <v-icon>mdi-cog</v-icon> <span>Settings</span>
                                </router-link>
                            </li>
                        </ul>
                    </nav>
                </div>
            </aside>
        </div>

        <!-- Main Content Area -->
        <main class="main-content">
            <header class="main-header">
                <div class="d-flex align-center">
                    <button class="hamburger-btn mr-3" @click="isMobileDrawerOpen = true">
                        <v-icon>mdi-menu</v-icon>
                    </button>
                    <div class="header-title">
                        <p class="breadcrumb">{{ route.meta.breadcrumb }}</p>
                        <h1>{{ route.meta.pageTitle }}</h1>
                    </div>
                </div>
                <div class="header-actions">
                    <div class="search-wrapper">
                        <v-icon>mdi-magnify</v-icon>
                        <input type="text" placeholder="Search logs..." class="neumorphic-input" />
                    </div>
                    <button class="neumorphic-btn accent-btn"><v-icon>mdi-bell-alert</v-icon> Alerts</button>
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
import { ref } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const isAccountDropdownOpen = ref(false);
const isHealthOpen = ref(false);
const isStatistics = ref(false);
const isMobileDrawerOpen = ref(false);

const accountDropdown = () => {
    isAccountDropdownOpen.value = !isAccountDropdownOpen.value;
};
const healthDropdown = () => {
    isHealthOpen.value = !isHealthOpen.value;
};
const statisticsDropdown = () => {
    isStatistics.value = !isStatistics.value;
};
</script>

<style scoped lang="scss">
@use "../../styles/settings.scss" as *;

/* Import Premium Fonts */
@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap");
@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");

.dashboard-container {
    display: flex;
    width: 100vw;
    height: 100vh;
    font-family: 'Plus Jakarta Sans', 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
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
    width: 30px;
    height: 30px;
    background: $accent-gradient;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 14px;
}

.sidebar-header h2 {
    font-size: 16px;
    font-weight: 700;
    letter-spacing: -0.5px;
}

.sidebar-nav ul {
    list-style: none;
}

.sidebar-nav li {
    margin-bottom: 6px;
}

.sidebar-nav a {
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

.sidebar-nav a i {
    width: 28px;
    font-size: 16px;
}

.sidebar-nav a.active,
.sidebar-nav a:hover,
.sidebar-nav .collapsible-activator:hover {
    background: #fff;
    color: $primary-text;
    box-shadow: 4px 4px 10px $shadow-dark;
}

.sidebar-nav a.active i,
.sidebar-nav .collapsible-activator:hover i {
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
    padding-left: 30px;
    margin-top: 5px;
    margin-bottom: 5px;
}

.collapsible-submenu li a {
    padding: 8px 14px;
    font-size: 13px;
    color: $secondary-text;
}

.collapsible-submenu li a:hover,
.collapsible-submenu li a.active {
    background: #f0f2f5;
    color: $primary-text;
    box-shadow: none;
}

/* Sidebar Help Box */
.help-box {
    background: $accent-gradient;
    border-radius: 14px;
    padding: 18px;
    color: white;
    text-align: center;
}

.help-icon {
    width: 36px;
    height: 36px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 10px;
    font-size: 16px;
}

.help-box h3 {
    font-size: 14px;
    margin-bottom: 3px;
}
.help-box p {
    font-size: 11px;
    opacity: 0.8;
    margin-bottom: 14px;
}

.documentation-btn {
    width: 100%;
    padding: 9px;
    border: none;
    border-radius: 7px;
    background: white;
    color: #252f40;
    font-weight: 700;
    font-size: 11px;
    cursor: pointer;
}

/* Main Content - Scrollable */
.main-content {
    flex-grow: 1;
    height: 100%;
    overflow-y: auto;
    padding: 25px 35px;
    background-color: $bg-color;
}

.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.breadcrumb {
    font-size: 11px;
    color: $secondary-text;
    margin-bottom: 3px;
}
.main-header h1 {
    font-size: 22px;
    font-weight: 700;
}

.header-actions {
    display: flex;
    gap: 15px;
    align-items: center;
}

.search-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.search-wrapper i {
    position: absolute;
    left: 12px;
    color: $secondary-text;
    font-size: 14px;
}

.search-wrapper .neumorphic-input {
    padding: 10px 10px 10px 35px;
    width: 220px;
    border: 1px solid #e2e8f0;
    background: #fff;
    border-radius: 10px;
    outline: none;
    font-size: 13px;
}

.accent-btn {
    background: $accent-gradient;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.icon-actions {
    display: flex;
    gap: 8px;
}
.icon-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background: transparent;
    color: $secondary-text;
    cursor: pointer;
    font-size: 16px;
}

.hamburger-btn {
    display: none;
}

/* Mobile Drawer Styles */
.mobile-drawer-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(4px);
    z-index: 999;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.mobile-drawer-overlay.open {
    opacity: 1;
    visibility: visible;
}
.mobile-sidebar {
    width: 280px;
    height: 100%;
    background: #f8fafc;
    box-shadow: 10px 0 30px rgba(15, 23, 42, 0.1);
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: absolute;
    top: 0;
    left: 0;
    display: flex !important;
    flex-direction: column;
}
.mobile-drawer-overlay.open .mobile-sidebar {
    transform: translateX(0);
}
.close-drawer-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    color: #64748b;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 0.2s;
}
.close-drawer-btn:hover {
    background-color: #f1f5f9;
}

/* RESPONSIVE */
@media (max-width: 959px) {
    .desktop-sidebar {
        display: none !important;
    }
    .hamburger-btn {
        display: flex !important;
        align-items: center;
        justify-content: center;
        background: white;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 8px;
        width: 38px;
        height: 38px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.03);
        cursor: pointer;
    }
    .main-content {
        padding: 20px 16px !important;
    }
}
@media (max-width: 768px) {
    .header-actions {
        display: none;
    }
}
</style>

<style lang="scss">
body, html, #app {
    font-family: 'Plus Jakarta Sans', 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
}
</style>
