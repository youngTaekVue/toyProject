<template>
  <section class="error-dashboard">
    <div class="section-header">
      <div>
        <p class="breadcrumb">Pages / API Failures</p>
        <h2>Excel 기반 오류 모니터링</h2>
        <p class="section-subtitle">헤더가 반복되는 Excel을 JSON 형태로 가공하고, 병원/오류 유형별 현황과 상세 리스트를 확인합니다.</p>
      </div>

      <div class="filter-row">
        <v-select
          v-model="selectedPeriod"
          :items="periodOptions"
          item-title="label"
          item-value="value"
          label="기간"
          density="comfortable"
          hide-details
          class="filter-input"
        />

        <v-select
          v-model="selectedHospital"
          :items="hospitalOptions"
          item-title="label"
          item-value="value"
          label="병원"
          density="comfortable"
          hide-details
          class="filter-input"
        />

        <v-select
          v-model="selectedEmr"
          :items="emrOptions"
          item-title="label"
          item-value="value"
          label="EMR사"
          density="comfortable"
          hide-details
          class="filter-input"
        />

        <v-select
          v-model="selectedState"
          :items="stateOptions"
          item-title="label"
          item-value="value"
          label="진행 상태"
          density="comfortable"
          hide-details
          class="filter-input"
        />

        <v-btn class="action-button" variant="tonal" color="primary" @click="loadExcelData">Excel 다시 불러오기</v-btn>
      </div>
    </div>

    <v-row class="summary-cards">
      <v-col cols="12" sm="6" md="4" lg="3">
        <div class="card neumorphic-card">
          <div>
            <h4>총 오류 건수</h4>
            <p class="card-value">{{ totalIssues }}건</p>
          </div>
          <div class="card-icon"><v-icon>mdi-alert-circle</v-icon></div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="3">
        <div class="card neumorphic-card">
          <div>
            <h4>오류율</h4>
            <p class="card-value">{{ errorRate }}% <span class="growth-positive">{{ failureCount }}건</span></p>
          </div>
          <div class="card-icon"><v-icon>mdi-chart-pie</v-icon></div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="3">
        <div class="card neumorphic-card">
          <div>
            <h4>확인요청 중</h4>
            <p class="card-value">{{ pendingRequests }}건</p>
          </div>
          <div class="card-icon"><v-icon>mdi-bell-alert</v-icon></div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="3">
        <div class="card neumorphic-card">
          <div>
            <h4>심각도 높은 건</h4>
            <p class="card-value">{{ criticalCount }}건</p>
          </div>
          <div class="card-icon"><v-icon>mdi-flame</v-icon></div>
        </div>
      </v-col>
    </v-row>

    <div class="status-summary">
      <div class="status-card neumorphic-card" v-for="item in stateSummary" :key="item.label">
        <h5>{{ item.label }}</h5>
        <p>{{ item.count }}건</p>
      </div>
    </div>

    <div class="charts-section">
      <v-row>
        <v-col cols="12" lg="6">
          <div class="chart-card neumorphic-card">
            <div class="chart-header">
              <div>
                <h4>병원별 오류 건수</h4>
                <p>병원별로 얼마나 많은 오류가 발생했는지 비교합니다.</p>
              </div>
            </div>
            <apexchart
              type="bar"
              height="320"
              :options="barChartOptions"
              :series="barChartSeries"
            />
          </div>
        </v-col>

        <v-col cols="12" lg="6">
          <div class="chart-card neumorphic-card">
            <div class="chart-header">
              <div>
                <h4>오류 유형 비중</h4>
                <p>오류 카테고리가 전체에서 차지하는 비율입니다.</p>
              </div>
            </div>
            <apexchart
              type="donut"
              height="320"
              :options="donutChartOptions"
              :series="donutSeries"
            />
          </div>
        </v-col>
      </v-row>
    </div>

    <div class="details-panel">
      <div class="detail-tabs">
        <button
          v-for="option in categoryOptions"
          :key="option.value"
          :class="['detail-tab', { active: selectedCategory.value === option.value }]"
          @click="selectedCategory.value = option.value"
          type="button"
        >
          {{ option.label }} ({{ option.count }})
        </button>
      </div>

      <div class="table-responsive-wrapper">
        <div class="project-table neumorphic-card">
          <h4>상세 오류 목록</h4>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>기관번호</th>
                <th>EMR사</th>
                <th>피보험자</th>
                <th>생년월일</th>
                <th>오류 사유</th>
                <th>진료 내역</th>
                <th>심각도</th>
                <th>진행 상태</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in visibleRows"
                :key="row.key"
                :class="rowHighlightClass(row)"
              >
                <td>{{ row.no }}</td>
                <td>{{ row.institutionId }}</td>
                <td>{{ row.emr }}</td>
                <td>{{ row.patient }}</td>
                <td>{{ row.birthDate }}</td>
                <td>{{ row.category }}</td>
                <td>{{ row.details }}</td>
                <td>{{ row.severity }}</td>
                <td><span :class="statusPillClass(row.state)">{{ row.state }}</span></td>
                <td>
                  <button
                    class="action-button"
                    :class="rowButtonClass(row.state)"
                    :disabled="row.state === '완료'"
                    @click="toggleRowState(row)"
                    type="button"
                  >
                    {{ row.state === '요청예정' ? '확인요청' : row.state === '확인요청' ? '수정요청' : row.state === '수정요청함' ? '완료 처리' : '완료' }}
                  </button>
                </td>
              </tr>
              <tr v-if="visibleRows.length === 0">
                <td colspan="10" class="empty-row">선택된 카테고리에 해당하는 오류가 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="json-card neumorphic-card">
      <h4>가공된 JSON 예시</h4>
      <pre>{{ jsonPreview }}</pre>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import * as XLSX from 'xlsx';

type RowState = '요청예정' | '확인요청' | '수정요청함' | '완료';

interface RawRow {
  [key: string]: unknown;
}

interface ErrorDetail {
  no: number;
  key: string;
  hospital: string;
  institutionId: string;
  emr: string;
  patient: string;
  birthDate: string;
  category: string;
  details: string;
  visitDate: string;
  uuid: string;
  severity: string;
  ageDays: number;
  state: RowState;
  dateObject: Date;
  [key: string]: unknown;
}

interface ReportDetail {
  no: number;
  visitDate: string;
  uuid: string;
  state: RowState;
  severity: string;
}

interface ReportError {
  category: string;
  count: number;
  details: ReportDetail[];
}

interface ReportPayload {
  hospital: string;
  reportDate: string;
  errors: ReportError[];
}

const storageKey = 'error-monitoring-row-states';
const defaultHospital = '알 수 없는 병원';

const selectedPeriod = ref<string>('all');
const selectedHospital = ref<string>('all');
const selectedEmr = ref<string>('all');
const selectedState = ref<string>('all');
const selectedCategory = ref<string>('all');
const rawRows = ref<RawRow[]>([]);
const persistedStates = ref<Record<string, RowState>>({});

const periodOptions = [
  { label: '전체 파일', value: 'all' },
  { label: '2026-05-01 ~ 2026-06-22', value: '20260501~20260622' },
  { label: '2026-06-23 ~ 2026-06-29', value: '20260623~20260629' },
];

const hospitalOptions = computed(() => {
  const hospitals = new Set<string>(rawRows.value.map((row) => asString(row.hospital, defaultHospital)));
  const items = Array.from(hospitals).map((hospital) => ({ label: hospital, value: hospital }));
  items.unshift({ label: '전체 병원', value: 'all' });
  return items;
});

const emrOptions = computed(() => {
  const emrs = new Set<string>(rawRows.value.map((row) => asString(row.emr, '알 수 없음')));
  const items = Array.from(emrs).map((emr) => ({ label: emr, value: emr }));
  items.unshift({ label: '전체 EMR사', value: 'all' });
  return items;
});

const stateOptions = computed(() => {
  const counts = normalizedRows.value.reduce<Record<string, number>>((acc, row) => {
    acc[row.state] = (acc[row.state] || 0) + 1;
    return acc;
  }, {});
  const states = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([state, count]) => ({ label: `${state} (${count})`, value: state, count }));
  return [{ label: '전체 상태', value: 'all', count: normalizedRows.value.length }, ...states];
});

function asString(value: unknown, fallback = ''): string {
  if (typeof value === 'string' && value.trim().length) return value.trim();
  if (typeof value === 'number') return String(value);
  return fallback;
}

const normalizedRows = computed<ErrorDetail[]>(() => {
  return rawRows.value.map((row, index) => {
    const hospital = asString(row.hospital, defaultHospital);
    const institutionId = asString(row.institutionId, '-');
    const emr = asString(row.emr, '-');
    const patient = asString(row.patient, '-');
    const birthDate = asString(row.birthDate, '-');
    const category = deriveCategory(row);
    const details = asString(row.details, '-');
    const visitDateObject = parseVisitDate(details);
    const visitDate = formatDate(visitDateObject);
    const uuid = extractUuid(details);
    const severity = computeSeverity(category);
    const ageDays = computeAgeDays(visitDateObject);
    const uniqueKey = `${hospital}|${institutionId}|${emr}|${patient}|${birthDate}|${visitDate}|${category}`;
    const state = persistedStates.value[uniqueKey] || '요청예정';

    return {
      ...row,
      no: index + 1,
      key: uniqueKey,
      hospital,
      institutionId,
      emr,
      patient,
      birthDate,
      category,
      details,
      visitDate,
      uuid,
      severity,
      ageDays,
      state,
      dateObject: visitDateObject,
    };
  });
});

const filteredRows = computed(() => {
  return normalizedRows.value.filter((row) => {
    const matchesHospital = selectedHospital.value === 'all' || row.hospital === selectedHospital.value;
    const matchesEmr = selectedEmr.value === 'all' || row.emr === selectedEmr.value;
    const matchesState = selectedState.value === 'all' || row.state === selectedState.value;
    return matchesHospital && matchesEmr && matchesState;
  });
});

const categoryOptions = computed(() => {
  const counts = filteredRows.value.reduce<Record<string, number>>((acc, row) => {
    acc[row.category] = (acc[row.category] || 0) + 1;
    return acc;
  }, {});

  const categories = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([category, count]) => ({ label: category, value: category, count }));

  const allCount = filteredRows.value.length;
  return [{ label: '전체', value: 'all', count: allCount }, ...categories];
});

const visibleRows = computed(() => {
  if (selectedCategory.value === 'all') {
    return filteredRows.value;
  }
  return filteredRows.value.filter((row) => row.category === selectedCategory.value);
});

const totalIssues = computed(() => filteredRows.value.length);
const pendingRequests = computed(() => filteredRows.value.filter((row) => row.state === '확인요청').length);
const revisionRequests = computed(() => filteredRows.value.filter((row) => row.state === '수정요청함').length);
const completedCount = computed(() => filteredRows.value.filter((row) => row.state === '완료').length);
const failureCount = computed(() => filteredRows.value.length);
const errorRate = computed(() => (filteredRows.value.length ? Math.round(((pendingRequests.value + revisionRequests.value + completedCount.value) / filteredRows.value.length) * 100) : 0));
const criticalCount = computed(() => filteredRows.value.filter((row) => row.severity === 'High').length);

const hospitalCounts = computed(() => {
  return filteredRows.value.reduce<Record<string, number>>((acc, row) => {
    acc[row.hospital] = (acc[row.hospital] || 0) + 1;
    return acc;
  }, {});
});

const barChartSeries = computed(() => [{ name: '오류 건수', data: Object.values(hospitalCounts.value) }]);

const barChartOptions = computed(() => ({
  chart: { toolbar: { show: false } },
  plotOptions: { bar: { borderRadius: 8, columnWidth: '55%' } },
  xaxis: { categories: Object.keys(hospitalCounts.value) },
  dataLabels: { enabled: false },
  tooltip: { y: { formatter: (value: number) => `${value}건` } },
  colors: ['#2563eb'],
  legend: { show: false },
}));

const categoryCounts = computed(() => {
  return filteredRows.value.reduce<Record<string, number>>((acc, row) => {
    acc[row.category] = (acc[row.category] || 0) + 1;
    return acc;
  }, {});
});

const donutSeries = computed(() => Object.values(categoryCounts.value));

const donutChartOptions = computed(() => ({
  labels: Object.keys(categoryCounts.value),
  legend: { position: 'bottom' },
  dataLabels: { enabled: true },
  plotOptions: { pie: { donut: { labels: { show: true } } } },
  colors: ['#2563eb', '#f59e0b', '#ef4444', '#10b981', '#8b5cf6'],
  tooltip: { y: { formatter: (value: number) => `${value}건` } },
}));

const stateCounts = computed(() => {
  return filteredRows.value.reduce<Record<string, number>>((acc, row) => {
    acc[row.state] = (acc[row.state] || 0) + 1;
    return acc;
  }, {});
});

const stateSummary = computed(() => {
  const counts = stateCounts.value;
  return [
    { label: '요청예정', count: counts['요청예정'] || 0 },
    { label: '확인요청', count: counts['확인요청'] || 0 },
    { label: '수정요청함', count: counts['수정요청함'] || 0 },
    { label: '완료', count: counts['완료'] || 0 },
  ];
});

const reportDate = computed(() => {
  if (!filteredRows.value.length) {
    return formatDate(new Date());
  }
  const latest = filteredRows.value
    .map((row) => row.dateObject)
    .sort((a, b) => b.getTime() - a.getTime())[0];
  return formatDate(latest);
});

const reportJson = computed<ReportPayload>(() => {
  const grouped = filteredRows.value.reduce<Record<string, ReportError>>((acc, row) => {
    if (!acc[row.category]) {
      acc[row.category] = { category: row.category, count: 0, details: [] };
    }
    acc[row.category].count += 1;
    acc[row.category].details.push({
      no: row.no,
      visitDate: row.visitDate,
      uuid: row.uuid,
      state: row.state,
      severity: row.severity,
    });
    return acc;
  }, {});

  return {
    hospital: selectedHospital.value === 'all' ? defaultHospital : selectedHospital.value,
    reportDate: reportDate.value,
    errors: Object.values(grouped),
  };
});

const jsonPreview = computed(() => JSON.stringify(reportJson.value, null, 2));

watch(selectedPeriod, () => {
  loadExcelData();
});

watch(categoryOptions, (options) => {
  if (!options.length) {
    selectedCategory.value = 'all';
    return;
  }
  if (!options.some((option) => option.value === selectedCategory.value)) {
    selectedCategory.value = 'all';
  }
});

function normalizeHeaderValue(value: unknown): string {
  if (typeof value !== 'string') return '';
  const normalized = value.trim().toLowerCase();
  const map: Record<string, string> = {
    timestamp: 'timestamp',
    time: 'timestamp',
    date: 'timestamp',
    endpoint: 'endpoint',
    api: 'endpoint',
    status: 'status',
    errorcode: 'errorCode',
    'error code': 'errorCode',
    retry: 'retry',
    category: 'category',
    hospital: 'hospital',
    patient: 'patient',
    no: 'no',
    '기관번호': 'institutionId',
    '병원명': 'hospital',
    'emr사': 'emr',
    '피보험자': 'patient',
    '생년월일': 'birthDate',
    '청구실패사유': 'category',
    '청구실패 사유': 'category',
    '진료내역': 'details',
    '진료 내역 (진료일자 및 uuid)': 'details',
  };

  if (map[normalized]) {
    return map[normalized];
  }

  if (normalized.includes('진료') && normalized.includes('uuid')) {
    return 'details';
  }
  if (normalized.includes('청구실패') && normalized.includes('사유')) {
    return 'category';
  }
  return normalized;
}

function normalizeSectionCategory(value: string): string {
  const text = value.trim();
  const match = text.match(/청구실패\s*사유\s*[:：]?\s*(.*)$/i);
  if (match && match[1]) return match[1].trim();
  const cleaned = text.replace(/^\?+\s*/g, '').trim();
  return cleaned || '미분류';
}

function isHeaderRow(row: unknown[]): boolean {
  const normalized = row.map((cell) => (typeof cell === 'string' ? cell.trim().toLowerCase() : ''));
  const known = [
    'no', 'timestamp', 'time', 'date', 'endpoint', 'api', 'status', 'errorcode', 'error code', 'retry', 'category', 'hospital', 'patient',
    '기관번호', '병원명', 'emr사', '피보험자', '생년월일', '청구실패사유', '청구실패 사유', '진료내역',
  ];
  const score = normalized.filter((value) => known.includes(value)).length;
  return score >= 2;
}

function buildRowObject(headers: string[], row: unknown[]): RawRow {
  return headers.reduce<RawRow>((acc, header, index) => {
    const value = row[index];
    acc[header] = value === undefined || value === null ? '' : String(value).trim();
    return acc;
  }, {});
}

function parseSheetRows(rows: unknown[][], sheetName: string): RawRow[] {
  const parsed: RawRow[] = [];
  let headers: string[] = [];
  let currentCategory = '';

  rows.forEach((row) => {
    if (!Array.isArray(row)) return;
    if (row.every((cell) => cell === undefined || cell === null || cell === '')) return;

    const firstCell = typeof row[0] === 'string' ? row[0].trim() : '';
    if (/청구실패\s*사유/i.test(firstCell)) {
      currentCategory = normalizeSectionCategory(firstCell);
      headers = [];
      return;
    }

    if (isHeaderRow(row)) {
      headers = row.map(normalizeHeaderValue).filter((key) => key.length > 0);
      return;
    }

    if (!headers.length) return;

    const rowObject = buildRowObject(headers, row);
    if (currentCategory) {
      rowObject.category = currentCategory;
    }
    if (!rowObject.hospital) {
      rowObject.hospital = sheetName.trim() || defaultHospital;
    }
    parsed.push(rowObject);
  });

  return parsed;
}

function parseVisitDate(detail: string): Date {
  const match = detail.match(/일자\s*[:：]?\s*([0-9]{4}[-./][0-9]{2}[-./][0-9]{2})/);
  if (match) {
    return new Date(match[1].replace(/\./g, '-'));
  }
  return new Date();
}

function extractUuid(detail: string): string {
  const match = detail.match(/UUID\s*[:：]?\s*([A-Za-z0-9-]+)/i);
  return match ? match[1] : '';
}

function computeAgeDays(date: Date): number {
  const diff = Date.now() - date.getTime();
  return Math.max(0, Math.floor(diff / (1000 * 60 * 60 * 24)));
}

function deriveCategory(row: RawRow): string {
  const category = asString(row.category);
  if (category) return category;

  const details = asString(row.details);
  if (/필수값|서식|승인번호|금액/.test(details)) {
    return details;
  }

  return '미분류';
}

function computeSeverity(category: string): string {
  if (/서식|승인번호|금액|필수값/.test(category)) return 'High';
  return 'Normal';
}

function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function loadPersistedStates() {
  const raw = window.localStorage.getItem(storageKey);
  if (!raw) return {};
  try {
    return JSON.parse(raw) as Record<string, RowState>;
  } catch {
    return {};
  }
}

function savePersistedStates() {
  window.localStorage.setItem(storageKey, JSON.stringify(persistedStates.value));
}

function getNextState(state: RowState): RowState {
  if (state === '요청예정') return '확인요청';
  if (state === '확인요청') return '수정요청함';
  if (state === '수정요청함') return '완료';
  return '완료';
}

function toggleRowState(row: ErrorDetail) {
  const next = getNextState(row.state);
  persistedStates.value = { ...persistedStates.value, [row.key]: next };
  savePersistedStates();
}

function rowHighlightClass(row: ErrorDetail) {
  if (row.ageDays > 7) return 'row-urgent';
  if (row.ageDays > 3) return 'row-warning';
  return 'row-normal';
}

function statusPillClass(state: RowState) {
  if (state === '요청예정') return 'status-pill status-pending';
  if (state === '확인요청') return 'status-pill status-request';
  if (state === '수정요청함') return 'status-pill status-revision';
  return 'status-pill status-complete';
}

function rowButtonClass(state: RowState) {
  if (state === '확인요청') return 'status-request-button';
  if (state === '수정요청함') return 'status-revision-button';
  if (state === '완료') return 'status-complete-button';
  return '';
}

async function loadExcelData() {
  try {
    const fileKeys = ['20260501~20260622', '20260623~20260629'];
    const selectedKeys = selectedPeriod.value === 'all' ? fileKeys : [selectedPeriod.value];
    const rows: RawRow[] = [];

    for (const fileKey of selectedKeys) {
      const url = `/files/${fileKey}.xlsx`;
      const response = await fetch(url);
      if (!response.ok) {
        console.warn(`Excel 파일을 불러올 수 없습니다: ${url}`);
        continue;
      }
      const arrayBuffer = await response.arrayBuffer();
      const workbook = XLSX.read(arrayBuffer, { type: 'array' });

      workbook.SheetNames.forEach((sheetName) => {
        const sheet = workbook.Sheets[sheetName];
        if (!sheet) return;
        const sheetRows = XLSX.utils.sheet_to_json(sheet, { header: 1, raw: false }) as unknown[][];
        const parsedRows = parseSheetRows(sheetRows, sheetName);
        parsedRows.forEach((row) => {
          if (!row.hospital) row.hospital = sheetName.trim() || defaultHospital;
          rows.push(row);
        });
      });
    }

    rawRows.value = rows;
    persistedStates.value = loadPersistedStates();
    if (!categoryOptions.value.some((option) => option.value === selectedCategory.value)) {
      selectedCategory.value = 'all';
    }
  } catch (error) {
    console.error('Excel 로드 실패:', error);
    rawRows.value = [];
  }
}

onMounted(() => {
  persistedStates.value = loadPersistedStates();
  loadExcelData();
});
</script>

<style scoped>
.error-dashboard {
  padding: 24px 0;
}

.section-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 30px;
}

.breadcrumb {
  margin: 0;
  color: #6e7681;
  font-size: 12px;
}

.section-header h2 {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
}

.section-subtitle {
  margin: 6px 0 0;
  color: #52606d;
  font-size: 14px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}

.filter-input {
  min-width: 180px;
  max-width: 260px;
}

.status-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}

.status-card {
  padding: 18px;
  text-align: center;
}

.status-card h5 {
  margin: 0 0 8px;
  font-size: 14px;
  color: #374151;
}

.status-card p {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
}
/* 
  display: flex;
  justify-content: space-between;
  align-items: center;
} */

.card h4 {
  margin: 0 0 8px;
  font-size: 14px;
}

.card-value {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
}

.growth-positive {
  color: #22c55e;
  font-size: 12px;
  margin-left: 8px;
}

.neumorphic-card {
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.06);
  padding: 22px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  height: 100%;
}

.card-icon {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, #2563eb 0%, #22c55e 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.chart-card {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.chart-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}

.chart-header p {
  margin: 0;
  color: #6e7681;
  font-size: 13px;
}

.details-panel {
  margin-top: 30px;
}

.detail-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 18px;
}

.detail-tab {
  border-radius: 999px;
  padding: 10px 18px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #334155;
  font-weight: 600;
  cursor: pointer;
}

.detail-tab.active {
  background: #2563eb;
  border-color: #2563eb;
  color: #ffffff;
}

.table-responsive-wrapper {
  overflow-x: auto;
  width: 100%;
}

.project-table {
  width: 100%;
}

.project-table h4 {
  margin: 0 0 16px;
  font-size: 16px;
}

.project-table table {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
}

.project-table th,
.project-table td {
  padding: 14px 12px;
  border-bottom: 1px solid #eef2f7;
  text-align: left;
  font-size: 13px;
}

.project-table th {
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.empty-row {
  text-align: center;
  color: #6e7681;
  padding: 24px 0;
}

.row-urgent {
  background: rgba(249, 115, 22, 0.08);
}

.row-warning {
  background: rgba(234, 179, 8, 0.1);
}

.row-normal {
  background: transparent;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.status-waiting {
  background: #f3f4f6;
  color: #334155;
}

.status-request {
  background: #fef3c7;
  color: #92400e;
}

.status-complete {
  background: #d1fae5;
  color: #047857;
}

.action-button {
  border: none;
  border-radius: 10px;
  padding: 10px 16px;
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s ease, opacity 0.15s ease;
  background: #2563eb;
}

.status-request-button {
  background: #f59e0b;
}

.status-complete-button {
  background: #10b981;
}

.action-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.action-button[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}

.json-card {
  margin-top: 24px;
}

.json-card pre {
  margin: 0;
  background: #f8fafc;
  padding: 18px;
  border-radius: 16px;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  max-height: 340px;
  overflow: auto;
}

@media (max-width: 960px) {
  .section-header,
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .project-table table {
    min-width: 620px;
  }
}

@media (max-width: 640px) {
  .action-button {
    width: 100%;
  }
}
</style>
 