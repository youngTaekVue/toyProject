<template>
  <v-card class="table-card" elevation="0">
    <v-card-title class="py-4 px-5 table-card-header">
      <span class="table-card-title">첨부 파일별 실패 내역</span>
    </v-card-title>
    
    <!-- Desktop Table View -->
    <div class="desktop-table-view">
      <v-table class="dashboard-table" style="table-layout: fixed;">
        <thead>
        <tr>
          <th class="text-left">첨부 파일</th>
          <th class="text-right" style="width: 120px;">실패 건수</th>
          <th class="text-right" style="width: 140px;">해결률</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="item in fileSummary" :key="item.fileName">
          <td class="text-left font-weight-medium text-slate-800">{{ item.displayName }}</td>
          <td class="text-right font-weight-bold text-slate-700">{{ formatNumber(item.count) }} 건</td>
          <td class="text-right">
            <div class="d-flex align-center justify-end">
              <span class="font-weight-bold mr-2 text-caption" :class="item.resolutionRate === 100 ? 'text-green' : 'text-orange'">{{ item.resolutionRate.toFixed(1) }}%</span>
              <div class="custom-progress-track">
                <div class="custom-progress-bar" :class="{ 'resolved': item.resolutionRate === 100 }" :style="{ width: item.resolutionRate + '%' }"></div>
              </div>
            </div>
          </td>
        </tr>
        </tbody>
      </v-table>
    </div>

    <!-- Mobile Card List View -->
    <div class="mobile-card-list pa-4">
      <div v-for="item in fileSummary" :key="item.fileName" class="file-mobile-card mb-4 pa-4">
        <div class="mb-3">
          <div class="mobile-field-label">첨부 파일</div>
          <div class="mobile-field-value font-weight-bold text-slate-800">{{ item.displayName }}</div>
        </div>
        <div class="mb-3">
          <div class="mobile-field-label">실패 건수</div>
          <div class="mobile-field-value font-weight-bold text-slate-700">{{ formatNumber(item.count) }} 건</div>
        </div>
        <div class="mb-1">
          <div class="mobile-field-label">해결률</div>
          <div class="mobile-field-value d-flex align-center mt-1" style="gap: 8px;">
            <span class="font-weight-bold text-caption mr-1" :class="item.resolutionRate === 100 ? 'text-green' : 'text-orange'">
              {{ item.resolutionRate.toFixed(1) }}%
            </span>
            <div class="custom-progress-track" style="width: 100px;">
              <div class="custom-progress-bar" :class="{ 'resolved': item.resolutionRate === 100 }" :style="{ width: item.resolutionRate + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </v-card>
</template>

<script setup lang="ts">
defineProps<{
  fileSummary: any[];
}>();

function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num || 0);
}
</script>

<style scoped>
.table-card {
  background: #ffffff;
  border-radius: 9px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}
.table-card-title { font-size: 14px; font-weight: 800; color: #0f172a; }
.table-card-header { border-bottom: 1px solid #f1f5f9; background-color: #ffffff; }

.dashboard-table {
  width: 100%;
  border-collapse: collapse;
}

/* Responsive View Toggle */
@media (min-width: 768px) {
  .mobile-card-list {
    display: none !important;
  }
}
@media (max-width: 767px) {
  .desktop-table-view {
    display: none !important;
  }
}

.file-mobile-card {
  background-color: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 9px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
  transition: all 0.2s ease;
}
.file-mobile-card:active {
  transform: translateY(1px);
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.02);
}
.mobile-field-label {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 2px;
}
.mobile-field-value {
  font-size: 13.5px;
  color: #0f172a;
}
.pa-4 {
  padding: 16px !important;
}
.mb-4 {
  margin-bottom: 16px !important;
}
.mb-3 {
  margin-bottom: 12px !important;
}
.mb-1 {
  margin-bottom: 4px !important;
}
.text-green { color: #10b981 !important; }
.text-orange { color: #f59e0b !important; }
.d-flex { display: flex !important; }
.align-center { align-items: center !important; }
.justify-end { justify-content: flex-end !important; }
.custom-progress-track {
  width: 50px;
  height: 6px;
  background-color: #f1f5f9;
  border-radius: 100px;
  overflow: hidden;
  position: relative;
  display: inline-block;
}
.custom-progress-bar {
  height: 100%;
  background-color: #f59e0b;
  border-radius: 100px;
  transition: width 0.4s ease;
}
.custom-progress-bar.resolved {
  background-color: #10b981;
}
</style>
