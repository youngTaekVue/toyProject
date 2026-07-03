<template>
  <!-- 대시보드 전체 폭을 제한하여 늘어짐 방지 -->
  <div class="dashboard-wrapper">
    <v-container fluid class="error-monitor-section pt-2 px-4 pb-8">

      <!-- Top Configuration Header -->
      <div class="d-flex align-center mb-5 mt-2">
        <span class="text-subtitle-2 font-weight-bold text-slate-700 mr-4 text-no-wrap tracking-tight">데이터 파일 선택:</span>
        <v-select
            v-model="selectedFileKey"
            :items="fileOptions"
            item-title="title"
            item-value="value"
            density="compact"
            variant="outlined"
            hide-details
            class="file-select-box"
            placeholder="파일을 선택하세요"
        ></v-select>
      </div>

      <!-- 1. Top Key Metrics Cards (가로 정렬 Flexbox) -->
      <div class="kpi-cards-container mb-6">
        <!-- 1) 총 실패 건수 -->
        <div class="premium-card">
          <div class="card-left">
            <span class="card-title-text">총 실패 건수</span>
            <div class="d-flex align-end mt-2">
              <span class="card-value-text">{{ formatNumber(kpiMetrics.totalFailures) }}</span>
              <span class="card-trend-badge" :class="kpiMetrics.failureTrend >= 0 ? 'trend-up' : 'trend-down'">
                {{ kpiMetrics.failureTrend >= 0 ? '↑' : '↓' }} {{ Math.abs(kpiMetrics.failureTrend) }}%
              </span>
            </div>
          </div>
          <div class="card-right icon-box-red">
            <v-icon size="small" color="white">mdi-alert-circle-outline</v-icon>
          </div>
        </div>

        <!-- 2) 영향을 받은 요양기관 수 -->
        <div class="premium-card">
          <div class="card-left">
            <span class="card-title-text">대상 요양기관 수</span>
            <div class="d-flex align-end mt-2">
              <span class="card-value-text">{{ formatNumber(kpiMetrics.affectedInstitutions) }}</span>
              <span class="card-trend-badge" :class="kpiMetrics.institutionTrend >= 0 ? 'trend-up' : 'trend-down'">
                {{ kpiMetrics.institutionTrend >= 0 ? '↑' : '↓' }} {{ Math.abs(kpiMetrics.institutionTrend) }}%
              </span>
            </div>
          </div>
          <div class="card-right icon-box-orange">
            <v-icon size="small" color="white">mdi-domain</v-icon>
          </div>
        </div>

        <!-- 3) 미등록 에러 건수 -->
        <div class="premium-card">
          <div class="card-left">
            <span class="card-title-text">미등록 에러 건수</span>
            <div class="d-flex align-end mt-2">
              <span class="card-value-text" :class="{'text-red font-weight-black': kpiMetrics.unclassifiedErrors > 0}">
                {{ formatNumber(kpiMetrics.unclassifiedErrors) }}
              </span>
              <span class="caption text-grey ml-1.5 pb-0.5 font-weight-medium">우선조치</span>
            </div>
          </div>
          <div class="card-right icon-box-purple">
            <v-icon size="small" color="white">mdi-database-plus</v-icon>
          </div>
        </div>

        <!-- 4) 최다 발생 에러 -->
        <div class="premium-card">
          <div class="card-left" style="max-width: calc(100% - 44px);">
            <span class="card-title-text">최다 발생 에러</span>
            <div class="mt-2 text-truncate font-weight-bold text-slate-800" style="font-size: 14px; line-height: 1.3;">
              {{ kpiMetrics.topErrorName }}
            </div>
            <span class="caption text-grey-darken-1 font-weight-medium mt-0.5">{{ formatNumber(kpiMetrics.topErrorCount) }}건 발생</span>
          </div>
          <div class="card-right icon-box-blue">
            <v-icon size="small" color="white">mdi-lightning-bolt</v-icon>
          </div>
        </div>

        <!-- 5) 시스템 안정성 점수 -->
        <div class="premium-card">
          <div class="card-left">
            <span class="card-title-text">시스템 안정성 점수</span>
            <div class="d-flex align-end mt-2">
              <span class="card-value-text text-green-darken-2">{{ kpiMetrics.stabilityScore }}점</span>
              <span class="caption text-grey ml-1.5 pb-0.5 font-weight-medium">전주대비 +{{ kpiMetrics.improvementRate }}%</span>
            </div>
          </div>
          <div class="card-right icon-box-green">
            <v-icon size="small" color="white">mdi-shield-check</v-icon>
          </div>
        </div>
      </div>

      <!-- 2. Visual Chart Analytics Section (가로 정렬 Flexbox) -->
      <div class="content-split-container mb-6">
        <!-- 하단 왼쪽: 에러 발생 및 기관 유입 트렌드 (혼합 차트) -->
        <div class="main-split-left">
          <v-card class="table-card pa-5" elevation="0">
            <div class="mb-4">
              <span class="table-card-title block">에러 발생 트렌드 분석</span>
              <p class="text-caption text-grey-darken-1 mb-0 mt-0.5">에러 건수(막대)와 요양기관 수(선)의 연동 추이 모니터링</p>
            </div>
            <div class="chart-wrapper">
              <apexchart type="line" height="260" :options="trendChartOptions" :series="trendChartSeries"></apexchart>
            </div>
          </v-card>
        </div>

        <!-- 하단 오른쪽: 주요 에러 유형 Top 5 비중 (도넛 차트) -->
        <div class="main-split-right">
          <v-card class="table-card pa-5" elevation="0">
            <div class="mb-4">
              <span class="table-card-title block">주요 에러 유형 비율 (Top 5)</span>
              <p class="text-caption text-grey-darken-1 mb-0">주요 실패 원인 집중 타겟팅용 분배 현황</p>
            </div>
            <div class="chart-wrapper d-flex justify-center align-center">
              <apexchart type="donut" width="100%" height="260" :options="donutChartOptions" :series="donutChartSeries"></apexchart>
            </div>
          </v-card>
        </div>
      </div>

      <!-- 3. Main Content Tables Area (가로 정렬 Flexbox) -->
      <div class="content-split-container">
        <!-- 왼쪽 테이블 영역 (요양기관별실패, 첨부파일별실패) -->
        <div class="main-split-left d-flex flex-column" style="gap: 24px;">
          <!-- Hospital Failure Table -->
          <v-card class="table-card" elevation="0">
            <v-card-title class="d-flex justify-space-between align-center py-4 px-5 table-card-header">
              <span class="table-card-title">요양기관별 실패 내역</span>
              <div class="search-box">
                <v-text-field v-model="hospitalSearch" density="compact" placeholder="요양기관명 검색..." hide-details prepend-inner-icon="mdi-magnify" variant="outlined" class="search-input"></v-text-field>
              </div>
            </v-card-title>

            <v-table class="dashboard-table">
              <thead>
              <tr>
                <th class="text-center" style="width: 60px;">No</th>
                <th class="text-left cursor-pointer user-select-none" @click="handleSort('hospital')" style="min-width: 180px;">요청 대상 요양기관명 <v-icon size="x-small">mdi-swap-vertical</v-icon></th>
                <th class="text-right cursor-pointer user-select-none" @click="handleSort('count')" style="width: 110px;">오류 건수 <v-icon size="x-small">mdi-swap-vertical</v-icon></th>
                <th class="text-right cursor-pointer user-select-none" @click="handleSort('resolutionRate')" style="width: 150px;">해결률 <v-icon size="x-small">mdi-swap-vertical</v-icon></th>
                <th class="text-center" style="width: 110px;">액션 링크</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="(item, idx) in paginatedHospitals" :key="item.hospital">
                <td class="text-center text-slate-400">{{ (hospitalPage - 1) * itemsPerPage + idx + 1 }}</td>
                <td class="text-left font-weight-medium text-slate-800">{{ item.hospital }}</td>
                <td class="text-right font-weight-bold text-slate-700">{{ formatNumber(item.count) }} 건</td>
                <td class="text-right">
                  <div class="d-flex align-center justify-end">
                    <span class="font-weight-bold mr-2.5" :class="item.resolutionRate === 100 ? 'text-green' : 'text-orange'">{{ item.resolutionRate.toFixed(2) }} %</span>
                    <v-progress-linear :model-value="item.resolutionRate" color="primary" height="6" rounded style="width: 60px;"></v-progress-linear>
                  </div>
                </td>
                <td class="text-center"><a href="#" class="action-link" @click.prevent="openHospitalDetail(item)">상세내역 ↗</a></td>
              </tr>
              <tr v-if="filteredHospitals.length === 0"><td colspan="5" class="text-center py-10 text-slate-400">데이터가 없습니다.</td></tr>
              </tbody>
            </v-table>
            <div class="d-flex justify-center align-center py-3 border-t" v-if="hospitalTotalPages > 1">
              <v-pagination v-model="hospitalPage" :length="hospitalTotalPages" total-visible="5" density="compact" active-color="primary"></v-pagination>
            </div>
          </v-card>

          <!-- Attached File Table -->
          <v-card class="table-card" elevation="0">
            <v-card-title class="py-4 px-5 table-card-header">
              <span class="table-card-title">첨부 파일별 실패 내역</span>
            </v-card-title>
            <v-table class="dashboard-table">
              <thead>
              <tr>
                <th class="text-left">첨부 파일</th>
                <th class="text-right" style="width: 160px;">오류 건수</th>
                <th class="text-right" style="width: 160px;">해결률</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="item in fileSummary" :key="item.fileName">
                <td class="text-left font-weight-medium text-slate-800">{{ item.displayName }}</td>
                <td class="text-right font-weight-bold text-slate-700">{{ formatNumber(item.count) }} 건</td>
                <td class="text-right">
                  <div class="d-flex align-center justify-end">
                    <span class="font-weight-bold mr-2.5" :class="item.resolutionRate === 100 ? 'text-green' : 'text-orange'">{{ item.resolutionRate.toFixed(2) }} %</span>
                    <v-progress-linear :model-value="item.resolutionRate" color="primary" height="6" rounded style="width: 70px;"></v-progress-linear>
                  </div>
                </td>
              </tr>
              </tbody>
            </v-table>
          </v-card>
        </div>

        <!-- 오른쪽 테이블 영역 (EMR 사별 실패 내역) -->
        <div class="main-split-right">
          <v-card class="table-card" elevation="0">
            <v-card-title class="d-flex justify-space-between align-center py-4 px-5 table-card-header">
              <span class="table-card-title">EMR 사별 실패 내역</span>
              <div class="search-box">
                <v-text-field v-model="emrSearch" density="compact" placeholder="EMR사 검색..." hide-details prepend-inner-icon="mdi-magnify" variant="outlined" class="search-input"></v-text-field>
              </div>
            </v-card-title>
            <v-table class="dashboard-table">
              <thead>
              <tr>
                <th class="text-left" style="min-width: 130px;">EMR 사별</th>
                <th class="text-right" style="width: 110px;">오류 건수</th>
                <th class="text-right" style="width: 150px;">해결률</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="item in paginatedEmrs" :key="item.emr">
                <td class="text-left font-weight-medium text-slate-800">{{ item.emr }}</td>
                <td class="text-right font-weight-bold text-slate-700">{{ formatNumber(item.count) }} 건</td>
                <td class="text-right">
                  <div class="d-flex align-center justify-end">
                    <span class="font-weight-bold mr-2.5" :class="item.resolutionRate === 100 ? 'text-green' : 'text-orange'">{{ item.resolutionRate.toFixed(2) }} %</span>
                    <v-progress-linear :model-value="item.resolutionRate" color="primary" height="6" rounded style="width: 60px;"></v-progress-linear>
                  </div>
                </td>
              </tr>
              </tbody>
            </v-table>
          </v-card>
        </div>
      </div>

    </v-container>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

import VueApexCharts from 'vue3-apexcharts';
const apexchart = VueApexCharts;

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

const sortKey = ref<string>('count');
const sortOrder = ref<'desc' | 'asc'>('desc');

const rawRows = ref<ErrorDetail[]>([]);
const persistedStates = ref<Record<string, RowState>>({});
const isLoading = ref(false);

const hospitalSearch = ref('');
const hospitalPage = ref(1);
const itemsPerPage = 10;
const emrSearch = ref('');
const emrPage = ref(1);

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
  const currentCases = groupedClaimCases.value;
  const totalFailures = currentCases.reduce((sum, c) => sum + c.count, 0);
  const failureTrend = -8.0;

  const uniqueHospitals = new Set(currentCases.map(c => c.hospital));
  const affectedInstitutions = uniqueHospitals.size;
  const institutionTrend = +2.4;

  const unclassifiedErrors = currentCases
      .filter(c => !c.category || c.category.includes('미분류') || c.category === '기타')
      .reduce((sum, c) => sum + c.count, 0);

  const errorMap: Record<string, number> = {};
  currentCases.forEach(c => { errorMap[c.category] = (errorMap[c.category] || 0) + c.count; });

  let topErrorName = 'N/A';
  let topErrorCount = 0;
  Object.entries(errorMap).forEach(([name, count]) => {
    if (count > topErrorCount) {
      topErrorCount = count;
      topErrorName = name;
    }
  });

  const stabilityScore = Math.max(45, Math.min(100, Math.round(100 - (totalFailures / 50))));
  const improvementRate = 4.2;

  return {
    totalFailures, failureTrend,
    affectedInstitutions, institutionTrend,
    unclassifiedErrors,
    topErrorName, topErrorCount,
    stabilityScore, improvementRate
  };
});

const trendChartData = computed(() => {
  const sortedFiles = [...allFileKeys.value].sort((a, b) => a.localeCompare(b));
  const categories = sortedFiles.map(key => key.replace(/_/g, '-'));
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
  stroke: { width: [0, 3.5], curve: 'smooth' },
  colors: ['#3b82f6', '#f59e0b'],
  plotOptions: { bar: { columnWidth: '40%', borderRadius: 6 } },
  markers: { size: [0, 5], colors: ['#ffffff'], strokeColors: '#f59e0b', strokeWidth: 2.5 },
  dataLabels: { enabled: false },
  xaxis: { categories: trendChartData.value.categories, axisBorder: { show: false } },
  yaxis: [
    { title: { text: '오류 건수', style: { color: '#64748b', fontWeight: 600 } }, labels: { formatter: (val: number) => val.toLocaleString() } },
    { opposite: true, title: { text: '기관 수', style: { color: '#64748b', fontWeight: 600 } }, labels: { formatter: (val: number) => Math.round(val) } }
  ],
  grid: { borderColor: '#f1f5f9' },
  legend: { position: 'bottom', horizontalAlign: 'center', boxWidth: 12 }
}));

const donutChartComputedData = computed(() => {
  const currentCases = groupedClaimCases.value;
  const errorMap: Record<string, number> = {};
  currentCases.forEach(c => { errorMap[c.category] = (errorMap[c.category] || 0) + c.count; });

  const sortedErrors = Object.entries(errorMap).sort((a, b) => b[1] - a[1]);
  const top5 = sortedErrors.slice(0, 5);
  const remainingSum = sortedErrors.slice(5).reduce((sum, curr) => sum + curr[1], 0);

  const labels = top5.map(e => e[0]);
  const series = top5.map(e => e[1]);

  if (remainingSum > 0) {
    labels.push('기타 에러');
    series.push(remainingSum);
  }

  return { labels, series };
});

const donutChartSeries = computed(() => donutChartComputedData.value.series);

const donutChartOptions = computed(() => ({
  chart: { fontFamily: 'Pretendard, sans-serif' },
  labels: donutChartComputedData.value.labels,
  colors: ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#94a3b8'],
  stroke: { colors: ['#ffffff'], width: 2 },
  plotOptions: {
    pie: {
      donut: {
        size: '68%',
        labels: {
          show: true,
          total: {
            show: true,
            label: '총 청구 오류건',
            fontSize: '11px',
            color: '#64748b',
            formatter: (w: any) => {
              const sum = w.globals.seriesTotals.reduce((a: number, b: number) => a + b, 0);
              return sum.toLocaleString() + ' 건';
            }
          }
        }
      }
    }
  },
  dataLabels: { enabled: false },
  legend: { position: 'bottom' }
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
  let list = groupedHospitals.value.filter(h => h.hospital.toLowerCase().includes(search));
  return list.sort((a, b) => {
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
  if (!search) return groupedEmrs.value.slice().sort((a, b) => b.count - a.count);
  return groupedEmrs.value.filter(e => e.emr.toLowerCase().includes(search)).sort((a, b) => b.count - a.count);
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
      // 🌟 핵심: 현재 상단 셀렉트박스에서 선택해서 보고 있는 그 엑셀 파일 키를 주소창에 태워서 보냅니다.
      fileKey: selectedFileKey.value
    }
  });
}
function formatNumber(num: number): string { return new Intl.NumberFormat().format(num || 0); }

watch([hospitalSearch, emrSearch, selectedFileKey], () => { hospitalPage.value = 1; emrPage.value = 1; });
onMounted(() => { loadExcelData(); });
</script>

<style scoped>
/* [핵심] 모니터가 무한정 넓어져도 대시보드가 가로로 퍼지는 것을 방지하는 마스터 래퍼 */
.dashboard-wrapper {
  width: 100%;
  //max-width: 1400px; /* 전체 최대 폭 제한 */
  margin: 0 auto; /* 화면 중앙 정렬 */
}

.error-monitor-section {
  font-family: 'Pretendard', sans-serif;
  background-color: #f8fafc;
}

.file-select-box {
  max-width: 260px;
}
.file-select-box :deep(.v-field) {
  border-radius: 8px !important;
}

/* 1. 상단 KPI 카드 가로 콤팩트 한 줄 배치 시스템 */
.kpi-cards-container {
  display: flex;
  gap: 14px;
  width: 100%;
}
.premium-card {
  flex: 1 1 0px; /* 모든 카드가 가로폭을 똑같이 나눠 가짐 */
  min-width: 190px;
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid rgba(15, 23, 42, 0.04);
  padding: 16px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 94px;
  box-shadow: 0 4px 10px -4px rgba(0, 0, 0, 0.02), 0 1px 3px rgba(0, 0, 0, 0.01);
}
.card-left { display: flex; flex-direction: column; width: 100%; overflow: hidden; }
.card-title-text { font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: -0.1px; }
.card-value-text { font-size: 21px; font-weight: 800; color: #0f172a; line-height: 1.1; }
.card-trend-badge { font-size: 10.5px; font-weight: 700; padding: 1px 5px; border-radius: 5px; margin-left: 6px; }
.trend-up { background-color: #fef2f2; color: #ef4444; }
.trend-down { background-color: #f0fdf4; color: #22c55e; }

.card-right { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.icon-box-red { background: linear-gradient(135deg, #f87171 0%, #dc2626 100%); }
.icon-box-orange { background: linear-gradient(135deg, #fb923c 0%, #ea580c 100%); }
.icon-box-purple { background: linear-gradient(135deg, #c084fc 0%, #9333ea 100%); }
.icon-box-blue { background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%); }
.icon-box-green { background: linear-gradient(135deg, #4ade80 0%, #16a34a 100%); }

/* 2. 대시보드 하단 레이아웃 가로 콤팩트 스플릿 구조 (7:5 비율 매칭) */
.content-split-container {
  display: flex;
  gap: 16px;
  width: 100%;
  align-items: flex-start;
}
.main-split-left {
  flex: 7; /* 왼쪽 콘텐츠 비중 7 */
  min-width: 0;
}
.main-split-right {
  flex: 5; /* 오른쪽 콘텐츠 비중 5 */
  min-width: 0;
}

/* 3. 대형 공통 패널 둥글기 및 그림자 정렬 */
.table-card {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.04);
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.02);
  overflow: hidden;
}
.table-card-title { font-size: 15px; font-weight: 800; color: #0f172a; }
.table-card-header { border-bottom: 1px solid #f1f5f9; background-color: #ffffff; }

.search-box { width: 200px; }
.search-input :deep(.v-field) {
  border-radius: 6px !important;
}

/* 4. 데이터 테이블 세부 여백 콤팩트화 */
.dashboard-table { width: 100%; border-collapse: collapse; }
.dashboard-table :deep(th) {
  background-color: #f8fafc !important;
  color: #475569 !important;
  font-size: 11.5px !important;
  font-weight: 700 !important;
  padding: 12px 16px !important;
}
.dashboard-table :deep(td) {
  padding: 11px 16px !important;
  font-size: 13px !important;
  color: #334155 !important;
  border-bottom: 1px solid #f1f5f9 !important;
}

.action-link { color: #2563eb; font-size: 12.5px; font-weight: 700; text-decoration: none; }
.action-link:hover { text-decoration: underline; }
.text-green { color: #10b981 !important; }
.text-orange { color: #f59e0b !important; }
.cursor-pointer { cursor: pointer; }
.user-select-none { user-select: none; }

.chart-wrapper { width: 100%; min-height: 260px; }
.block { display: block; }
</style>