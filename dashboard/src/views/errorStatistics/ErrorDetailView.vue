<template>
  <v-container fluid class="error-detail-section pt-0">
    <!-- Header Block -->
    <div class="d-flex align-center mb-6">
      <v-btn
        icon="mdi-arrow-left"
        variant="elevated"
        elevation="1"
        class="mr-4 back-btn"
        color="white"
        @click="goBack"
      ></v-btn>
      <div>
        <h1 class="text-h5 font-weight-bold text-slate-800">
          [{{ targetType === 'hospital' ? '요양기관' : 'EMR사' }} 상세내역] {{ targetName }}
        </h1>
        <span class="text-subtitle-2 text-grey-500">청구 오류 건 단위 상세 데이터 및 상태 관리</span>
      </div>
    </div>

    <!-- Summary Metrics Cards -->
    <v-row class="mb-6" v-if="targetSummary">
      <v-col cols="12" sm="4">
        <div class="summary-card total-box">
          <div class="card-info">
            <span class="metric-label">총 청구오류 건수</span>
            <span class="metric-val text-blue">{{ formatNumber(targetSummary.count) }} <span class="unit">건</span></span>
          </div>
          <div class="metric-icon bg-blue-light">
            <v-icon color="blue">mdi-alert-circle</v-icon>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="4">
        <div class="summary-card pending-box">
          <div class="card-info">
            <span class="metric-label">회신대기 건수</span>
            <span class="metric-val text-orange">{{ formatNumber(targetSummary.sentCount) }} <span class="unit">건</span></span>
          </div>
          <div class="metric-icon bg-orange-light">
            <v-icon color="orange">mdi-email-send</v-icon>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="4">
        <div class="summary-card success-box">
          <div class="card-info">
            <span class="metric-label">최종완료 건수</span>
            <span class="metric-val text-green">{{ formatNumber(targetSummary.confirmedCount) }} <span class="unit">건</span></span>
          </div>
          <div class="metric-icon bg-green-light">
            <v-icon color="green">mdi-check-decagram</v-icon>
          </div>
        </div>
      </v-col>
    </v-row>
    <!-- EMR Hospital Filter Grid -->
    <div v-if="targetType === 'emr' && emrHospitalsSummary.length > 0" class="mb-6">
      <div class="text-subtitle-2 font-weight-bold mb-3 text-slate-800 d-flex align-center">
        <v-icon size="small" class="mr-1" color="primary">mdi-hospital-building</v-icon> EMR 사용 요양기관 필터
      </div>
      <v-row class="g-3">
        <!-- Total Card -->
        <v-col cols="12" sm="6" md="3">
          <v-card 
            :class="['metric-filter-card', selectedHospitalFilter === 'all' ? 'active-card' : '']"
            @click="selectedHospitalFilter = 'all'"
            elevation="0"
          >
            <div class="d-flex flex-column py-3 px-4">
              <span class="text-caption text-grey-darken-1 font-weight-medium">요양기관 전체</span>
              <div class="d-flex align-baseline mt-1 justify-space-between">
                <span class="text-h6 font-weight-bold text-slate-900">{{ allRows.length }} 건</span>
                <span class="text-caption font-weight-bold text-blue">{{ targetSummary.confirmedCount }} / {{ targetSummary.count }} 완료</span>
              </div>
            </div>
          </v-card>
        </v-col>
        <!-- Individual Hospital Cards -->
        <v-col cols="12" sm="6" md="3" v-for="h in emrHospitalsSummary" :key="h.hospital">
          <v-card 
            :class="['metric-filter-card', selectedHospitalFilter === h.hospital ? 'active-card' : '']"
            @click="selectedHospitalFilter = h.hospital"
            elevation="0"
          >
            <div class="d-flex flex-column py-3 px-4">
              <span class="text-caption text-grey-darken-1 font-weight-bold text-truncate" style="max-width: 180px;">{{ h.hospital }}</span>
              <div class="d-flex align-baseline mt-1 justify-space-between">
                <span class="text-h6 font-weight-bold text-slate-900">{{ h.casesCount }} 건</span>
                <span class="text-caption font-weight-bold text-green">{{ h.resolutionRate.toFixed(0) }}% 완료</span>
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- Table Card -->
    <v-card class="table-card" elevation="0">
      <v-card-title class="d-flex justify-space-between align-center py-4 px-6 table-card-header">
        <span class="table-card-title">상세 청구 오류 리스트</span>
        <div class="d-flex gap-2 align-center">
          <div class="search-box">
            <v-text-field
              v-model="searchQuery"
              density="compact"
              placeholder="오류 내용 또는 요양기관명 검색..."
              hide-details
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              class="search-input"
            ></v-text-field>
          </div>
        </div>
      </v-card-title>

      <v-table class="detail-table">
        <thead>
          <tr>
            <th class="text-center" style="width: 60px;">No</th>
            <th class="text-left" style="min-width: 180px;">요청 대상 요양기관명</th>
            <th class="text-left" style="min-width: 250px;">청구실패 사유 (오류 내용)</th>
            <th class="text-right" style="width: 120px;">실패 건수</th>
            <th class="text-center" style="width: 140px;">실시간 진행 상태</th>
            <th class="text-center" style="width: 120px;">액션</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in paginatedRows" :key="row.key">
            <td class="text-center">{{ (currentPage - 1) * itemsPerPage + idx + 1 }}</td>
            <td class="text-left">{{ row.hospital }}</td>
            <td class="text-left text-body-2 font-weight-medium text-wrap-pretty">{{ row.category }}</td>
            <td class="text-right font-weight-bold text-primary">{{ formatNumber(row.count) }} 건</td>
            <td class="text-center">
              <v-chip :color="getStatusColor(row.state)" variant="flat" size="small" class="status-chip-fixed">
                {{ row.state }}
              </v-chip>
            </td>
            <td class="text-center">
              <v-btn
                size="x-small"
                :color="row.state === '최종완료' ? 'grey-lighten-1' : 'primary'"
                variant="flat"
                class="action-btn-small"
                @click="toggleRowState(row)"
              >
                {{ getRowButtonLabel(row.state) }}
              </v-btn>
            </td>
          </tr>
          <tr v-if="filteredRows.length === 0">
            <td colspan="6" class="text-center py-10 text-grey">데이터가 없습니다.</td>
          </tr>
        </tbody>
      </v-table>

      <!-- Pagination -->
      <div class="d-flex justify-center align-center py-4 border-t" v-if="totalPages > 1">
        <v-pagination
          v-model="currentPage"
          :length="totalPages"
          total-visible="6"
          density="compact"
          active-color="primary"
        ></v-pagination>
      </div>
    </v-card>

    <!-- Overlay Loader -->
    <v-overlay :model-value="isLoading" class="align-center justify-center" persistent>
      <v-progress-circular color="primary" indeterminate size="64"></v-progress-circular>
    </v-overlay>
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

// Types matching Dashboard.vue
type RowState = '미확인' | '회신대기' | '최종완료';

interface ErrorDetail {
  no: number;
  fileKey: string;
  hospital: string;
  institutionId: string;
  emr: string;
  category: string;
  details: string;
  visitDate: string;
  uuid: string;
  patient: string;
  birthDate: string;
  state: RowState;
}

interface ClaimCase {
  key: string;
  hospital: string;
  institutionId: string;
  emr: string;
  category: string;
  patient: string;
  birthDate: string;
  count: number;
  state: RowState;
  fileKey: string;
  rows: ErrorDetail[];
}

const route = useRoute();
const router = useRouter();

// Route query params
const targetType = ref<'hospital' | 'emr'>((route.query.type as 'hospital' | 'emr') || 'hospital');
const targetName = ref<string>((route.query.name as string) || '');

// Constants
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000') + '/api/errorStatistics';

// States
const allRows = ref<ClaimCase[]>([]);
const persistedStates = ref<Record<string, RowState>>({});
const isLoading = ref(false);
const searchQuery = ref('');
const currentPage = ref(1);
const itemsPerPage = 10;
const selectedHospitalFilter = ref<string>('all');

function getGroupKey(row: { fileKey: string; hospital: string; category: string; patient: string; birthDate: string }): string {
  return `${row.fileKey}|${row.hospital}|${row.category.substring(0, 30)}|${row.patient}|${row.birthDate}`;
}

function goBack() {
  router.push('/error-statistics');
}

// 1. Fetch data from all files on mount
async function loadData() {
  isLoading.value = true;
  try {
    const filesRes = await fetch(`${API_BASE_URL}/files?t=${Date.now()}`);
    if (!filesRes.ok) throw new Error('Failed to load file list');
    const filesJson = await filesRes.json();
    
    let fileKeys: string[] = [];
    if (filesJson.success && Array.isArray(filesJson.files)) {
      fileKeys = filesJson.files;
    }

    const loadedDetailRows: ErrorDetail[] = [];
    const tempPersistedStates: Record<string, RowState> = {};

    for (const fileKey of fileKeys) {
      const dataRes = await fetch(`${API_BASE_URL}/data/${fileKey}?t=${Date.now()}`);
      if (!dataRes.ok) continue;
      const dataJson = await dataRes.json();
      if (dataJson.success && Array.isArray(dataJson.rows)) {
        dataJson.rows.forEach((row: ErrorDetail) => {
          loadedDetailRows.push(row);
          const key = getGroupKey(row);
          tempPersistedStates[key] = row.state;
        });
      }
    }

    persistedStates.value = tempPersistedStates;
    
    // Group details by getGroupKey
    const groups: Record<string, ErrorDetail[]> = {};
    loadedDetailRows.forEach(row => {
      const key = getGroupKey(row);
      if (!groups[key]) groups[key] = [];
      groups[key].push(row);
    });

    const cases: ClaimCase[] = Object.entries(groups).map(([groupKey, rows]) => {
      const first = rows[0];
      return {
        key: groupKey,
        hospital: first.hospital,
        institutionId: first.institutionId,
        emr: first.emr,
        category: first.category,
        patient: first.patient,
        birthDate: first.birthDate,
        count: rows.length,
        state: tempPersistedStates[groupKey] || '미확인',
        fileKey: first.fileKey,
        rows
      };
    });

    // Filter by targetType and targetName
    allRows.value = cases.filter(c => 
      targetType.value === 'hospital' ? c.hospital === targetName.value : c.emr === targetName.value
    );

    // Sort cases by count descending
    allRows.value.sort((a, b) => b.count - a.count);
    
    // Reset selected filter
    selectedHospitalFilter.value = 'all';

  } catch (error) {
    console.error('상세 데이터 로드 실패:', error);
  } finally {
    isLoading.value = false;
  }
}

// 2. Computed summary metrics
const targetSummary = computed(() => {
  if (allRows.value.length === 0) {
    return { count: 0, sentCount: 0, confirmedCount: 0 };
  }
  const count = allRows.value.length;
  const sentCount = allRows.value.filter(c => persistedStates.value[c.key] === '회신대기').length;
  const confirmedCount = allRows.value.filter(c => persistedStates.value[c.key] === '최종완료').length;
  return { count, sentCount, confirmedCount };
});

const emrHospitalsSummary = computed(() => {
  if (targetType.value !== 'emr') return [];
  const summaryMap: Record<string, { count: number; casesCount: number; resolvedCasesCount: number; resolutionRate: number }> = {};
  
  allRows.value.forEach(c => {
    if (!summaryMap[c.hospital]) {
      summaryMap[c.hospital] = { count: 0, casesCount: 0, resolvedCasesCount: 0, resolutionRate: 0 };
    }
    summaryMap[c.hospital].count += c.count;
    summaryMap[c.hospital].casesCount++;
    const state = persistedStates.value[c.key] || '미확인';
    if (state === '최종완료') {
      summaryMap[c.hospital].resolvedCasesCount++;
    }
  });

  return Object.entries(summaryMap).map(([hospital, data]) => {
    const resolutionRate = data.casesCount > 0 ? (data.resolvedCasesCount / data.casesCount) * 100 : 0;
    return {
      hospital,
      count: data.count,
      casesCount: data.casesCount,
      resolutionRate
    };
  }).sort((a, b) => b.casesCount - a.casesCount);
});

// 3. Filtering & Pagination
const filteredRows = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  
  // Re-apply states reactively
  let mapped = allRows.value.map(row => {
    return {
      ...row,
      state: persistedStates.value[row.key] || '미확인'
    };
  });

  // Apply hospital sub-filter if targetType is emr
  if (targetType.value === 'emr' && selectedHospitalFilter.value !== 'all') {
    mapped = mapped.filter(r => r.hospital === selectedHospitalFilter.value);
  }

  if (!query) return mapped;
  return mapped.filter(r => 
    r.hospital.toLowerCase().includes(query) || 
    r.category.toLowerCase().includes(query)
  );
});

const totalPages = computed(() => Math.ceil(filteredRows.value.length / itemsPerPage));

const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredRows.value.slice(start, start + itemsPerPage);
});

// 4. Actions
async function toggleRowState(claimCase: ClaimCase) {
  const key = claimCase.key;
  const currentState = persistedStates.value[key] || '미확인';
  
  let nextState: RowState = '미확인';
  if (currentState === '미확인') nextState = '회신대기';
  else if (currentState === '회신대기') nextState = '최종완료';

  isLoading.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fileKey: claimCase.fileKey,
        fileKeys: [claimCase.fileKey],
        hospital: claimCase.hospital,
        patient: claimCase.patient,
        birthDate: claimCase.birthDate,
        category: claimCase.category,
        state: nextState
      })
    });

    if (res.ok) {
      persistedStates.value[key] = nextState;
    } else {
      console.error('상태 변경 API 실패');
    }
  } catch (error) {
    console.error('상태 변경 실패:', error);
  } finally {
    isLoading.value = false;
  }
}

function getRowButtonLabel(state: RowState): string {
  if (state === '미확인') return '회신대기';
  if (state === '회신대기') return '최종완료';
  return '되돌리기';
}

function getStatusColor(state: RowState): string {
  if (state === '회신대기') return '#e28743'; // Orange
  if (state === '최종완료') return '#2dce89'; // Green
  return '#718096'; // Grey
}

function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num);
}

watch(searchQuery, () => {
  currentPage.value = 1;
});

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.error-detail-section {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
  background-color: #f8fafc;
  min-height: 100vh;
  letter-spacing: -0.02em;
}

.back-btn {
  border: 1px solid #e2e8f0 !important;
  border-radius: 8px !important;
  text-transform: none !important;
  font-weight: 600 !important;
  transition: all 0.2s ease;
}
.back-btn:hover {
  background-color: #f1f5f9 !important;
  border-color: #cbd5e1 !important;
  transform: translateX(-2px);
}

/* Metric Cards with premium shadows & gradients */
.summary-card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px -2px rgba(50, 50, 93, 0.04), 0 2px 8px -1px rgba(0, 0, 0, 0.02);
  padding: 22px 26px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(226, 232, 240, 0.8);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.01);
  border-color: rgba(203, 213, 225, 0.8);
}

.card-info {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}

.metric-val {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.metric-val .unit {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  margin-left: 2px;
}

.metric-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}
.summary-card:hover .metric-icon {
  transform: scale(1.1) rotate(5deg);
}

.bg-blue-light { background-color: #eff6ff; }
.bg-orange-light { background-color: #fffbeb; }
.bg-green-light { background-color: #ecfdf5; }

.text-blue { color: #2563eb; }
.text-orange { color: #d97706; }
.text-green { color: #059669; }

/* Interactive Metric Filter Cards */
.metric-filter-card {
  border: 1px solid #e2e8f0 !important;
  border-radius: 12px !important;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  background-color: #ffffff !important;
  position: relative;
  overflow: hidden;
}
.metric-filter-card:hover {
  border-color: #3b82f6 !important;
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.04) !important;
}
.metric-filter-card.active-card {
  border-color: #3b82f6 !important;
  border-width: 2px !important;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important;
  box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.15) !important;
}

/* Premium Table Styling */
.table-card {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 4px 20px -2px rgba(50, 50, 93, 0.04);
  overflow: hidden;
}

.table-card-title {
  font-size: 17px;
  font-weight: 800;
  color: #1e293b;
  letter-spacing: -0.02em;
}

.table-card-header {
  border-bottom: 1px solid #f1f5f9;
  background-color: #ffffff;
}

.search-box {
  width: 240px;
}

.search-input :deep(.v-field) {
  border-radius: 8px !important;
  background-color: #f8fafc !important;
}

.search-input :deep(.v-field__outline) {
  --v-field-border-width: 1px !important;
  color: #e2e8f0 !important;
}
.search-input :deep(.v-field--focused .v-field__outline) {
  color: #3b82f6 !important;
}

.search-input :deep(.v-field__input) {
  padding-top: 6px !important;
  padding-bottom: 6px !important;
  min-height: 36px !important;
  font-size: 13px !important;
}

.detail-table {
  width: 100%;
}

.detail-table :deep(th) {
  background-color: #f8fafc !important;
  color: #475569 !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  padding: 14px 18px !important;
  border-bottom: 1px solid #e2e8f0 !important;
  white-space: nowrap !important;
  letter-spacing: 0.03em;
}

.detail-table :deep(td) {
  padding: 14px 18px !important;
  font-size: 13px !important;
  color: #334155 !important;
  border-bottom: 1px solid #f1f5f9 !important;
  white-space: nowrap !important;
  transition: all 0.2s ease;
}

.detail-table :deep(tr) {
  position: relative;
  transition: background-color 0.2s ease;
}

.detail-table :deep(tr:hover) {
  background-color: #f8fafc !important;
}

/* Hover sliding line indicator */
.detail-table :deep(tr::after) {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background-color: #3b82f6;
  opacity: 0;
  transition: opacity 0.2s ease;
}
.detail-table :deep(tr:hover::after) {
  opacity: 1;
}

/* Semi-transparent Pastel Badge States */
.status-chip-fixed {
  font-weight: 700 !important;
  font-size: 11px !important;
  padding: 0 12px !important;
  border-radius: 6px !important;
  height: 24px !important;
  letter-spacing: -0.01em;
}
.status-chip-fixed[color="#718096"] {
  background-color: #f1f5f9 !important;
  color: #64748b !important;
}
.status-chip-fixed[color="#e28743"] {
  background-color: #fff3e0 !important;
  color: #e65100 !important;
}
.status-chip-fixed[color="#2dce89"] {
  background-color: #e8f5e9 !important;
  color: #2e7d32 !important;
}

/* Capsule buttons with micro-interactions */
.action-btn-small {
  background-color: #f8fafc !important;
}
.metric-filter-card.active-card {
  border-color: #3b82f6 !important;
  border-width: 2px !important;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1), 0 2px 4px -1px rgba(59, 130, 246, 0.06) !important;
  background-color: #eff6ff !important;
}
</style>
