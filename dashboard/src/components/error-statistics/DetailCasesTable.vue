<template>
  <v-card class="table-card" elevation="0">
    <v-card-title class="d-flex justify-space-between align-center py-3 px-5 table-card-header flex-wrap gap-y-3">
      <span class="table-card-title">상세 청구 오류 리스트</span>
      <div class="search-box">
        <div class="search-input-wrapper">
          <v-icon class="search-input-icon">mdi-magnify</v-icon>
          <input 
            type="text" 
            v-model="searchQueryModel" 
            placeholder="오류 내용 또는 요양기관명 검색..." 
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
          <th class="text-center" style="width: 55px;">No</th>
          <th v-if="currentFileKey === 'all'" class="text-left" style="width: 140px;">데이터 차수</th>
          <th class="text-left cursor-pointer user-select-none" @click="$emit('sort', 'hospital')" style="min-width: 160px;">
            요양기관명
            <v-icon size="x-small" :color="sortKey === 'hospital' ? 'blue-darken-2' : 'grey-lighten-1'">
              {{ sortKey === 'hospital' ? (sortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
            </v-icon>
          </th>
          <th class="text-left cursor-pointer user-select-none" @click="$emit('sort', 'category')" style="min-width: 260px;">
            청구실패 사유 (오류 내용)
            <v-icon size="x-small" :color="sortKey === 'category' ? 'blue-darken-2' : 'grey-lighten-1'">
              {{ sortKey === 'category' ? (sortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
            </v-icon>
          </th>
          <th class="text-right cursor-pointer user-select-none" @click="$emit('sort', 'count')" style="width: 100px;">
            실패 건수
            <v-icon size="x-small" :color="sortKey === 'count' ? 'blue-darken-2' : 'grey-lighten-1'">
              {{ sortKey === 'count' ? (sortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
            </v-icon>
          </th>
          <th class="text-center font-weight-bold" style="width: 130px;">H열 상태</th>
          <th class="text-center font-weight-bold" style="width: 130px;">액션</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(row, idx) in paginatedRows" :key="row.key">
          <td class="text-center text-slate-400 font-weight-medium">{{ (currentPage - 1) * itemsPerPage + idx + 1 }}</td>
          <td v-if="currentFileKey === 'all'" class="text-left text-slate-500 font-weight-medium">
            <span class="filekey-badge">
              {{ formatFileKey(row.fileKey) }}
            </span>
          </td>
          <td class="text-left font-weight-bold text-slate-800 text-truncate" :title="row.hospital">{{ row.hospital }}</td>
          <td class="text-left text-body-2 font-weight-medium text-wrap-pretty">{{ row.category }}</td>
          <td class="text-right font-weight-bold text-slate-700">{{ formatNumber(row.count) }} 건</td>
          <td class="text-center">
            <span class="custom-badge" :class="getStatusBadgeClass(row.state)">
              {{ row.state }}
            </span>
          </td>
          <td class="text-center">
            <button
                class="sleek-btn"
                :class="getActionButtonClass(row.state)"
                @click.prevent="$emit('toggle-row-state', row)"
            >
              {{ getRowButtonLabel(row.state) }}
            </button>
          </td>
        </tr>
        <tr v-if="filteredRows.length === 0">
          <td colspan="6" class="text-center py-10 text-slate-400">데이터가 없습니다.</td>
        </tr>
        </tbody>
      </v-table>
    </div>

    <!-- Mobile Card View -->
    <div class="mobile-card-list">
      <div v-for="(row, idx) in paginatedRows" :key="row.key" class="mobile-error-card mb-4 pa-4">
        <div class="d-flex align-center justify-space-between mb-3">
          <span class="mobile-card-no">#{{ (currentPage - 1) * itemsPerPage + idx + 1 }}</span>
          <span class="custom-badge" :class="getStatusBadgeClass(row.state)">
            {{ row.state }}
          </span>
        </div>

        <div v-if="currentFileKey === 'all'" class="mb-2">
          <div class="mobile-field-label">데이터 차수</div>
          <div class="mobile-field-value text-slate-600">
            <span class="filekey-badge">
              {{ formatFileKey(row.fileKey) }}
            </span>
          </div>
        </div>

        <div class="mb-2">
          <div class="mobile-field-label">요양기관명</div>
          <div class="mobile-field-value font-weight-bold text-slate-800">{{ row.hospital }}</div>
        </div>

        <div class="mb-2">
          <div class="mobile-field-label">청구실패 사유 (오류 내용)</div>
          <div class="mobile-field-value text-body-2 text-slate-700">{{ row.category }}</div>
        </div>

        <div class="mb-3">
          <div class="mobile-field-label">실패 건수</div>
          <div class="mobile-field-value font-weight-bold text-slate-900">{{ formatNumber(row.count) }} 건</div>
        </div>

        <div class="mt-4 pt-3 border-t">
          <button
              class="sleek-btn w-100 py-2 text-center"
              :class="getActionButtonClass(row.state)"
              @click.prevent="$emit('toggle-row-state', row)"
          >
            {{ getRowButtonLabel(row.state) }}
          </button>
        </div>
      </div>
      <div v-if="filteredRows.length === 0" class="text-center py-8 text-slate-400">데이터가 없습니다.</div>
    </div>

    <!-- Custom Pagination -->
    <div class="custom-pagination border-t py-3" v-if="totalPages > 1">
      <button class="pag-btn" :disabled="currentPage === 1" @click="currentPageModel = currentPage - 1">이전</button>
      <span class="pag-info">{{ currentPage }} / {{ totalPages }}</span>
      <button class="pag-btn" :disabled="currentPage === totalPages" @click="currentPageModel = currentPage + 1">다음</button>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  paginatedRows: any[];
  filteredRows: any[];
  currentPage: number;
  totalPages: number;
  itemsPerPage: number;
  searchQuery: string;
  sortKey: string;
  sortOrder: 'asc' | 'desc';
  currentFileKey?: string;
}>();

const emit = defineEmits<{
  (e: 'update:currentPage', page: number): void;
  (e: 'update:searchQuery', query: string): void;
  (e: 'toggle-row-state', row: any): void;
  (e: 'sort', key: string): void;
}>();

const currentPageModel = computed({
  get: () => props.currentPage,
  set: (val) => emit('update:currentPage', val)
});

const searchQueryModel = computed({
  get: () => props.searchQuery,
  set: (val) => emit('update:searchQuery', val)
});

function getStatusBadgeClass(state: string): string {
  if (state === '최종완료') return 'badge-resolved';
  if (state === '회신대기') return 'badge-pending';
  return 'badge-unconfirmed';
}

function getActionButtonClass(state: string): string {
  if (state === '최종완료') return 'sleek-btn-flat-warning';
  if (state === '회신대기') return 'sleek-btn-flat-info';
  return 'sleek-btn-flat-success';
}

function getRowButtonLabel(state: string): string {
  if (state === '최종완료') return '미확인 초기화';
  if (state === '회신대기') return '최종완료 처리';
  return '회신대기 처리';
}

function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num || 0);
}

function formatFileKey(key: string): string {
  if (!key) return '-';
  const clean = key.replace(/_/g, '-');
  if (/^\d{8}$/.test(key)) {
    return `${key.substring(0, 4)}.${key.substring(4, 6)}.${key.substring(6, 8)}`;
  }
  const parts = key.split('_');
  if (parts.length === 2 && /^\d{8}$/.test(parts[0]) && /^\d{8}$/.test(parts[1])) {
    const f1 = `${parts[0].substring(0, 4)}.${parts[0].substring(4, 6)}.${parts[0].substring(6, 8)}`;
    const f2 = `${parts[1].substring(0, 4)}.${parts[1].substring(4, 6)}.${parts[1].substring(6, 8)}`;
    if (f1 === f2) return f1;
    return `${f1} ~ ${f2}`;
  }
  return clean;
}
</script>

<style scoped>
.table-card {
  background: #ffffff;
  border-radius: 9px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  font-family: 'Plus Jakarta Sans', 'Pretendard', sans-serif;
}

.table-card-title { font-size: 14px; font-weight: 800; color: #0f172a; }
.table-card-header { border-bottom: 1px solid #f1f5f9; background-color: #ffffff; }

/* Unified Sleek Search Input */
.search-box {
  width: 250px;
}
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
}
.sleek-search-input:focus {
  border-color: #3b82f6;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.08);
}

.dashboard-table { width: 100%; border-collapse: collapse; }
.dashboard-table :deep(th) {
  background-color: #f8fafc !important;
  color: #475569 !important;
  font-size: 11.5px !important;
  font-weight: 700 !important;
  padding: 13px 18px !important;
  border-bottom: 1px solid #e2e8f0 !important;
  white-space: nowrap !important;
}
.dashboard-table :deep(td) {
  padding: 13px 18px !important;
  font-size: 13px !important;
  color: #334155 !important;
  border-bottom: 1px solid #f1f5f9 !important;
}
.dashboard-table :deep(tr:hover) { background-color: #f8fafc !important; }

/* Custom Badge Styles */
.custom-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 700;
  border-radius: 4px;
  line-height: 1;
  white-space: nowrap;
}

.filekey-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 700;
  border-radius: 6px;
  background-color: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
  line-height: 1;
  white-space: nowrap;
}
.badge-unconfirmed {
  background-color: #f1f5f9;
  color: #64748b;
}
.badge-pending {
  background-color: #fffbeb;
  color: #d97706;
}
.badge-resolved {
  background-color: #ecfdf5;
  color: #059669;
}

/* Sleek Button Styles */
.sleek-btn {
  border: 1px solid transparent;
  background-color: #f1f5f9;
  color: #475569;
  font-size: 11px;
  font-weight: 700;
  padding: 5px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  white-space: nowrap;
}
.sleek-btn-flat-success {
  background-color: #ecfdf5;
  color: #059669;
  border-color: rgba(16, 185, 129, 0.05);
}
.sleek-btn-flat-success:hover {
  background-color: #d1fae5;
}
.sleek-btn-flat-warning {
  background-color: #fff1f2;
  color: #e11d48;
  border-color: rgba(225, 29, 72, 0.05);
}
.sleek-btn-flat-warning:hover {
  background-color: #ffe4e6;
}
.sleek-btn-flat-info {
  background-color: #f0f9ff;
  color: #0284c7;
  border-color: rgba(2, 132, 199, 0.05);
}
.sleek-btn-flat-info:hover {
  background-color: #e0f2fe;
}

/* Pagination Styles (Matches dashboard) */
.custom-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.pag-btn {
  border: 1px solid #cbd5e1;
  background-color: #ffffff;
  color: #475569;
  font-size: 11.5px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}
.pag-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #f1f5f9;
  border-color: #e2e8f0;
}
.pag-btn:not(:disabled):hover {
  background-color: #f8fafc;
  border-color: #94a3b8;
}
.pag-info {
  font-size: 11.5px;
  font-weight: 700;
  color: #475569;
}

.border-t {
  border-top: 1px solid #f1f5f9;
}

/* Responsive Table / Card Switcher */
.desktop-table-view {
  display: block;
}
.mobile-card-list {
  display: none;
}

.cursor-pointer { cursor: pointer; }
.user-select-none { user-select: none; }

@media (max-width: 960px) {
  .desktop-table-view {
    display: none;
  }
  .mobile-card-list {
    display: block;
    padding: 16px;
    background-color: #f8fafc;
  }
  .mobile-error-card {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.05);
  }
  .mobile-card-no {
    font-size: 12px;
    font-weight: 700;
    color: #94a3b8;
  }
  .mobile-field-label {
    font-size: 10px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    margin-bottom: 2px;
  }
  .mobile-field-value {
    font-size: 13px;
    color: #334155;
    line-height: 1.4;
  }
  .w-100 {
    width: 100%;
  }
}
</style>
