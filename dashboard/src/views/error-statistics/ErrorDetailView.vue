<template>
  <div class="dashboard-wrapper">
    <v-container fluid class="error-monitor-section pt-3 px-4 pb-8">

      <!-- Header Block -->
      <DetailHeader
        :targetType="targetType"
        :targetName="targetName"
        :currentFileKey="currentFileKey"
        @back="goBack"
      />

      <!-- Summary Metrics Cards -->
      <DetailKpiCards :targetSummary="targetSummary" />

      <!-- EMR Hospital Filter Grid -->
      <EmrHospitalFilterGrid
        :targetType="targetType"
        :emrHospitalsSummary="emrHospitalsSummary"
        v-model:selectedHospitalFilter="selectedHospitalFilter"
        :allRowsLength="allRows.length"
        :targetSummary="targetSummary"
      />

      <!-- Table Card -->
      <DetailCasesTable
        v-model:currentPage="currentPage"
        v-model:searchQuery="searchQuery"
        :paginatedRows="paginatedRows"
        :filteredRows="filteredRows"
        :totalPages="totalPages"
        :itemsPerPage="itemsPerPage"
        :sortKey="sortKey"
        :sortOrder="sortOrder"
        @sort="handleSort"
        @toggle-row-state="toggleRowState"
      />

      <!-- Overlay Loader -->
      <v-overlay :model-value="isLoading" class="align-center justify-center" persistent>
        <v-progress-circular color="primary" indeterminate size="64"></v-progress-circular>
      </v-overlay>

    </v-container>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

// Component imports
import DetailHeader from '@/components/error-statistics/DetailHeader.vue';
import DetailKpiCards from '@/components/error-statistics/DetailKpiCards.vue';
import EmrHospitalFilterGrid from '@/components/error-statistics/EmrHospitalFilterGrid.vue';
import DetailCasesTable from '@/components/error-statistics/DetailCasesTable.vue';

type RowState = '미확인' | '회신대기' | '최종완료';

interface ErrorDetail {
  no: number;
  fileKey: string;
  sheetName?: string;
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
  key: string;
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

const targetType = ref<string>((route.query.type as string) || 'hospital');
const targetName = ref<string>((route.query.name as string) || '');
const currentFileKey = ref<string>((route.query.fileKey as string) || '');

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000') + '/api/errorStatistics';

const allRows = ref<ClaimCase[]>([]);
const persistedStates = ref<Record<string, RowState>>({});
const isLoading = ref(false);

const searchQuery = ref('');
const currentPage = ref(1);
const itemsPerPage = 10;

const sortKey = ref<string>('count');
const sortOrder = ref<'desc' | 'asc'>('desc');

const selectedHospitalFilter = ref('all');

function goBack() {
  router.push('/error-statistics');
}

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

async function loadData() {
  isLoading.value = true;
  try {
    let loadedRows: ErrorDetail[] = [];
    if (currentFileKey.value === 'all') {
      const filesRes = await fetch(`${API_BASE_URL}/files?t=${Date.now()}`);
      if (!filesRes.ok) throw new Error('Failed to load file list');
      const filesJson = await filesRes.json();
      if (filesJson.success && Array.isArray(filesJson.files)) {
        for (const fileKey of filesJson.files) {
          const dataRes = await fetch(`${API_BASE_URL}/data/${fileKey}?t=${Date.now()}`);
          if (!dataRes.ok) continue;
          const dataJson = await dataRes.json();
          if (dataJson.success && Array.isArray(dataJson.rows)) {
            dataJson.rows.forEach((row: ErrorDetail) => {
              loadedRows.push(row);
            });
          }
        }
      }
    } else {
      const dataRes = await fetch(`${API_BASE_URL}/data/${currentFileKey.value}?t=${Date.now()}`);
      if (!dataRes.ok) throw new Error('Data load failed');
      const dataJson = await dataRes.json();
      if (dataJson.success && Array.isArray(dataJson.rows)) {
        loadedRows = dataJson.rows;
      }
    }

    if (loadedRows.length >= 0) {
      const tempPersistedStates: Record<string, RowState> = {};
      const groups: Record<string, ErrorDetail[]> = {};
      
      loadedRows.forEach((row: ErrorDetail) => {
        const key = getGroupKey(row);
        tempPersistedStates[key] = row.state;
        if (!groups[key]) groups[key] = [];
        groups[key].push(row);
      });

      persistedStates.value = tempPersistedStates;

      const cases: ClaimCase[] = Object.entries(groups).map(([groupKey, rows]) => {
        const first = rows[0];
        let cleanDetails = first.details || '';
        if (cleanDetails.includes('===')) {
          cleanDetails = cleanDetails.split(/={3,}/)[0].trim();
        }
        const errorTitle = first.category && !first.category.includes('미분류') ? first.category : cleanDetails.substring(0, 40);

        return {
          key: groupKey,
          hospital: first.hospital.trim(),
          institutionId: first.institutionId,
          emr: first.emr,
          category: errorTitle,
          patient: rows.length > 1 ? `${first.patient} 외 ${rows.length - 1}명` : first.patient,
          birthDate: first.birthDate,
          count: rows.length,
          state: tempPersistedStates[groupKey] || '미확인',
          fileKey: first.fileKey,
          rows
        };
      });

      let filtered = cases;
      if (targetType.value === 'hospital') {
        filtered = cases.filter((c: ClaimCase) => c.hospital.trim() === targetName.value.trim());
      } else {
        filtered = cases.filter((c: ClaimCase) => c.emr === targetName.value);
      }

      filtered.sort((a, b) => b.count - a.count);
      allRows.value = filtered;
    }
  } catch (error) {
    console.error('Failed to load detail data:', error);
  } finally {
    isLoading.value = false;
  }
}

const targetSummary = computed(() => {
  if (allRows.value.length === 0) return null;
  const count = allRows.value.reduce((sum, r) => sum + r.count, 0);
  const sentCount = allRows.value.filter(r => (persistedStates.value[r.key] || '미확인') === '회신대기').reduce((sum, r) => sum + r.count, 0);
  const confirmedCount = allRows.value.filter(r => (persistedStates.value[r.key] || '미확인') === '최종완료').reduce((sum, r) => sum + r.count, 0);
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
    summaryMap[c.hospital].casesCount += c.count;
    const state = persistedStates.value[c.key] || '미확인';
    if (state === '최종완료') {
      summaryMap[c.hospital].resolvedCasesCount += c.count;
    }
  });

  return Object.entries(summaryMap).map(([hospital, data]) => {
    const resolutionRate = data.casesCount > 0 ? (data.resolvedCasesCount / data.casesCount) * 100 : 0;
    return { hospital, count: data.count, casesCount: data.casesCount, resolutionRate };
  }).sort((a, b) => b.casesCount - a.casesCount);
});

const filteredRows = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  let mapped = allRows.value.map(row => ({
    ...row,
    state: persistedStates.value[row.key] || '미확인'
  }));

  if (targetType.value === 'emr' && selectedHospitalFilter.value !== 'all') {
    mapped = mapped.filter(r => r.hospital === selectedHospitalFilter.value);
  }

  if (query) {
    mapped = mapped.filter(r =>
        r.hospital.toLowerCase().includes(query) ||
        r.category.toLowerCase().includes(query)
    );
  }

  return mapped.slice().sort((a, b) => {
    const valA = a[sortKey.value as keyof typeof a];
    const valB = b[sortKey.value as keyof typeof b];
    const modifier = sortOrder.value === 'asc' ? 1 : -1;
    if (typeof valA === 'string' && typeof valB === 'string') {
      return valA.localeCompare(valB) * modifier;
    }
    return (Number(valA) - Number(valB)) * modifier;
  });
});

const totalPages = computed(() => Math.ceil(filteredRows.value.length / itemsPerPage));
const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredRows.value.slice(start, start + itemsPerPage);
});

async function toggleRowState(row: any) {
  const key = row.key;
  const currentState = persistedStates.value[key] || '미확인';

  let nextState: RowState = '미확인';

  if (currentState === '미확인') {
    nextState = '회신대기';
  } else if (currentState === '회신대기') {
    nextState = '최종완료';
  } else if (currentState === '최종완료') {
    nextState = '미확인';
  }

  isLoading.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fileKey: row.fileKey,
        hospital: row.hospital,
        patient: row.patient,
        birthDate: row.birthDate,
        category: row.category,
        state: nextState,
        rows: row.rows
      })
    });

    if (res.ok) {
      persistedStates.value[key] = nextState;
    } else {
      console.error('H열 상태 되돌리기 API 실패');
    }
  } catch (error) {
    console.error('상태 변경 중 예외 발생:', error);
  } finally {
    isLoading.value = false;
  }
}

watch([searchQuery, selectedHospitalFilter, sortKey, sortOrder], () => {
  currentPage.value = 1;
});
onMounted(() => { loadData(); });
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
  display: flex;
  flex-direction: column;
  gap: 24px;
}
</style>
