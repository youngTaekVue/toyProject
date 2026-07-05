<template>
  <!-- 대시보드 전체 폭을 제한하여 늘어짐 방지 -->
  <div class="dashboard-wrapper">
    <v-container fluid class="error-monitor-section pt-3 px-4 pb-8">

      <!-- Top Header Row with File Select -->
      <div class="d-flex align-center justify-space-between mb-6 mt-1 flex-wrap gap-y-3">
        <div>
          <h2 class="text-subtitle-1 font-weight-bold text-slate-800 mb-0 d-flex align-center">
            <v-icon color="primary" class="mr-2" size="small">mdi-chart-timeline-variant</v-icon>
            실시간 청구실패 에러 현황판
          </h2>
        </div>
        <div class="d-flex align-center">
          <span class="text-caption font-weight-bold text-slate-600 mr-2.5 text-no-wrap">데이터 차수 선택:</span>
          <select v-model="selectedFileKey" class="sleek-select">
            <option v-for="opt in fileOptions" :key="opt.value" :value="opt.value">
              {{ opt.title }}
            </option>
          </select>
        </div>
      </div>

      <!-- 1. Top Key Metrics Cards -->
      <KpiCards :kpiMetrics="kpiMetrics" />

      <!-- 2. Visual Chart Analytics Section -->
      <div class="content-split-container mb-6">
        <!-- 하단 왼쪽: 에러 발생 및 기관 유입 트렌드 (혼합 차트) -->
        <div class="main-split-left">
          <TrendMixedChart :options="trendChartOptions" :series="trendChartSeries" />
        </div>

        <!-- 하단 오른쪽: 가장 많이 발생한 에러 유형 TOP 5 (가로 막대 랭킹) -->
        <div class="main-split-right">
          <TopErrorsChart :claimCases="groupedClaimCases" />
        </div>
      </div>

      <!-- 3. Main Content Tables Area -->
      <div class="content-split-container mb-6">
        <!-- 왼쪽 테이블 영역 (요양기관별 실패 내역) -->
        <div class="main-split-left">
          <HospitalFailureTable
            v-model:hospitalPage="hospitalPage"
            v-model:selectedStatusFilter="selectedStatusFilter"
            v-model:hospitalSearch="hospitalSearch"
            :paginatedHospitals="paginatedHospitals"
            :filteredHospitals="filteredHospitals"
            :hospitalTotalPages="hospitalTotalPages"
            :itemsPerPage="itemsPerPage"
            :sortKey="sortKey"
            :sortOrder="sortOrder"
            :persistedStates="persistedStates"
            :isLoading="isLoading"
            @sort="handleSort"
            @open-detail="openHospitalDetail"
            @toggle-state="toggleHospitalState"
          />
        </div>

        <!-- 오른쪽 테이블 영역 (EMR 사별 실패 내역) -->
        <div class="main-split-right">
          <EmrVendorFailureTable
            v-model:emrSearch="emrSearch"
            v-model:emrPage="emrPage"
            :paginatedEmrs="paginatedEmrs"
            :filteredEmrs="filteredEmrs"
          />
        </div>
      </div>

      <!-- 4. 하단 전체 영역 (첨부 파일별 실패 내역) -->
      <div class="content-split-container mb-6 mx-1">
        <AttachedFileFailureTable :fileSummary="fileSummary" />
      </div>

      <!-- Overlay Loader -->
      <v-overlay :model-value="isLoading" class="align-center justify-center" persistent>
        <v-progress-circular color="primary" indeterminate size="64"></v-progress-circular>
      </v-overlay>

    </v-container>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

// Component imports
import KpiCards from '@/components/error-statistics/KpiCards.vue';
import TrendMixedChart from '@/components/error-statistics/TrendMixedChart.vue';
import TopErrorsChart from '@/components/error-statistics/TopErrorsChart.vue';
import HospitalFailureTable from '@/components/error-statistics/HospitalFailureTable.vue';
import AttachedFileFailureTable from '@/components/error-statistics/AttachedFileFailureTable.vue';
import EmrVendorFailureTable from '@/components/error-statistics/EmrVendorFailureTable.vue';

const router = useRouter();
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

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000') + '/api/errorStatistics';

const allFileKeys = ref<string[]>([]);
const selectedFileKey = ref<string>('');

const sortKey = ref<string>('hospital');
const sortOrder = ref<'desc' | 'asc'>('asc');

const rawRows = ref<ErrorDetail[]>([]);
const persistedStates = ref<Record<string, RowState>>({});
const isLoading = ref(false);

const hospitalSearch = ref('');
const hospitalPage = ref(1);
const itemsPerPage = 10;
const emrSearch = ref('');
const emrPage = ref(1);

const selectedStatusFilter = ref<'all' | 'active' | 'resolved'>('all');

function getGroupKey(row: ErrorDetail): string {
  let cleanDetails = row.details || '';
  if (cleanDetails.includes('===')) {
    cleanDetails = cleanDetails.split(/={3,}/)[0].trim();
  }
  const errorTitle = row.category && !row.category.includes('미분류') ? row.category : cleanDetails.substring(0, 40);
  return `${row.fileKey}|${row.hospital.trim()}|${errorTitle}`;
}

function handleSort(key: string) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortOrder.value = 'desc';
  }
}

const fileOptions = computed(() => {
  return allFileKeys.value
      .map(key => ({ title: key.replace(/_/g, '-'), value: key }))
      .sort((a, b) => b.value.localeCompare(a.value));
});

const normalizedRows = computed<ErrorDetail[]>(() => {
  return rawRows.value
      .filter(row => row.hospital && !row.hospital.includes('청구실패 사유') && !row.hospital.startsWith('■'))
      .map(row => ({ ...row, state: persistedStates.value[getGroupKey(row)] || '미확인' }));
});

const allGroupedClaimCases = computed<ClaimCase[]>(() => {
  const groups: Record<string, ErrorDetail[]> = {};
  normalizedRows.value.forEach(row => {
    const key = getGroupKey(row);
    if (!groups[key]) groups[key] = [];
    groups[key].push(row);
  });

  return Object.entries(groups).map(([groupKey, rows]) => {
    const first = rows[0];
    let cleanDetails = first.details || '';
    if (cleanDetails.includes('===')) {
      cleanDetails = cleanDetails.split(/={3,}/)[0].trim();
    }
    const errorTitle = first.category && !first.category.includes('미분류') ? first.category : cleanDetails.substring(0, 40);

    return {
      key: groupKey, hospital: first.hospital.trim(), institutionId: first.institutionId,
      emr: first.emr, category: errorTitle,
      patient: rows.length > 1 ? `${first.patient} 외 ${rows.length - 1}명` : first.patient,
      birthDate: first.birthDate, count: rows.length,
      state: persistedStates.value[groupKey] || '미확인', fileKey: first.fileKey, rows
    };
  });
});

const groupedClaimCases = computed<ClaimCase[]>(() => {
  if (!selectedFileKey.value) return allGroupedClaimCases.value;
  return allGroupedClaimCases.value.filter(c => c.fileKey === selectedFileKey.value);
});

const kpiMetrics = computed(() => {
  const sortedFiles = [...allFileKeys.value].sort((a, b) => a.localeCompare(b));
  const currIndex = sortedFiles.indexOf(selectedFileKey.value);
  const prevFileKey = currIndex > 0 ? sortedFiles[currIndex - 1] : null;

  const currCases = groupedClaimCases.value;
  const prevCases = prevFileKey ? allGroupedClaimCases.value.filter(c => c.fileKey === prevFileKey) : [];

  const currRawFailures = currCases.reduce((sum, c) => sum + c.count, 0);
  const currFailures = currCases.length;
  const currHospitals = new Set(currCases.map(c => c.hospital)).size;

  const currRawUnconfirmed = currCases.filter(c => c.state === '미확인').reduce((sum, c) => sum + c.count, 0);
  const currUnconfirmed = currCases.filter(c => c.state === '미확인').length;

  const currRawPending = currCases.filter(c => c.state === '회신대기').reduce((sum, c) => sum + c.count, 0);
  const currPending = currCases.filter(c => c.state === '회신대기').length;

  const currRawResolved = currCases.filter(c => c.state === '최종완료').reduce((sum, c) => sum + c.count, 0);
  const currResolved = currCases.filter(c => c.state === '최종완료').length;

  const prevRawFailures = prevCases.reduce((sum, c) => sum + c.count, 0);
  const prevHospitals = prevCases.length > 0 ? new Set(prevCases.map(c => c.hospital)).size : 0;
  const prevRawUnconfirmed = prevCases.filter(c => c.state === '미확인').reduce((sum, c) => sum + c.count, 0);
  const prevRawPending = prevCases.filter(c => c.state === '회신대기').reduce((sum, c) => sum + c.count, 0);
  const prevRawResolved = prevCases.filter(c => c.state === '최종완료').reduce((sum, c) => sum + c.count, 0);

  const failuresTrend = prevRawFailures > 0 ? ((currRawFailures - prevRawFailures) / prevRawFailures) * 100 : 0;
  const hospitalsTrend = prevHospitals > 0 ? ((currHospitals - prevHospitals) / prevHospitals) * 100 : 0;
  const unconfirmedTrend = prevRawUnconfirmed > 0 ? ((currRawUnconfirmed - prevRawUnconfirmed) / prevRawUnconfirmed) * 100 : 0;
  const pendingTrend = prevRawPending > 0 ? ((currRawPending - prevRawPending) / prevRawPending) * 100 : 0;
  const resolvedTrend = prevRawResolved > 0 ? ((currRawResolved - prevRawResolved) / prevRawResolved) * 100 : 0;

  return {
    rawFailures: currRawFailures, failures: currFailures, failuresTrend,
    hospitals: currHospitals, hospitalsTrend,
    rawUnconfirmed: currRawUnconfirmed, unconfirmed: currUnconfirmed, unconfirmedTrend,
    rawPending: currRawPending, pending: currPending, pendingTrend,
    rawResolved: currRawResolved, resolved: currResolved, resolvedTrend,
    hasPrev: prevFileKey !== null
  };
});

const trendChartData = computed(() => {
  const sortedFiles = [...allFileKeys.value].sort((a, b) => a.localeCompare(b));
  const categories = sortedFiles.map(key => {
    const parts = key.split('_');
    if (parts.length === 2 && parts[0].length === 8 && parts[1].length === 8) {
      const f1 = `${parts[0].substring(4, 6)}/${parts[0].substring(6, 8)}`;
      const f2 = `${parts[1].substring(4, 6)}/${parts[1].substring(6, 8)}`;
      return `${f1} ~ ${f2}`;
    }
    return key.replace(/_/g, '-');
  });
  const failureCounts: number[] = [];
  const hospitalCounts: number[] = [];

  sortedFiles.forEach(fileKey => {
    const fileCases = allGroupedClaimCases.value.filter(c => c.fileKey === fileKey);
    failureCounts.push(fileCases.reduce((sum, c) => sum + c.count, 0));
    const hospitals = new Set(fileCases.map(c => c.hospital));
    hospitalCounts.push(hospitals.size);
  });

  return { categories, failureCounts, hospitalCounts };
});

const trendChartSeries = computed(() => [
  { name: '오류 발생 건수 (건)', type: 'column', data: trendChartData.value.failureCounts },
  { name: '대상 요양기관 수 (곳)', type: 'line', data: trendChartData.value.hospitalCounts }
]);

const trendChartOptions = computed(() => ({
  chart: { id: 'trend-mixed-chart', toolbar: { show: false }, fontFamily: 'Pretendard, sans-serif' },
  stroke: { width: [0, 3], curve: 'smooth' },
  colors: ['#3b82f6', '#ff3366'],
  plotOptions: { bar: { columnWidth: '40%', borderRadius: 6 } },
  markers: {
    size: 5,
    colors: ['#ff3366'],
    strokeColors: '#ffffff',
    strokeWidth: 2,
    hover: { size: 7 }
  },
  dataLabels: {
    enabled: false
  },
  xaxis: { categories: trendChartData.value.categories, axisBorder: { show: false } },
  yaxis: [
    { title: { text: '오류 건수', style: { color: '#64748b', fontWeight: 600 } }, labels: { formatter: (val: number) => val.toLocaleString() } },
    { opposite: true, title: { text: '기관 수', style: { color: '#64748b', fontWeight: 600 } }, labels: { formatter: (val: number) => Math.round(val) } }
  ],
  grid: { borderColor: '#f1f5f9' },
  legend: { position: 'bottom', horizontalAlign: 'center', boxWidth: 12 }
}));


const groupedHospitals = computed(() => {
  const hospitalCounts: Record<string, { count: number; cases: ClaimCase[] }> = {};
  groupedClaimCases.value.forEach(claimCase => {
    if (!hospitalCounts[claimCase.hospital]) hospitalCounts[claimCase.hospital] = { count: 0, cases: [] };
    hospitalCounts[claimCase.hospital].count += claimCase.count;
    hospitalCounts[claimCase.hospital].cases.push(claimCase);
  });
  return Object.entries(hospitalCounts).map(([hospital, data]) => ({
    hospital, count: data.count, casesCount: data.cases.length,
    resolutionRate: data.cases.length > 0 ? (data.cases.filter(c => c.state === '최종완료').length / data.cases.length) * 100 : 0,
    cases: data.cases
  }));
});

const filteredHospitals = computed(() => {
  const search = hospitalSearch.value.trim().toLowerCase();
  let list = groupedHospitals.value;

  if (search) {
    list = list.filter(h => h.hospital.toLowerCase().includes(search));
  }

  if (selectedStatusFilter.value === 'active') {
    list = list.filter(h => h.resolutionRate < 100);
  } else if (selectedStatusFilter.value === 'resolved') {
    list = list.filter(h => h.resolutionRate === 100);
  }

  return list.slice().sort((a, b) => {
    const valA = a[sortKey.value as keyof typeof a];
    const valB = b[sortKey.value as keyof typeof b];
    const modifier = sortOrder.value === 'asc' ? 1 : -1;
    if (typeof valA === 'string' && typeof valB === 'string') return valA.localeCompare(valB) * modifier;
    return (Number(valA) - Number(valB)) * modifier;
  });
});

const hospitalTotalPages = computed(() => Math.ceil(filteredHospitals.value.length / itemsPerPage));
const paginatedHospitals = computed(() => {
  return filteredHospitals.value.slice((hospitalPage.value - 1) * itemsPerPage, hospitalPage.value * itemsPerPage);
});

const groupedEmrs = computed(() => {
  const emrCounts: Record<string, { count: number; cases: ClaimCase[] }> = {};
  groupedClaimCases.value.forEach(claimCase => {
    if (!emrCounts[claimCase.emr]) emrCounts[claimCase.emr] = { count: 0, cases: [] };
    emrCounts[claimCase.emr].count += claimCase.count;
    emrCounts[claimCase.emr].cases.push(claimCase);
  });
  return Object.entries(emrCounts).map(([emr, data]) => ({
    emr, count: data.count, casesCount: data.cases.length,
    resolutionRate: data.cases.length > 0 ? (data.cases.filter(c => c.state === '최종완료').length / data.cases.length) * 100 : 0,
    cases: data.cases
  }));
});

const filteredEmrs = computed(() => {
  const search = emrSearch.value.trim().toLowerCase();
  let list = groupedEmrs.value;
  if (search) {
    list = list.filter(e => e.emr.toLowerCase().includes(search));
  }
  return list.slice().sort((a, b) => {
    if (a.emr === '미지정') return 1;
    if (b.emr === '미지정') return -1;
    return a.emr.localeCompare(b.emr);
  });
});

const paginatedEmrs = computed(() => {
  return filteredEmrs.value.slice((emrPage.value - 1) * itemsPerPage, emrPage.value * itemsPerPage);
});

const fileSummary = computed(() => {
  const fileStats: Record<string, { totalCases: number; resolvedCases: number }> = {};
  allFileKeys.value.forEach(key => fileStats[key] = { totalCases: 0, resolvedCases: 0 });
  allGroupedClaimCases.value.forEach(claimCase => {
    if (claimCase.fileKey && fileStats[claimCase.fileKey]) {
      fileStats[claimCase.fileKey].totalCases += claimCase.count;
      if (claimCase.state === '최종완료') fileStats[claimCase.fileKey].resolvedCases += claimCase.count;
    }
  });
  return Object.entries(fileStats).sort((a, b) => a[0].localeCompare(b[0])).map(([fileKey, data]) => ({
    fileName: fileKey, displayName: fileKey.replace(/_/g, '-'), count: data.totalCases,
    resolutionRate: data.totalCases > 0 ? (data.resolvedCases / data.totalCases) * 100 : 0
  }));
});

async function loadExcelData() {
  isLoading.value = true;
  try {
    const filesRes = await fetch(`${API_BASE_URL}/files?t=${Date.now()}`);
    if (!filesRes.ok) throw new Error('Failed to load file list');
    const filesJson = await filesRes.json();

    if (filesJson.success && Array.isArray(filesJson.files)) {
      allFileKeys.value = filesJson.files;
      if (filesJson.files.length > 0 && !selectedFileKey.value) {
        const sorted = [...filesJson.files].sort((a, b) => b.localeCompare(a));
        selectedFileKey.value = sorted[0];
      }
    }

    const loadedRows: ErrorDetail[] = [];
    const tempPersistedStates: Record<string, RowState> = {};

    for (const fileKey of allFileKeys.value) {
      const dataRes = await fetch(`${API_BASE_URL}/data/${fileKey}?t=${Date.now()}`);
      if (!dataRes.ok) continue;
      const dataJson = await dataRes.json();
      if (dataJson.success && Array.isArray(dataJson.rows)) {
        dataJson.rows.forEach((row: ErrorDetail) => {
          loadedRows.push(row);
          tempPersistedStates[getGroupKey(row)] = row.state;
        });
      }
    }
    rawRows.value = loadedRows;
    persistedStates.value = tempPersistedStates;
  } catch (error) {
    console.error('Data loading error:', error);
  } finally {
    isLoading.value = false;
  }
}

function openHospitalDetail(item: { hospital: string }) {
  router.push({
    path: '/error-statistics/detail',
    query: {
      type: 'hospital',
      name: item.hospital,
      fileKey: selectedFileKey.value
    }
  });
}

function getHospitalOverallState(item: any): RowState {
  if (!item || !item.cases) return '미확인';
  const states = item.cases.map((c: any) => persistedStates.value[c.key] || '미확인');
  if (states.includes('미확인')) return '미확인';
  if (states.includes('회신대기')) return '회신대기';
  return '최종완료';
}

async function toggleHospitalState(item: any) {
  const currentState = getHospitalOverallState(item);
  let nextState: RowState = '회신대기';
  
  if (currentState === '미확인') {
    nextState = '회신대기';
  } else if (currentState === '회신대기') {
    nextState = '최종완료';
  } else if (currentState === '최종완료') {
    nextState = '미확인';
  }

  isLoading.value = true;
  try {
    const allHospitalRows = item.cases.flatMap((c: any) => c.rows);
    const res = await fetch(`${API_BASE_URL}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fileKey: selectedFileKey.value,
        hospital: item.hospital,
        state: nextState,
        rows: allHospitalRows
      })
    });

    if (res.ok) {
      allHospitalRows.forEach((r: any) => {
        const key = getGroupKey(r);
        persistedStates.value[key] = nextState;
      });
    } else {
      console.error('Hospital state update API failed');
    }
  } catch (error) {
    console.error('Error toggling hospital state:', error);
  } finally {
    isLoading.value = false;
  }
}

watch(
  [hospitalSearch, emrSearch, selectedFileKey, selectedStatusFilter, sortKey, sortOrder],
  () => {
    hospitalPage.value = 1;
    emrPage.value = 1;
  }
);
onMounted(() => { loadExcelData(); });
</script>

<style scoped>
.dashboard-wrapper {
  width: 100%;
  margin: 0 auto;
}

.error-monitor-section {
  font-family: 'Plus Jakarta Sans', 'Pretendard', sans-serif;
  background-color: #f1f5f9;
  min-height: 100vh;
}

/* sleek-select */
.sleek-select {
  appearance: none;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 6px 36px 6px 12px;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  outline: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19.5 8.25l-7.5 7.5-7.5-7.5'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 14px;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.sleek-select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 2. 대시보드 하단 레이아웃 가로 콤팩트 스플릿 구조 (7:5 비율 매칭) */
.content-split-container {
  display: flex;
  gap: 20px;
  width: 100%;
  align-items: flex-start;
  margin-top: 20px;
}
.main-split-left {
  flex: 7;
  min-width: 0;
}
.main-split-right {
  flex: 5;
  min-width: 0;
}

.table-card {
  background: #ffffff;
  border-radius: 9px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}
.table-card-title { font-size: 14px; font-weight: 800; color: #0f172a; }
.table-card-header { border-bottom: 1px solid #f1f5f9; background-color: #ffffff; }

/* 3. 대형 패널 둥글기 및 그림자 */
.chart-container-inner {
  background-color: #f8fafc;
  border-radius: 9px;
  padding: 16px 12px 6px 12px;
  margin-top: 8px;
  border: 1px solid #cbd5e1;
  width: 100%;
}

.block { display: block; }

/* 반응형 웹 (Responsive Queries) */
@media (max-width: 960px) {
  .content-split-container {
    flex-direction: column;
    gap: 24px;
  }
  .main-split-left,
  .main-split-right {
    width: 100%;
    flex: none;
  }
}
</style>
