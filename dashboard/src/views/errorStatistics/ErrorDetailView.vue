<template>
  <!-- [수정] 메인 대시보드와 일체감을 주는 화면 최대 폭 제한 래퍼 장착 -->
  <div class="dashboard-fluid-wrapper">
    <v-container fluid class="error-detail-section pt-1 px-1 pb-6">

      <!-- Header Block -->
      <div class="d-flex align-center mb-5 mt-2 px-1">
        <v-btn
            icon="mdi-arrow-left"
            variant="elevated"
            elevation="1"
            class="mr-4 back-btn"
            color="white"
            @click="goBack"
        ></v-btn>
        <div>
          <h1 class="text-h6 font-weight-bold text-slate-800 leading-tight">
            [{{ targetType === 'hospital' ? '요양기관' : 'EMR사' }} 상세내역] {{ targetName }}
          </h1>
          <span class="text-caption text-grey-500 font-weight-medium">
            조회 차수: <v-chip size="x-small" color="primary" variant="flat" class="font-weight-bold ml-1">{{ currentFileKey ? currentFileKey.replace(/_/g, '-') : '전체' }}</v-chip>
          </span>
        </div>
      </div>

      <!-- Summary Metrics Cards (Flexbox 한 줄 매칭 정렬) -->
      <div class="kpi-cards-container mb-4" v-if="targetSummary">
        <!-- 1) 총 청구오류 건수 -->
        <div class="premium-card">
          <div class="card-left">
            <span class="card-title-text">총 청구오류 건수</span>
            <div class="d-flex align-end mt-2">
              <span class="card-value-text text-blue">{{ formatNumber(targetSummary.count) }}</span>
              <span class="caption text-grey ml-1.5 pb-0.5 font-weight-medium">건</span>
            </div>
          </div>
          <div class="card-right icon-box-blue">
            <v-icon size="small" color="white">mdi-alert-circle</v-icon>
          </div>
        </div>

        <!-- 2) 회신대기 건수 -->
        <div class="premium-card">
          <div class="card-left">
            <span class="card-title-text">회신대기 건수</span>
            <div class="d-flex align-end mt-2">
              <span class="card-value-text text-orange">{{ formatNumber(targetSummary.sentCount) }}</span>
              <span class="caption text-grey ml-1.5 pb-0.5 font-weight-medium">건</span>
            </div>
          </div>
          <div class="card-right icon-box-orange">
            <v-icon size="small" color="white">mdi-email-send</v-icon>
          </div>
        </div>

        <!-- 3) 최종완료 건수 -->
        <div class="premium-card">
          <div class="card-left">
            <span class="card-title-text">최종완료 건수</span>
            <div class="d-flex align-end mt-2">
              <span class="card-value-text text-green">{{ formatNumber(targetSummary.confirmedCount) }}</span>
              <span class="caption text-grey ml-1.5 pb-0.5 font-weight-medium">건</span>
            </div>
          </div>
          <div class="card-right icon-box-green">
            <v-icon size="small" color="white">mdi-check-decagram</v-icon>
          </div>
        </div>
      </div>

      <!-- EMR Hospital Filter Grid -->
      <div v-if="targetType === 'emr' && emrHospitalsSummary.length > 0" class="mb-4 px-1">
        <div class="text-caption font-weight-bold mb-2 text-slate-800 d-flex align-center">
          <v-icon size="x-small" class="mr-1" color="primary">mdi-hospital-building</v-icon> EMR 사용 요양기관 필터
        </div>
        <v-row class="g-2 mx-n1">
          <v-col cols="12" sm="6" md="3" class="px-1 py-1">
            <v-card
                :class="['metric-filter-card', selectedHospitalFilter === 'all' ? 'active-card' : '']"
                @click="selectedHospitalFilter = 'all'"
                elevation="0"
            >
              <div class="d-flex flex-column py-2.5 px-4">
                <span class="text-caption text-grey-darken-1 font-weight-medium">요양기관 전체</span>
                <div class="d-flex align-baseline mt-1 justify-space-between">
                  <span class="text-subtitle-1 font-weight-bold text-slate-900">{{ allRows.length }} 건</span>
                  <span class="text-caption font-weight-bold text-blue">{{ targetSummary.confirmedCount }} / {{ targetSummary.count }} 완료</span>
                </div>
              </div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3" v-for="h in emrHospitalsSummary" :key="h.hospital" class="px-1 py-1">
            <v-card
                :class="['metric-filter-card', selectedHospitalFilter === h.hospital ? 'active-card' : '']"
                @click="selectedHospitalFilter = h.hospital"
                elevation="0"
            >
              <div class="d-flex flex-column py-2.5 px-4">
                <span class="text-caption text-grey-darken-1 font-weight-bold text-truncate" style="max-width: 180px;">{{ h.hospital }}</span>
                <div class="d-flex align-baseline mt-1 justify-space-between">
                  <span class="text-subtitle-1 font-weight-bold text-slate-900">{{ h.casesCount }} 건</span>
                  <span class="text-caption font-weight-bold text-green">{{ h.resolutionRate.toFixed(0) }}% 완료</span>
                </div>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </div>

      <!-- Table Card (여백 쫀쫀하게 밀착 리사이징) -->
      <v-card class="table-card mx-1" elevation="0">
        <v-card-title class="d-flex justify-space-between align-center py-4 px-5 table-card-header">
          <span class="table-card-title">상세 청구 오류 리스트</span>
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
        </v-card-title>

        <v-table class="dashboard-table">
          <thead>
          <tr>
            <th class="text-center" style="width: 55px;">No</th>
            <th class="text-left" style="min-width: 160px;">요청 대상 요양기관명</th>
            <th class="text-left" style="min-width: 260px;">청구실패 사유 (오류 내용)</th>
            <th class="text-right" style="width: 100px;">실패 건수</th>
            <th class="text-center" style="width: 130px;">H열 상태</th>
            <th class="text-center" style="width: 100px;">액션</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="(row, idx) in paginatedRows" :key="row.key">
            <td class="text-center text-slate-400">{{ (currentPage - 1) * itemsPerPage + idx + 1 }}</td>
            <td class="text-left font-weight-medium text-slate-800">{{ row.hospital }}</td>
            <td class="text-left text-body-2 font-weight-medium text-wrap-pretty">{{ row.category }}</td>
            <td class="text-right font-weight-bold text-slate-700">{{ formatNumber(row.count) }} 건</td>
            <td class="text-center">
              <v-chip :color="getStatusColor(row.state)" variant="flat" size="small" class="status-chip-fixed">
                {{ row.state }}
              </v-chip>
            </td>
            <td class="text-center">
              <v-btn
                  size="x-small"
                  :color="row.state === '최종완료' ? 'warning' : row.state === '회신대기' ? 'success' : 'primary'"
                  variant="flat"
                  class="action-btn-capsule"
                  @click="toggleRowState(row)"
              >
                {{ getRowButtonLabel(row.state) }}
              </v-btn>

            </td>
          </tr>
          <tr v-if="filteredRows.length === 0">
            <td colspan="6" class="text-center py-10 text-slate-400">데이터가 없습니다.</td>
          </tr>
          </tbody>
        </v-table>

        <!-- Pagination -->
        <div class="d-flex justify-center align-center py-3" v-if="totalPages > 1">
          <v-pagination
              v-model="currentPage"
              :length="totalPages"
              total-visible="5"
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

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

const targetType = ref<'hospital' | 'emr'>((route.query.type as 'hospital' | 'emr') || 'hospital');
const targetName = ref<string>((route.query.name as string) || '');

// [핵심 수정] 라우터 쿼리에 실려온 대시보드 선택 차수 fileKey를 명확하게 포착
const currentFileKey = ref<string>((route.query.fileKey as string) || '');

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000') + '/api/errorStatistics';

const allRows = ref<ClaimCase[]>([]);
const persistedStates = ref<Record<string, RowState>>({});
const isLoading = ref(false);
const searchQuery = ref('');
const currentPage = ref(1);
const itemsPerPage = 10;
const selectedHospitalFilter = ref<string>('all');

function getGroupKey(row: ErrorDetail): string {
  let cleanDetails = row.details || '';
  if (cleanDetails.includes('===')) {
    cleanDetails = cleanDetails.split(/={3,}/)[0].trim();
  }
  const errorTitle = row.category && !row.category.includes('미분류') ? row.category : cleanDetails.substring(0, 40);
  return `${row.fileKey}|${row.hospital.trim()}|${errorTitle}`;
}

function goBack() {
  router.push('/error-statistics');
}

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

    // [로직 개편] 만약 주소창에 특정 fileKey가 명시되어 들어온 경우, 해당 파일 데이터만 핀포인트 로드하여 과거 데이터 노출 현상 완전 원천 봉쇄
    if (currentFileKey.value) {
      fileKeys = fileKeys.filter(key => key === currentFileKey.value);
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

    const groups: Record<string, ErrorDetail[]> = {};
    loadedDetailRows.forEach(row => {
      const key = getGroupKey(row);
      if (!groups[key]) groups[key] = [];
      groups[key].push(row);
    });

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

    // 병원명 혹은 EMR사 명칭 기준 일치 로우 압축 스크리닝
    allRows.value = cases.filter(c =>
        targetType.value === 'hospital' ? c.hospital === targetName.value : c.emr === targetName.value
    );

    allRows.value.sort((a, b) => b.count - a.count);
    selectedHospitalFilter.value = 'all';

  } catch (error) {
    console.error('상세 내역 동적 파싱 실패:', error);
  } finally {
    isLoading.value = false;
  }
}

const targetSummary = computed(() => {
  if (allRows.value.length === 0) return { count: 0, sentCount: 0, confirmedCount: 0 };
  const count = allRows.value.reduce((sum, c) => sum + c.count, 0);
  const sentCount = allRows.value.filter(c => persistedStates.value[c.key] === '회신대기').reduce((sum, c) => sum + c.count, 0);
  const confirmedCount = allRows.value.filter(c => persistedStates.value[c.key] === '최종완료').reduce((sum, c) => sum + c.count, 0);
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

// 4. Actions (되돌리기 순환 구조 반영)
async function toggleRowState(claimCase: ClaimCase) {
  const key = claimCase.key;
  const currentState = persistedStates.value[key] || '미확인';

  let nextState: RowState = '미확인';

  // 상태 순환 구조 설계: 미확인 ➡️ 회신대기 ➡️ 최종완료 ➡️ (되돌리기 클릭 시) 회신대기
  if (currentState === '미확인') {
    nextState = '회신대기';
  } else if (currentState === '회신대기') {
    nextState = '최종완료';
  } else if (currentState === '최종완료') {
    // 🌟 [핵심] 최종완료 상태에서 버튼(되돌리기)을 누르면 다시 '회신대기' 상태로 백업
    nextState = '회신대기';
  }

  isLoading.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fileKey: claimCase.fileKey, // 대시보드에서 지정해서 들어온 단일 파일 키
        hospital: claimCase.hospital,
        patient: claimCase.patient,
        birthDate: claimCase.birthDate,
        category: claimCase.category,
        state: nextState // 변경될 상태값 전송
      })
    });

    if (res.ok) {
      // 엑셀 저장 성공 시 화면의 실시간 진행 상태(persistedStates) 즉시 업데이트
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

// 버튼 라벨 정의
function getRowButtonLabel(state: RowState): string {
  if (state === '미확인') return '회신대기';
  if (state === '회신대기') return '최종완료';
  return '되돌리기'; // '최종완료' 상태일 때 텍스트 매핑
}

function getStatusColor(state: RowState): string {
  if (state === '회신대기') return '#fb6340';
  if (state === '최종완료') return '#2dce89';
  return '#718096';
}

function formatNumber(num: number): string { return new Intl.NumberFormat().format(num || 0); }
watch(searchQuery, () => { currentPage.value = 1; });
onMounted(() => { loadData(); });
</script>

<style scoped>
/* 100% 가로 꽉 찬 시원한 유연 구조 매핑 및 1400px 브레이크 래퍼 */
.dashboard-fluid-wrapper {
  width: 100%;
  max-width: 100% !important;
  padding: 0 4px;
}

.error-detail-section {
  font-family: 'Pretendard', sans-serif;
  background-color: #f8fafc;
  min-height: 100vh;
}

.back-btn {
  border: 1px solid rgba(15, 23, 42, 0.05) !important;
  border-radius: 8px !important;
  transition: all 0.2s ease;
}
.back-btn:hover {
  background-color: #f1f5f9 !important;
  transform: translateX(-2px);
}

.file-select-box { max-width: 240px; }

/* 요약 카드 계층화 단일화 패키지 */
.kpi-cards-container {
  display: flex;
  gap: 12px;
  width: 100%;
}

.premium-card {
  flex: 1 1 0px;
  min-width: 190px;
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid rgba(15, 23, 42, 0.04);
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 94px;
  box-shadow: 0 15px 20px 0 rgba(0,0,0,0.04);
}

.card-left { display: flex; flex-direction: column; width: 100%; overflow: hidden; }
.card-title-text { font-size: 11.5px; font-weight: 700; color: #64748b; }
.card-value-text { font-size: 21px; font-weight: 800; line-height: 1.1; }

.card-right { width: 32px; height: 32px; border-radius: 7px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.icon-box-blue { background: linear-gradient(310deg, #60a5fa 0%, #2563eb 100%); }
.icon-box-orange { background: linear-gradient(310deg, #fb923c 0%, #ea580c 100%); }
.icon-box-green { background: linear-gradient(310deg, #4ade80 0%, #16a34a 100%); }

.text-blue { color: #2563eb !important; }
.text-orange { color: #fb6340 !important; }
.text-green { color: #2dce89 !important; }

/* 서브 필터 아이템 디자인 쫀쫀하게 정렬 */
.metric-filter-card {
  border: 1px solid rgba(15, 23, 42, 0.05) !important;
  border-radius: 12px !important;
  cursor: pointer;
  background-color: #ffffff !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.01) !important;
  transition: all 0.2s ease;
}
.metric-filter-card:hover {
  border-color: #2563eb !important;
  transform: translateY(-1px);
}
.metric-filter-card.active-card {
  border-color: #2563eb !important;
  border-width: 1.5px !important;
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.08) !important;
  background-color: #eff6ff !important;
}

/* 테이블 패널 가공 */
.table-card {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid rgba(15, 23, 42, 0.04);
  box-shadow: 0 15px 20px 0 rgba(0,0,0,0.04);
  overflow: hidden;
}

.table-card-title { font-size: 13.5px; font-weight: 700; color: #0f172a; }
.table-card-header { border-bottom: 1px solid #f1f5f9; background-color: #ffffff; }
.search-box { width: 220px; }
.search-input :deep(.v-field) { border-radius: 6px !important; }

/* 메인 그리드 테이블 패딩 최소 압축 정합 */
.dashboard-table { width: 100%; border-collapse: collapse; }
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
  padding: 9px 14px !important;
  font-size: 12.5px !important;
  color: #334155 !important;
  border-bottom: 1px solid #f0f0f0 !important;
}
.dashboard-table :deep(tr:hover) { background-color: #f8fafc !important; }

/* 엑셀 연동 소프트 민트/연두 감성의 파스텔 뱃지 컬러 세팅 */
.status-chip-fixed {
  font-weight: 700 !important;
  font-size: 10.5px !important;
  padding: 0 10px !important;
  border-radius: 5px !important;
  height: 22px !important;
}
.status-chip-fixed[color="#718096"] {
  background-color: #f1f5f9 !important;
  color: #64748b !important;
}
.status-chip-fixed[color="#fb6340"] {
  background-color: #fff5e6 !important;
  color: #fb6340 !important;
}
.status-chip-fixed[color="#2dce89"] {
  background-color: #e6f7e9 !important;
  color: #2dce89 !important;
}

.action-btn-capsule {
  font-weight: 700 !important;
  font-size: 11px !important;
  border-radius: 6px !important;
}
</style>