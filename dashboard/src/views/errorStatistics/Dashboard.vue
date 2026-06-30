<template>
  <v-container fluid class="error-monitor-section pt-0">
    
    <!-- Top Key Metrics Cards (Soft UI Style) -->
    <v-row class="mb-6 mt-1">
      <v-col cols="12" md="4">
        <div class="premium-card">
          <div class="card-left">
            <span class="card-title-text">Total Requests (총 청구건)</span>
            <div class="d-flex align-center mt-1">
              <span class="card-value-text">{{ formatNumber(totalRequests) }}</span>
              <span class="card-badge-percentage badge-blue ml-2">
                {{ totalRequests > 0 ? ((confirmedCount / totalRequests) * 100).toFixed(0) : 0 }}% 해결율
              </span>
            </div>
          </div>
          <div class="card-right icon-box-blue">
            <v-icon size="large" color="white">mdi-alert-circle</v-icon>
          </div>
        </div>
      </v-col>
      <v-col cols="12" md="4">
        <div class="premium-card">
          <div class="card-left">
            <span class="card-title-text">Mail Sent (회신대기)</span>
            <div class="d-flex align-center mt-1">
              <span class="card-value-text">{{ formatNumber(mailSentCount) }}</span>
              <span class="card-badge-percentage badge-orange ml-2">
                {{ totalRequests > 0 ? ((mailSentCount / totalRequests) * 100).toFixed(0) : 0 }}% 대기율
              </span>
            </div>
          </div>
          <div class="card-right icon-box-orange">
            <v-icon size="large" color="white">mdi-email-send</v-icon>
          </div>
        </div>
      </v-col>
      <v-col cols="12" md="4">
        <div class="premium-card">
          <div class="card-left">
            <span class="card-title-text">Confirmed (최종완료)</span>
            <div class="d-flex align-center mt-1">
              <span class="card-value-text">{{ formatNumber(confirmedCount) }}</span>
              <span class="card-badge-percentage badge-green ml-2">
                +{{ totalRequests > 0 ? ((confirmedCount / totalRequests) * 100).toFixed(0) : 0 }}% 완료
              </span>
            </div>
          </div>
          <div class="card-right icon-box-green">
            <v-icon size="large" color="white">mdi-check-decagram</v-icon>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Main Content Area -->
    <v-row>
      <!-- Left Column (Hospitals & File Summary) -->
      <v-col cols="12" md="7">
        <!-- Hospital Failure Table -->
        <v-card class="table-card mb-6" elevation="0">
          <v-card-title class="d-flex justify-space-between align-center py-3 px-4 table-card-header">
            <span class="table-card-title">요양기관별 실패 내역</span>
            <div class="search-box">
              <v-text-field
                v-model="hospitalSearch"
                density="compact"
                placeholder="요양기관명 검색..."
                hide-details
                prepend-inner-icon="mdi-magnify"
                variant="outlined"
                class="search-input"
              ></v-text-field>
            </div>
          </v-card-title>
          
          <v-table class="dashboard-table">
            <thead>
              <tr>
                <th class="text-center" style="width: 60px;">No</th>
                <th class="text-left" style="min-width: 180px;">요청 대상 요양기관명</th>
                <th class="text-right" style="width: 120px;">오류 건수</th>
                <th class="text-right" style="width: 160px;">해결률 (처리율)</th>
                <th class="text-center" style="width: 120px;">액션 링크</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in paginatedHospitals" :key="item.hospital">
                <td class="text-center">{{ (hospitalPage - 1) * itemsPerPage + idx + 1 }}</td>
                <td class="text-left font-weight-medium">{{ item.hospital }}</td>
                <td class="text-right font-weight-bold text-slate-700">{{ formatNumber(item.casesCount) }} 건</td>
                <td class="text-right">
                  <div class="d-flex align-center justify-end">
                    <span class="font-weight-bold mr-2" :class="item.resolutionRate === 100 ? 'text-green' : 'text-orange'">
                      {{ item.resolutionRate.toFixed(2) }} %
                    </span>
                    <v-progress-linear
                      :model-value="item.resolutionRate"
                      color="primary"
                      height="6"
                      rounded
                      style="width: 70px;"
                    ></v-progress-linear>
                  </div>
                </td>
                <td class="text-center">
                  <a href="#" class="action-link" @click.prevent="openHospitalDetail(item)">
                    상세내역 ↗
                  </a>
                </td>
              </tr>
              <tr v-if="filteredHospitals.length === 0">
                <td colspan="5" class="text-center py-8 text-grey">데이터가 없습니다.</td>
              </tr>
            </tbody>
          </v-table>
          
          <!-- Hospital Table Pagination -->
          <div class="d-flex justify-center align-center py-3 border-t" v-if="hospitalTotalPages > 1">
            <v-pagination
              v-model="hospitalPage"
              :length="hospitalTotalPages"
              total-visible="5"
              density="compact"
              active-color="primary"
            ></v-pagination>
          </div>
        </v-card>

        <!-- Attached File Table -->
        <v-card class="table-card" elevation="0">
          <v-card-title class="py-3 px-4 table-card-header">
            <span class="table-card-title">첨부 파일별 실패 내역</span>
          </v-card-title>
          
          <v-table class="dashboard-table">
            <thead>
              <tr>
                <th class="text-left">첨부 파일</th>
                <th class="text-right" style="width: 200px;">오류 건수</th>
                <th class="text-right" style="width: 200px;">해결률 (오류 해결)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in fileSummary" :key="item.fileName">
                <td class="text-left font-weight-medium">{{ item.displayName }}</td>
                <td class="text-right font-weight-bold">{{ formatNumber(item.count) }} 건</td>
                <td class="text-right">
                  <div class="d-flex align-center justify-end">
                    <span class="font-weight-bold mr-2" :class="item.resolutionRate === 100 ? 'text-green' : 'text-orange'">
                      {{ item.resolutionRate.toFixed(2) }} %
                    </span>
                    <v-progress-linear
                      :model-value="item.resolutionRate"
                      color="primary"
                      height="6"
                      rounded
                      style="width: 80px;"
                    ></v-progress-linear>
                  </div>
                </td>
              </tr>
              <tr v-if="fileSummary.length === 0">
                <td colspan="3" class="text-center py-8 text-grey">파일 데이터가 없습니다.</td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>

      <!-- Right Column (EMR Vendors) -->
      <v-col cols="12" md="5">
        <!-- EMR Failure Table -->
        <v-card class="table-card" elevation="0">
          <v-card-title class="d-flex justify-space-between align-center py-3 px-4 table-card-header">
            <span class="table-card-title">EMR 사별 실패 내역</span>
            <div class="search-box">
              <v-text-field
                v-model="emrSearch"
                density="compact"
                placeholder="EMR사 검색..."
                hide-details
                prepend-inner-icon="mdi-magnify"
                variant="outlined"
                class="search-input"
              ></v-text-field>
            </div>
          </v-card-title>
          
          <v-table class="dashboard-table">
            <thead>
              <tr>
                <th class="text-left" style="min-width: 150px;">EMR 사별</th>
                <th class="text-right" style="width: 120px;">오류 건수</th>
                <th class="text-right" style="width: 160px;">해결률 (처리율)</th>
                <th class="text-center" style="width: 100px;">액션 링크</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in paginatedEmrs" :key="item.emr">
                <td class="text-left font-weight-medium">{{ item.emr }}</td>
                <td class="text-right font-weight-bold text-slate-700">{{ formatNumber(item.casesCount) }} 건</td>
                <td class="text-right">
                  <div class="d-flex align-center justify-end">
                    <span class="font-weight-bold mr-2" :class="item.resolutionRate === 100 ? 'text-green' : 'text-orange'">
                      {{ item.resolutionRate.toFixed(2) }} %
                    </span>
                    <v-progress-linear
                      :model-value="item.resolutionRate"
                      color="primary"
                      height="6"
                      rounded
                      style="width: 70px;"
                    ></v-progress-linear>
                  </div>
                </td>
                <td class="text-center">
                  <a href="#" class="action-link" @click.prevent="openEmrDetail(item)">
                    상세내역 ↗
                  </a>
                </td>
              </tr>
              <tr v-if="filteredEmrs.length === 0">
                <td colspan="4" class="text-center py-8 text-grey">데이터가 없습니다.</td>
              </tr>
            </tbody>
          </v-table>
          
          <!-- EMR Table Pagination -->
          <div class="d-flex justify-center align-center py-3 border-t" v-if="emrTotalPages > 1">
            <v-pagination
              v-model="emrPage"
              :length="emrTotalPages"
              total-visible="5"
              density="compact"
              active-color="primary"
            ></v-pagination>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Detail Dialog -->
    <v-dialog v-model="detailDialog" max-width="950px" scrollable>
      <v-card v-if="detailTarget">
        <v-card-title class="d-flex justify-space-between align-center border-b px-6 py-4">
          <span class="text-h6 font-weight-bold text-slate-800">
            [{{ detailTargetType === 'hospital' ? '요양기관' : 'EMR사' }} 상세내역 - 청구건 단위] {{ detailTarget.name }}
          </span>
          <v-btn icon="mdi-close" variant="text" @click="detailDialog = false" size="small"></v-btn>
        </v-card-title>
        
        <v-card-text class="px-6 py-5 bg-slate-50">
          <!-- Summary in dialog -->
          <v-row class="mb-5">
            <v-col cols="4">
              <div class="dialog-stat-box box-total">
                <span class="stat-label">총 청구건수</span>
                <span class="stat-value text-blue">{{ formatNumber(detailTarget.count) }} 건</span>
              </div>
            </v-col>
            <v-col cols="4">
              <div class="dialog-stat-box box-sent">
                <span class="stat-label">회신대기 청구건수</span>
                <span class="stat-value text-orange">{{ formatNumber(detailTarget.sentCount) }} 건</span>
              </div>
            </v-col>
            <v-col cols="4">
              <div class="dialog-stat-box box-confirmed">
                <span class="stat-label">최종완료 청구건수</span>
                <span class="stat-value text-green">{{ formatNumber(detailTarget.confirmedCount) }} 건</span>
              </div>
            </v-col>
          </v-row>

          <!-- Detail Table -->
          <v-card outlined elevation="0" class="border">
            <v-table class="detail-inner-table">
              <thead>
                <tr>
                  <th class="text-center" style="width: 50px;">No</th>
                  <th class="text-left" style="width: 100px;">피보험자</th>
                  <th class="text-center" style="width: 110px;">생년월일</th>
                  <th class="text-left">청구실패 사유 (오류 내용)</th>
                  <th class="text-right" style="width: 100px;">실패 건수</th>
                  <th class="text-center" style="width: 110px;">상태</th>
                  <th class="text-center" style="width: 90px;">액션</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in paginatedDetailRows" :key="row.key">
                  <td class="text-center">{{ (detailPage - 1) * detailItemsPerPage + idx + 1 }}</td>
                  <td class="text-left font-weight-medium">{{ row.patient }}</td>
                  <td class="text-center font-weight-medium">{{ row.birthDate }}</td>
                  <td class="text-left text-body-2 font-weight-medium text-wrap-pretty">{{ row.category }}</td>
                  <td class="text-right font-weight-bold text-primary">{{ formatNumber(row.count) }} 건</td>
                  <td class="text-center">
                    <v-chip :color="getStatusColor(row.state)" variant="flat" size="x-small" class="status-chip-fixed">
                      {{ row.state }}
                    </v-chip>
                  </td>
                  <td class="text-center">
                    <v-btn
                      size="x-small"
                      :color="row.state === '최종완료' ? 'grey-lighten-1' : 'primary'"
                      variant="flat"
                      class="action-btn-small"
                      @click="toggleCaseState(row)"
                    >
                      {{ getRowButtonLabel(row.state) }}
                    </v-btn>
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-card>
          
          <!-- Detail Table Pagination -->
          <div class="d-flex justify-center align-center mt-5" v-if="detailTotalPages > 1">
            <v-pagination
              v-model="detailPage"
              :length="detailTotalPages"
              total-visible="5"
              density="compact"
              active-color="primary"
            ></v-pagination>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Loading Indicator -->
    <v-overlay :model-value="isLoading" class="align-center justify-center" persistent>
      <v-progress-circular color="primary" indeterminate size="64"></v-progress-circular>
    </v-overlay>

  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// 1. Types
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

// 2. Constants & API URL
const defaultHospital = '알 수 없는 병원';
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000') + '/api/errorStatistics';

// Get all keys (filenames without extension) - populated from API
const allFileKeys = ref<string[]>([]);

// 4. Reactive States
const rawRows = ref<ErrorDetail[]>([]);
const persistedStates = ref<Record<string, RowState>>({});
const isLoading = ref(false);

const hospitalSearch = ref('');
const hospitalPage = ref(1);
const itemsPerPage = 10;

const emrSearch = ref('');
const emrPage = ref(1);

const statusOptions: RowState[] = ['미확인', '회신대기', '최종완료'];

// Detail Dialog States
const detailDialog = ref(false);
const detailTargetType = ref<'hospital' | 'emr'>('hospital');
const detailTargetName = ref('');
const detailPage = ref(1);
const detailItemsPerPage = 10;

// Helper to calculate record state key
function getGroupKey(row: { fileKey: string; hospital: string; category: string; patient: string; birthDate: string }): string {
  return `${row.fileKey}|${row.hospital}|${row.category.substring(0, 30)}|${row.patient}|${row.birthDate}`;
}

// 6. Loading Excel Data from Backend API
async function loadExcelData() {
  isLoading.value = true;
  try {
    // Fetch file list
    const filesRes = await fetch(`${API_BASE_URL}/files?t=${Date.now()}`);
    if (!filesRes.ok) throw new Error('Failed to load file list');
    const filesJson = await filesRes.json();
    
    if (filesJson.success && Array.isArray(filesJson.files)) {
      allFileKeys.value = filesJson.files;
    }

    const fileKeys = allFileKeys.value;
    const loadedRows: ErrorDetail[] = [];
    const tempPersistedStates: Record<string, RowState> = {};

    // Fetch data for each file
    for (const fileKey of fileKeys) {
      const dataRes = await fetch(`${API_BASE_URL}/data/${fileKey}?t=${Date.now()}`);
      if (!dataRes.ok) {
        console.warn(`Failed to fetch data for Excel file key: ${fileKey}`);
        continue;
      }
      const dataJson = await dataRes.json();
      if (dataJson.success && Array.isArray(dataJson.rows)) {
        dataJson.rows.forEach((row: ErrorDetail) => {
          loadedRows.push(row);
          // Set state map cache from file status
          const key = getGroupKey(row);
          tempPersistedStates[key] = row.state;
        });
      }
    }

    rawRows.value = loadedRows;
    persistedStates.value = tempPersistedStates;
  } catch (error) {
    console.error('Excel 로드 실패:', error);
  } finally {
    isLoading.value = false;
  }
}

// 8. Reactive Computed Values for Grouping and Table Rendering
const normalizedRows = computed<ErrorDetail[]>(() => {
  return rawRows.value.map(row => {
    const key = getGroupKey(row);
    const state = persistedStates.value[key] || '미확인';
    return {
      ...row,
      state
    };
  });
});

// Grouped Claim Cases (Hospitals > Errors > Patient + Birthdate)
const groupedClaimCases = computed<ClaimCase[]>(() => {
  const groups: Record<string, ErrorDetail[]> = {};
  
  normalizedRows.value.forEach(row => {
    const key = getGroupKey(row);
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(row);
  });

  return Object.entries(groups).map(([groupKey, rows]) => {
    const first = rows[0];
    const hospital = first.hospital;
    const institutionId = first.institutionId;
    const emr = first.emr;
    const category = first.category;
    const patient = first.patient;
    const birthDate = first.birthDate;
    const fileKey = first.fileKey;

    const state = persistedStates.value[groupKey] || '미확인';

    return {
      key: groupKey,
      hospital,
      institutionId,
      emr,
      category,
      patient,
      birthDate,
      count: rows.length,
      state,
      fileKey,
      rows
    };
  });
});

// Overall Stats for Top Cards (Grouped Claim Cases basis)
const totalRequests = computed(() => groupedClaimCases.value.length);
const mailSentCount = computed(() => groupedClaimCases.value.filter(c => c.state === '회신대기').length);
const confirmedCount = computed(() => groupedClaimCases.value.filter(c => c.state === '최종완료').length);

// SVG Dynamic Bar Chart for Top 8 failing hospitals (Soft UI active users style)
const barChartData = computed(() => {
  const list = paginatedHospitals.value.slice(0, 8);
  if (list.length === 0) return [];
  const maxVal = Math.max(...list.map(d => d.casesCount), 10);
  const height = 110;
  const width = 280;
  const padding = 15;

  return list.map((item, index) => {
    const x = padding + (index * (width - padding * 2)) / Math.max(list.length - 1, 1);
    const barHeight = (item.casesCount * (height - padding * 2)) / maxVal;
    const y = height - padding - barHeight;
    return {
      x: x - 6,
      y,
      width: 12,
      height: barHeight,
      hospital: item.hospital,
      count: item.casesCount
    };
  });
});

// SVG Dynamic curve chart for files (Soft UI sales overview style)
const chartData = computed(() => {
  const list = fileSummary.value;
  if (list.length === 0) {
    return { points: [], pathCount: 'M 0 0', pathRate: 'M 0 0', maxCount: 10 };
  }

  const maxCount = Math.max(...list.map(d => d.count), 10);
  const width = 560;
  const height = 150;
  const padding = 30;

  const points = list.map((item, index) => {
    const x = padding + (index * (width - padding * 2)) / Math.max(list.length - 1, 1);
    const yCount = height - padding - (item.count * (height - padding * 2)) / maxCount;
    const yRate = height - padding - (item.resolutionRate * (height - padding * 2)) / 100;
    return {
      x,
      yCount,
      yRate,
      label: item.displayName,
      count: item.count,
      rate: item.resolutionRate
    };
  });

  // Calculate smooth bezier paths
  let pathCount = '';
  let pathRate = '';
  if (points.length > 0) {
    pathCount = `M ${points[0].x} ${points[0].yCount}`;
    pathRate = `M ${points[0].x} ${points[0].yRate}`;

    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[i];
      const p1 = points[i + 1];
      const cpX1 = p0.x + (p1.x - p0.x) / 3;
      const cpY1 = p0.yCount;
      const cpX2 = p0.x + (2 * (p1.x - p0.x)) / 3;
      const cpY2 = p1.yCount;
      pathCount += ` C ${cpX1} ${cpY1}, ${cpX2} ${cpY2}, ${p1.x} ${p1.yCount}`;

      const cpY1_r = p0.yRate;
      const cpY2_r = p1.yRate;
      pathRate += ` C ${cpX1} ${cpY1_r}, ${cpX2} ${cpY2_r}, ${p1.x} ${p1.yRate}`;
    }
  }

  return {
    points,
    pathCount,
    pathRate,
    maxCount
  };
});

// Hospital Grouping
const groupedHospitals = computed(() => {
  const hospitalCounts: Record<string, { count: number; cases: ClaimCase[] }> = {};
  
  groupedClaimCases.value.forEach(claimCase => {
    if (!hospitalCounts[claimCase.hospital]) {
      hospitalCounts[claimCase.hospital] = { count: 0, cases: [] };
    }
    hospitalCounts[claimCase.hospital].count += claimCase.count; // sum failure occurrences
    hospitalCounts[claimCase.hospital].cases.push(claimCase);
  });

  return Object.entries(hospitalCounts).map(([hospital, data]) => {
    // Calculate resolution rate based on cases
    const totalCases = data.cases.length;
    const resolvedCases = data.cases.filter(c => c.state === '최종완료').length;
    const resolutionRate = totalCases > 0 ? (resolvedCases / totalCases) * 100 : 0;

    return {
      hospital,
      count: data.count,
      casesCount: totalCases,
      resolutionRate,
      cases: data.cases
    };
  });
});

const filteredHospitals = computed(() => {
  const search = hospitalSearch.value.trim().toLowerCase();
  if (!search) return groupedHospitals.value.slice().sort((a, b) => b.casesCount - a.casesCount);

  return groupedHospitals.value
    .filter(h => h.hospital.toLowerCase().includes(search))
    .sort((a, b) => b.casesCount - a.casesCount);
});

const hospitalTotalPages = computed(() => Math.ceil(filteredHospitals.value.length / itemsPerPage));

const paginatedHospitals = computed(() => {
  const start = (hospitalPage.value - 1) * itemsPerPage;
  return filteredHospitals.value.slice(start, start + itemsPerPage);
});

// EMR Grouping
const groupedEmrs = computed(() => {
  const emrCounts: Record<string, { count: number; cases: ClaimCase[] }> = {};
  
  groupedClaimCases.value.forEach(claimCase => {
    if (!emrCounts[claimCase.emr]) {
      emrCounts[claimCase.emr] = { count: 0, cases: [] };
    }
    emrCounts[claimCase.emr].count += claimCase.count; // sum failure occurrences
    emrCounts[claimCase.emr].cases.push(claimCase);
  });

  return Object.entries(emrCounts).map(([emr, data]) => {
    // Calculate resolution rate based on cases
    const totalCases = data.cases.length;
    const resolvedCases = data.cases.filter(c => c.state === '최종완료').length;
    const resolutionRate = totalCases > 0 ? (resolvedCases / totalCases) * 100 : 0;

    return {
      emr,
      count: data.count,
      casesCount: totalCases,
      resolutionRate,
      cases: data.cases
    };
  });
});

const filteredEmrs = computed(() => {
  const search = emrSearch.value.trim().toLowerCase();
  if (!search) return groupedEmrs.value.slice().sort((a, b) => b.casesCount - a.casesCount);

  return groupedEmrs.value
    .filter(e => e.emr.toLowerCase().includes(search))
    .sort((a, b) => b.casesCount - a.casesCount);
});

const emrTotalPages = computed(() => Math.ceil(filteredEmrs.value.length / itemsPerPage));

const paginatedEmrs = computed(() => {
  const start = (emrPage.value - 1) * itemsPerPage;
  return filteredEmrs.value.slice(start, start + itemsPerPage);
});

// File Summary Table Grouping (incorporating Resolution Rate)
const fileSummary = computed(() => {
  const fileStats: Record<string, { rawCount: number; totalCases: number; resolvedCases: number }> = {};
  
  allFileKeys.value.forEach(key => {
    fileStats[key] = { rawCount: 0, totalCases: 0, resolvedCases: 0 };
  });

  // Count raw failure rows
  rawRows.value.forEach(row => {
    if (row.fileKey && fileStats[row.fileKey]) {
      fileStats[row.fileKey].rawCount++;
    }
  });

  // Count unique grouped claim cases and resolved cases
  groupedClaimCases.value.forEach(claimCase => {
    if (claimCase.fileKey && fileStats[claimCase.fileKey]) {
      fileStats[claimCase.fileKey].totalCases++;
      if (claimCase.state === '최종완료') {
        fileStats[claimCase.fileKey].resolvedCases++;
      }
    }
  });

  const sortedFiles = Object.entries(fileStats).sort((a, b) => a[0].localeCompare(b[0]));

  return sortedFiles.map(([fileKey, data]) => {
    const rawCount = data.rawCount;
    const totalCases = data.totalCases;
    const resolvedCases = data.resolvedCases;
    const resolutionRate = totalCases > 0 ? (resolvedCases / totalCases) * 100 : 0;
    
    let displayName = fileKey.replace(/_/g, '-');
    if (fileKey === '20260622_20260629') {
      displayName = '20260623-20260629';
    }

    return {
      fileName: fileKey,
      displayName,
      count: totalCases, // total unique grouped failure cases count
      resolutionRate // resolved cases percentage
    };
  });
});

// 9. Detail Dialog Computed Data (Claim Cases drilldown)
const detailTarget = computed(() => {
  if (!detailTargetName.value) return null;
  const name = detailTargetName.value;
  
  const cases = groupedClaimCases.value.filter(c => 
    detailTargetType.value === 'hospital' ? c.hospital === name : c.emr === name
  );

  // Sort claim cases by count descending (largest failure count first)
  cases.sort((a, b) => b.count - a.count);

  const count = cases.length; // total cases count
  const sentCount = cases.filter(c => c.state === '회신대기').length;
  const confirmedCount = cases.filter(c => c.state === '최종완료').length;

  return {
    name,
    count,
    sentCount,
    confirmedCount,
    cases
  };
});

const detailTotalPages = computed(() => {
  if (!detailTarget.value) return 0;
  return Math.ceil(detailTarget.value.cases.length / detailItemsPerPage);
});

const paginatedDetailRows = computed(() => {
  if (!detailTarget.value) return [];
  const start = (detailPage.value - 1) * detailItemsPerPage;
  return detailTarget.value.cases.slice(start, start + detailItemsPerPage);
});

// 10. Actions & Mutating State via Backend API
async function updateHospitalState(hospital: string, state: RowState) {
  isLoading.value = true;
  try {
    const hCases = groupedClaimCases.value.filter(c => c.hospital === hospital);
    const promises = hCases.map(c => 
      fetch(`${API_BASE_URL}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fileKey: c.fileKey,
          hospital: c.hospital,
          patient: c.patient,
          birthDate: c.birthDate,
          category: c.category,
          visitDate: c.visitDate,
          uuid: c.uuid,
          state: state
        })
      }).then(res => {
        if (!res.ok) throw new Error('API failed');
        return res;
      })
    );
    await Promise.all(promises);

    // Apply to local state immediately
    hCases.forEach(c => {
      persistedStates.value[c.key] = state;
    });
  } catch (error) {
    console.error('병원 상태 업데이트 실패:', error);
  } finally {
    isLoading.value = false;
  }
}

async function updateEmrState(emr: string, state: RowState) {
  isLoading.value = true;
  try {
    const eCases = groupedClaimCases.value.filter(c => c.emr === emr);
    const promises = eCases.map(c => 
      fetch(`${API_BASE_URL}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fileKey: c.fileKey,
          hospital: c.hospital,
          patient: c.patient,
          birthDate: c.birthDate,
          category: c.category,
          visitDate: c.visitDate,
          uuid: c.uuid,
          state: state
        })
      }).then(res => {
        if (!res.ok) throw new Error('API failed');
        return res;
      })
    );
    await Promise.all(promises);

    // Apply to local state immediately
    eCases.forEach(c => {
      persistedStates.value[c.key] = state;
    });
  } catch (error) {
    console.error('EMR 상태 업데이트 실패:', error);
  } finally {
    isLoading.value = false;
  }
}

async function toggleCaseState(claimCase: ClaimCase) {
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
      // Apply to local state immediately
      persistedStates.value[key] = nextState;
    } else {
      console.error('상태 변경 실패');
    }
  } catch (error) {
    console.error('상태 변경 중 오류 발생:', error);
  } finally {
    isLoading.value = false;
  }
}

function getRowButtonLabel(state: RowState): string {
  if (state === '미확인') return '회신대기';
  if (state === '회신대기') return '최종완료';
  return '되돌리기';
}

function openHospitalDetail(item: { hospital: string }) {
  router.push({
    path: '/error-statistics/detail',
    query: {
      type: 'hospital',
      name: item.hospital
    }
  });
}

function openEmrDetail(item: { emr: string }) {
  router.push({
    path: '/error-statistics/detail',
    query: {
      type: 'emr',
      name: item.emr
    }
  });
}

// Formatting utils
function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num);
}

function getStatusColor(state: RowState): string {
  if (state === '회신대기') return '#e28743'; // Orange
  if (state === '최종완료') return '#2dce89'; // Green
  return '#718096'; // Grey
}

// 11. Watchers
watch([hospitalSearch, emrSearch], () => {
  hospitalPage.value = 1;
  emrPage.value = 1;
});

// 12. Lifecycle
onMounted(() => {
  loadExcelData();
});
</script>

<style scoped>
.error-monitor-section {
  font-family: 'Pretendard', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
  background-color: #f8fafc;
}

/* Premium SaaS Card Layout matching user mockup */
.premium-card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px -2px rgba(50, 50, 93, 0.04), 0 2px 8px -1px rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(226, 232, 240, 0.8);
  padding: 22px 26px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.premium-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.01);
  border-color: rgba(203, 213, 225, 0.8);
}

/* Soft UI Badge styles */
.card-badge-percentage {
  font-size: 11px !important;
  font-weight: 700 !important;
  padding: 2px 8px !important;
  border-radius: 6px !important;
  line-height: 1.2 !important;
  display: inline-flex !important;
  align-items: center !important;
}
.badge-blue {
  background-color: #eff6ff !important;
  color: #3b82f6 !important;
}
.badge-orange {
  background-color: #fffbeb !important;
  color: #d97706 !important;
}
.badge-green {
  background-color: #ecfdf5 !important;
  color: #10b981 !important;
}

/* Soft UI Interactive Charts */
.chart-gradient-card {
  background: #ffffff !important;
  border-radius: 16px !important;
  border: 1px solid rgba(226, 232, 240, 0.8) !important;
  box-shadow: 0 4px 20px -2px rgba(50, 50, 93, 0.04) !important;
  overflow: hidden;
}
.chart-gradient-bg {
  background: linear-gradient(135deg, #1565c0 0%, #6a1b9a 100%);
  padding: 15px;
  border-radius: 12px;
  margin: 15px 15px 0 15px;
  box-shadow: 0 8px 26px -4px rgba(21, 101, 192, 0.3);
}
.active-users-svg {
  width: 100%;
  height: auto;
  display: block;
}
.chart-bar-rect {
  transition: fill-opacity 0.2s ease, transform 0.2s ease;
  transform-origin: bottom;
  cursor: pointer;
}
.chart-bar-rect:hover {
  fill-opacity: 0.8;
  transform: scaleY(1.05);
}

.chart-card-subtitle {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.chart-card-title {
  font-size: 16px;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.chart-card-desc {
  font-size: 12px;
  line-height: 1.5;
}

.chart-curve-card {
  background: #ffffff !important;
  border-radius: 16px !important;
  border: 1px solid rgba(226, 232, 240, 0.8) !important;
  box-shadow: 0 4px 20px -2px rgba(50, 50, 93, 0.04) !important;
  overflow: hidden;
}
.chart-curve-body {
  position: relative;
}
.curve-chart-svg {
  width: 100%;
  height: auto;
  display: block;
}
.chart-curve-path {
  filter: drop-shadow(0px 4px 6px rgba(59, 130, 246, 0.15));
}
.chart-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.chart-dot.bg-blue { background-color: #3b82f6; }
.chart-dot.bg-purple { background-color: #8b5cf6; }

.chart-point-dot {
  cursor: pointer;
  transition: r 0.2s ease, fill-opacity 0.2s ease;
}
.chart-point-dot:hover {
  r: 8;
  fill-opacity: 0.9;
}

.svg-grid-text {
  font-size: 9px;
  fill: #94a3b8;
  font-weight: 600;
}
.svg-axis-label {
  font-size: 9px;
  fill: #64748b;
  font-weight: 700;
}

.card-left {
  display: flex;
  flex-direction: column;
}

.card-title-text {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-value-text {
  font-size: 26px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.card-unit-text {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  margin-left: 2px;
}

.card-right {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}
.premium-card:hover .card-right {
  transform: scale(1.1) rotate(5deg);
}

.icon-box-blue {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.icon-box-orange {
  background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
}

.icon-box-green {
  background: linear-gradient(135deg, #10b981 0%, #047857 100%);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}

/* Table Cards styling */
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

/* Search Box Input */
.search-box {
  width: 220px;
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

.search-input :deep(.v-input__control) {
  height: 36px !important;
}

/* Tables styling */
.dashboard-table {
  width: 100%;
  border-collapse: collapse;
}

.dashboard-table :deep(table) {
  width: 100%;
}

.dashboard-table :deep(th) {
  background-color: #f8fafc !important;
  color: #475569 !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  padding: 14px 18px !important;
  border-bottom: 1px solid #e2e8f0 !important;
  white-space: nowrap !important;
  letter-spacing: 0.03em;
}

.dashboard-table :deep(td) {
  padding: 14px 18px !important;
  font-size: 13px !important;
  color: #334155 !important;
  border-bottom: 1px solid #f1f5f9 !important;
  white-space: nowrap !important;
  transition: all 0.2s ease;
}

.dashboard-table {
  min-width: 480px !important;
}

.dashboard-table :deep(tr) {
  position: relative;
  transition: background-color 0.2s ease;
}

.dashboard-table :deep(tr:hover) {
  background-color: #f8fafc !important;
}

/* Hover sliding line indicator */
.dashboard-table :deep(tr::after) {
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
.dashboard-table :deep(tr:hover::after) {
  opacity: 1;
}

.status-chip {
  font-weight: 700 !important;
  font-size: 11px !important;
  padding: 0 10px !important;
  border-radius: 4px !important;
  height: 24px !important;
  cursor: pointer;
  color: #ffffff !important;
}

.status-chip-fixed {
  font-weight: 700 !important;
  font-size: 10px !important;
  padding: 0 8px !important;
  border-radius: 4px !important;
  height: 20px !important;
  color: #ffffff !important;
}

.action-link {
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  transition: all 0.2s ease;
}

.action-link:hover {
  color: #1d4ed8;
  transform: translateX(3px);
}

.text-green {
  color: #10b981 !important;
  font-weight: 700;
}

.text-orange {
  color: #f59e0b !important;
  font-weight: 700;
}

/* Dialog Styling */
.dialog-stat-box {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.01);
  transition: all 0.2s ease;
}

.box-total { border-top: 4px solid #3b82f6; }
.box-sent { border-top: 4px solid #f59e0b; }
.box-confirmed { border-top: 4px solid #10b981; }

.stat-label {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  margin-bottom: 6px;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 20px;
  font-weight: 800;
  color: #1e293b;
}

.text-blue { color: #3b82f6; }
.text-orange { color: #f59e0b; }
.text-green { color: #10b981; }

.bg-slate-50 {
  background-color: #f8fafc;
}

.detail-inner-table {
  width: 100%;
}

.detail-inner-table :deep(th) {
  background-color: #ebf2fc !important;
  color: #4a5568 !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  padding: 8px 12px !important;
  border-bottom: 1px solid #cbd5e1 !important;
}

.detail-inner-table :deep(td) {
  padding: 8px 12px !important;
  font-size: 12px !important;
  border-bottom: 1px solid #edf2f7 !important;
}

.action-btn-small {
  font-size: 10px !important;
  font-weight: 700 !important;
  height: 22px !important;
  padding: 0 8px !important;
}
</style>