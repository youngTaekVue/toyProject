<template>
  <v-card class="table-card emr-card-fixed" elevation="0">
    <v-card-title class="d-flex justify-space-between align-center py-3 px-5 table-card-header">
      <span class="table-card-title">EMR 사별 실패 내역</span>
      <div class="search-box">
        <div class="search-input-wrapper">
          <v-icon class="search-input-icon">mdi-magnify</v-icon>
          <input 
            type="text" 
            v-model="emrSearchModel" 
            placeholder="EMR사 검색..." 
            class="sleek-search-input" 
          />
        </div>
      </div>
    </v-card-title>
    
    <!-- Desktop Table View -->
    <div class="desktop-table-view">
      <v-table class="dashboard-table" style="table-layout: fixed;">
        <thead>
        <tr>
          <th class="text-center" style="width: 50px;">No</th>
          <th class="text-left">EMR사명</th>
          <th class="text-right" style="width: 110px;">실패 건수</th>
          <th class="text-right" style="width: 135px;">해결률</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(item, idx) in paginatedEmrs" :key="item.emr">
          <td class="text-center text-slate-400 font-weight-medium">
            {{ (emrPage - 1) * 10 + idx + 1 }}
          </td>
          <td class="text-left font-weight-medium text-slate-800 text-truncate" :title="item.emr">
            {{ item.emr }}
          </td>
          <td class="text-right font-weight-bold text-slate-700">
            {{ formatNumber(item.count) }}건 <span class="text-caption text-grey font-weight-medium">({{ formatNumber(item.casesCount) }}건)</span>
          </td>
          <td class="text-right">
            <div class="d-flex align-center justify-end">
              <span class="font-weight-bold mr-2 text-caption" :class="item.resolutionRate === 100 ? 'text-green' : 'text-orange'">
                {{ item.resolutionRate.toFixed(1) }}%
              </span>
              <div class="custom-progress-track">
                <div class="custom-progress-bar" :class="{ 'resolved': item.resolutionRate === 100 }" :style="{ width: item.resolutionRate + '%' }"></div>
              </div>
            </div>
          </td>
        </tr>
        <tr v-if="filteredEmrs.length === 0">
          <td colspan="4" class="text-center py-10 text-slate-400">데이터가 없습니다.</td>
        </tr>
        </tbody>
      </v-table>
    </div>

    <!-- Mobile Card List View -->
    <div class="mobile-card-list pa-4">
      <div v-for="(item, idx) in paginatedEmrs" :key="item.emr" class="emr-mobile-card mb-4 pa-4">
        <div class="mb-3 d-flex align-center justify-space-between">
          <span class="mobile-card-no">#{{ (emrPage - 1) * 10 + idx + 1 }}</span>
        </div>
        <div class="mb-3">
          <div class="mobile-field-label">EMR사명</div>
          <div class="mobile-field-value font-weight-bold text-slate-800">{{ item.emr }}</div>
        </div>
        <div class="mb-3">
          <div class="mobile-field-label">실패 건수</div>
          <div class="mobile-field-value font-weight-bold text-slate-700">
            {{ formatNumber(item.count) }}건 <span class="text-caption text-grey">({{ formatNumber(item.casesCount) }}건)</span>
          </div>
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
      <div v-if="filteredEmrs.length === 0" class="text-center py-10 text-slate-400">데이터가 없습니다.</div>
    </div>

    <!-- Custom Pagination inside Card Footer -->
    <div class="py-3 px-5 border-t d-flex align-center justify-center bg-slate-50 mt-auto" v-if="emrTotalPages > 1">
      <div class="custom-pagination">
        <button class="pag-btn" :disabled="emrPage === 1" @click="emrPageModel--">이전</button>
        <span class="pag-info">{{ emrPage }} / {{ emrTotalPages || 1 }}</span>
        <button class="pag-btn" :disabled="emrPage >= emrTotalPages" @click="emrPageModel++">다음</button>
      </div>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  paginatedEmrs: any[];
  filteredEmrs: any[];
  emrPage: number;
  emrSearch: string;
}>();

const emit = defineEmits<{
  (e: 'update:emrSearch', search: string): void;
  (e: 'update:emrPage', page: number): void;
}>();

const emrSearchModel = computed({
  get: () => props.emrSearch,
  set: (val) => emit('update:emrSearch', val)
});

const emrPageModel = computed({
  get: () => props.emrPage,
  set: (val) => emit('update:emrPage', val)
});

const emrTotalPages = computed(() => Math.ceil(props.filteredEmrs.length / 10));

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

/* search-box */
.search-box { width: 180px; }
.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}
.search-input-icon {
  position: absolute;
  left: 10px;
  color: #94a3b8;
  font-size: 16px !important;
  pointer-events: none;
}
.sleek-search-input {
  width: 100%;
  height: 32px;
  box-sizing: border-box;
  padding: 6px 10px 6px 32px;
  font-size: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background-color: #f8fafc;
  color: #334155;
  outline: none;
  transition: border-color 0.2s, background-color 0.2s, box-shadow 0.2s;
  font-family: 'Plus Jakarta Sans', 'Pretendard', sans-serif;
}
.sleek-search-input:focus {
  border-color: #3b82f6;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.08);
}

/* table and progress */
.dashboard-table {
  width: 100%;
  border-collapse: collapse;
}
.dashboard-table :deep(th) {
  background-color: #f8fafc !important;
  color: #475569 !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  padding: 10px 14px !important;
  border-bottom: 1px solid #f0f0f0 !important;
  white-space: nowrap !important;
}
.dashboard-table :deep(td) {
  padding: 10px 14px !important;
  font-size: 12.5px !important;
  color: #334155 !important;
  border-bottom: 1px solid #f0f0f0 !important;
}
.dashboard-table :deep(tr:hover) { background-color: #f8fafc !important; }

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

/* custom-pagination */
.custom-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.pag-btn {
  border: 1px solid #e2e8f0;
  background-color: #ffffff;
  color: #475569;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}
.pag-btn:hover:not(:disabled) {
  background-color: #f8fafc;
  color: #0f172a;
  border-color: #cbd5e1;
}
.pag-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.pag-info {
  font-size: 11.5px;
  font-weight: 700;
  color: #64748b;
}

.border-t {
  border-top: 1px solid #f1f5f9;
}
.text-green { color: #10b981 !important; }
.text-orange { color: #f59e0b !important; }

.emr-card-fixed {
  height: 650px;
  display: flex;
  flex-direction: column;
}
.emr-card-fixed :deep(.v-table) {
  flex: 1 1 auto;
}
.emr-card-fixed :deep(.v-table__wrapper) {
  flex: 1 1 auto;
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
  .emr-card-fixed {
    height: auto !important; /* Allow scroll height to adjust on mobile */
  }
}

.emr-mobile-card {
  background-color: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 9px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
  transition: all 0.2s ease;
}
.emr-mobile-card:active {
  transform: translateY(1px);
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.02);
}
.mobile-card-no {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  background-color: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
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
</style>
