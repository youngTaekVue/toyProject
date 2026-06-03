<template>
  <AppLayout pageTitle="Main Dashboard" breadcrumb="Pages / Dashboard" currentRoute="dashboard">
    <!-- v-container fluid를 사용하여 v-row의 음수 마진을 상쇄하고 가로 스크롤을 방지합니다 -->
    <v-container fluid class="dashboard-section pt-0">
      <h2>App Dashboard Overview</h2>

      <!-- App Overview and Key Metrics -->
      <v-row class="summary-cards">
        <v-col cols="12" sm="6" md="4" lg="3">
          <div class="card neumorphic-card">
            <div class="card-content">
              <h4>Total Installs</h4>
              <p class="card-value">150,000 <span class="growth-positive">+12%</span></p>
            </div>
            <div class="card-icon"><v-icon>mdi-download</v-icon></div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="3">
          <div class="card neumorphic-card">
            <div class="card-content">
              <h4>Daily Active Users (DAU)</h4>
              <p class="card-value">25,000 <span class="growth-positive">+5%</span></p>
            </div>
            <div class="card-icon"><v-icon>mdi-account-group</v-icon></div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="3">
          <div class="card neumorphic-card">
            <div class="card-content">
              <h4>Monthly Active Users (MAU)</h4>
              <p class="card-value">75,000 <span class="growth-positive">+8%</span></p>
            </div>
            <div class="card-icon"><v-icon>mdi-account-check</v-icon></div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="3">
          <div class="card neumorphic-card">
            <div class="card-content">
              <h4>Avg. Rating</h4>
              <p class="card-value">4.5 <span class="growth-positive">(12k Reviews)</span></p>
            </div>
            <div class="card-icon"><v-icon>mdi-star</v-icon></div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="3">
          <div class="card neumorphic-card">
            <div class="card-content">
              <h4>Revenue (Est.)</h4>
              <p class="card-value">$1,200 <span class="growth-positive">+15%</span></p>
            </div>
            <div class="card-icon"><v-icon>mdi-currency-usd</v-icon></div>
          </div>
        </v-col>
      </v-row>

      <!-- User Acquisition and Churn -->
      <h3 style="margin-top: 40px;">User Acquisition & Churn</h3>
      <v-row class="main-grid">
        <v-col cols="12" lg="8">
          <div class="chart-card neumorphic-card">
            <div class="chart-header">
              <h4>Downloads Trend</h4>
              <p><span>(+10%) more</span> this month</p>
            </div>
            <div class="chart-placeholder">
              <!-- Chart will be rendered here by JS -->
            </div>
          </div>
        </v-col>
        <v-col cols="12" lg="4">
          <div class="chart-card neumorphic-card">
            <div class="chart-header">
              <h4>Uninstall Rate</h4>
              <p><span>(-0.5%) decrease</span> from last month</p>
            </div>
            <div class="chart-placeholder circle-placeholder">
              <!-- Chart will be rendered here by JS -->
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row class="summary-cards" style="margin-top: 20px;">
        <v-col cols="12" sm="6" md="4" lg="3">
          <div class="card neumorphic-card">
            <div class="card-content">
              <h4>D1 Retention</h4>
              <p class="card-value">65% <span class="growth-positive">+2%</span></p>
            </div>
            <div class="card-icon"><v-icon>mdi-refresh</v-icon></div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="3">
          <div class="card neumorphic-card">
            <div class="card-content">
              <h4>D7 Retention</h4>
              <p class="card-value">40% <span class="growth-positive">+1%</span></p>
            </div>
            <div class="card-icon"><v-icon>mdi-refresh</v-icon></div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="3">
          <div class="card neumorphic-card">
            <div class="card-content">
              <h4>D30 Retention</h4>
              <p class="card-value">20% <span class="growth-positive">0%</span></p>
            </div>
            <div class="card-icon"><v-icon>mdi-refresh</v-icon></div>
          </div>
        </v-col>
      </v-row>

      <!-- User Behavior and Engagement -->
      <h3 style="margin-top: 40px;">User Behavior & Engagement</h3>
      <v-row class="main-grid">
        <v-col cols="12" lg="8">
          <div class="chart-card neumorphic-card">
            <div class="chart-header">
              <h4>Average Session Time</h4>
              <p><span>(+10s) increase</span> from last week</p>
            </div>
            <div class="chart-placeholder circle-placeholder">
              <!-- Chart will be rendered here by JS -->
            </div>
          </div>
        </v-col>
        <v-col cols="12" lg="4">
          <div class="table-responsive-wrapper">
            <div class="project-table neumorphic-card">
              <h4>Feature Usage</h4>
              <table>
                <thead>
                <tr>
                  <th>Feature</th>
                  <th>Usage Count</th>
                  <th>% of Users</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                  <td>Hourly Forecast</td>
                  <td>120,000</td>
                  <td>80%</td>
                </tr>
                <tr>
                  <td>Weekly Forecast</td>
                  <td>90,000</td>
                  <td>60%</td>
                </tr>
                <tr>
                  <td>Weather Widget</td>
                  <td>45,000</td>
                  <td>30%</td>
                </tr>
                <tr>
                  <td>Location Search</td>
                  <td>75,000</td>
                  <td>50%</td>
                </tr>
                </tbody>
              </table>
            </div>
          </div>
        </v-col>
      </v-row>
      <div class="table-responsive-wrapper" style="margin-top: 20px;">
        <div class="project-table neumorphic-card">
          <h4>Geographical Distribution</h4>
          <table>
            <thead>
            <tr>
              <th>Country</th>
              <th>Users</th>
              <th>% of Total</th>
            </tr>
            </thead>
            <tbody>
            <tr>
              <td>South Korea</td>
              <td>80,000</td>
              <td>53.3%</td>
            </tr>
            <tr>
              <td>United States</td>
              <td>30,000</td>
              <td>20.0%</td>
            </tr>
            <tr>
              <td>Japan</td>
              <td>15,000</td>
              <td>10.0%</td>
            </tr>
            <tr>
              <td>Germany</td>
              <td>7,500</td>
              <td>5.0%</td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- App Performance and Stability -->
      <h3 style="margin-top: 40px;">App Performance & Stability</h3>
      <v-row class="summary-cards">
        <v-col cols="12" sm="6" md="4" lg="3">
          <div class="card neumorphic-card">
            <div class="card-content">
              <h4>Crash Rate</h4>
              <p class="card-value">0.1% <span class="growth-negative">-0.05%</span></p>
            </div>
            <div class="card-icon"><v-icon>mdi-bug</v-icon></div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="3">
          <div class="card neumorphic-card">
            <div class="card-content">
              <h4>ANR Rate</h4>
              <p class="card-value">0.05% <span class="growth-negative">-0.02%</span></p>
            </div>
            <div class="card-icon"><v-icon>mdi-hourglass-half</v-icon></div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="3">
          <div class="card neumorphic-card">
            <div class="card-content">
              <h4>Load Time (Avg)</h4>
              <p class="card-value">1.5s <span class="growth-positive">+0.1s</span></p>
            </div>
            <div class="card-icon"><v-icon>mdi-speedometer</v-icon></div>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '../components/AppLayout.vue'; // Updated import path
</script>

<style scoped>
/* New Dashboard Section Specific Styles */
.dashboard-section {
  margin-top: 40px;
}

.dashboard-section h2 {
  font-size: 18px; /* Base for xs */
  font-weight: 700;
  margin-bottom: 20px;
}

.dashboard-section h3 {
  font-size: 14px; /* Base for xs */
  font-weight: 600;
  margin-bottom: 15px;
  margin-top: 30px; /* Added margin for separation */
}

/* Neumorphic Cards */
.neumorphic-card {
  background: #fff;
  border-radius: 14px; /* Reduced border-radius */
  box-shadow: 0 15px 20px 0 rgba(0,0,0,0.04); /* Adjusted shadow */
  padding: 18px; /* Reduced padding */
  border: 1px solid rgba(255, 255, 255, 0.3);
  height: 100%; /* Ensure cards in v-col take full height */
}

/* Vuetify v-row adds negative margins, so we need to adjust */
.summary-cards {
  margin-bottom: 25px; /* Reduced margin */
}

.summary-cards .card {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-cards h3, .summary-cards h4 { /* Added h4 for new dashboard cards */
  font-size: 12px; /* Base for xs */
  color: var(--secondary-text);
  margin-bottom: 4px;
}
.card-value { font-size: 16px; /* Base for xs */ font-weight: 700; }
.growth-positive, .growth-negative {
  font-size: 11px; /* Base for xs */
  margin-left: 4px;
}
.growth-positive { color: #28a745; /* Green */ }
.growth-negative { color: #dc3545; /* Red */ }

.card-icon {
  width: 40px; /* Base for xs */
  height: 40px; /* Base for xs */
  background: linear-gradient(310deg, #007bff 0%, #00c6ff 100%);
  border-radius: 10px; /* Reduced border-radius */
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px; /* Base for xs */
}

/* Layout Grid */
/* .main-grid is now a v-row, so gap is handled by Vuetify */

.charts-section {
  display: flex;
  flex-direction: column;
  gap: 20px; /* Reduced gap */
}

.chart-placeholder {
  height: 180px; /* Base for xs */
  background: #f8f9fa;
  border-radius: 10px; /* Reduced border-radius */
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  padding: 15px; /* Reduced padding */
}

/* Project Table */
.table-responsive-wrapper {
  overflow-x: auto; /* Enable horizontal scrolling */
  width: 100%; /* Ensure it takes full width */
}

.project-table table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px; /* Reduced margin */
  min-width: 500px; /* Ensure table has a minimum width to enable scrolling */
}

.project-table th {
  text-align: left;
  font-size: 10px; /* Base for xs */
  text-transform: uppercase;
  color: var(--secondary-text);
  padding: 10px 0; /* Reduced padding */
  border-bottom: 1px solid #f0f0f0;
}

.project-table td {
  padding: 12px 0; /* Reduced padding */
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px; /* Base for xs */
}

.company-cell { display: flex; align-items: center; gap: 8px; /* Reduced gap */ font-weight: 600; }
.company-cell img { border-radius: 5px; /* Reduced border-radius */ width: 20px; height: 20px; } /* Reduced image size */

.badge {
  padding: 3px 8px; /* Base for xs */
  border-radius: 7px; /* Reduced border-radius */
  font-size: 9px; /* Base for xs */
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
  background: linear-gradient(310deg, #007bff 0%, #00c6ff 100%);
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
.timeline-content p { font-size: 12px; /* Base for xs */ font-weight: 600; }
.timeline-content span { font-size: 10px; /* Base for xs */ color: var(--secondary-text); }

/* Responsive Font Sizes */
/* Small (sm) - 600px and up */
@media (min-width: 600px) {
  .dashboard-section h2 { font-size: 19px; }
  .dashboard-section h3 { font-size: 15px; }
  .summary-cards h3, .summary-cards h4 { font-size: 13px; }
  .card-value { font-size: 17px; }
  .growth-positive, .growth-negative { font-size: 12px; }
  .card-icon { width: 42px; height: 42px; font-size: 17px; }
  .chart-placeholder { height: 190px; }
  .project-table th { font-size: 11px; }
  .project-table td { font-size: 13px; }
  .badge { padding: 3px 10px; font-size: 10px; }
  .timeline-content p { font-size: 13px; }
  .timeline-content span { font-size: 11px; }
}

/* Medium (md) - 840px and up */
@media (min-width: 840px) {
  .dashboard-section h2 { font-size: 20px; }
  .dashboard-section h3 { font-size: 16px; }
  .summary-cards h3, .summary-cards h4 { font-size: 14px; }
  .card-value { font-size: 18px; }
  .growth-positive, .growth-negative { font-size: 13px; }
  .card-icon { width: 44px; height: 44px; font-size: 18px; }
  .chart-placeholder { height: 200px; }
  .project-table th { font-size: 12px; }
  .project-table td { font-size: 14px; }
  .badge { font-size: 11px; }
  .timeline-content p { font-size: 14px; }
  .timeline-content span { font-size: 12px; }
}

/* Large (lg) - 1145px and up */
@media (min-width: 1145px) {
  .dashboard-section h2 { font-size: 22px; }
  .dashboard-section h3 { font-size: 18px; }
  .summary-cards h3, .summary-cards h4 { font-size: 15px; }
  .card-value { font-size: 20px; }
  .growth-positive, .growth-negative { font-size: 14px; }
  .card-icon { width: 48px; height: 48px; font-size: 20px; }
  .chart-placeholder { height: 220px; }
  .project-table th { font-size: 13px; }
  .project-table td { font-size: 15px; }
  .badge { font-size: 12px; }
  .timeline-content p { font-size: 15px; }
  .timeline-content span { font-size: 13px; }
}

/* Extra Large (xl) - 1545px and up */
@media (min-width: 1545px) {
  .dashboard-section h2 { font-size: 24px; }
  .dashboard-section h3 { font-size: 20px; }
  .summary-cards h3, .summary-cards h4 { font-size: 16px; }
  .card-value { font-size: 22px; }
  .growth-positive, .growth-negative { font-size: 15px; }
  .card-icon { width: 52px; height: 52px; font-size: 22px; }
  .chart-placeholder { height: 240px; }
  .project-table th { font-size: 14px; }
  .project-table td { font-size: 16px; }
  .badge { font-size: 13px; }
  .timeline-content p { font-size: 16px; }
  .timeline-content span { font-size: 14px; }
}

/* Extra Extra Large (xxl) - 2138px and up */
@media (min-width: 2138px) {
  .dashboard-section h2 { font-size: 26px; }
  .dashboard-section h3 { font-size: 22px; }
  .summary-cards h3, .summary-cards h4 { font-size: 18px; }
  .card-value { font-size: 24px; }
  .growth-positive, .growth-negative { font-size: 16px; }
  .card-icon { width: 56px; height: 56px; font-size: 24px; }
  .chart-placeholder { height: 260px; }
  .project-table th { font-size: 15px; }
  .project-table td { font-size: 17px; }
  .badge { font-size: 14px; }
  .timeline-content p { font-size: 17px; }
  .timeline-content span { font-size: 15px; }
}

/* REMOVE OLD RESPONSIVE CSS */
/*
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
*/
</style>