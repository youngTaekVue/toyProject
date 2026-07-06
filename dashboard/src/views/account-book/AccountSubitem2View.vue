<template>
  <v-container fluid class="dashboard-section pt-0">
    <!-- KPI 요약 정보 카드 (한눈에 자산 현황을 보기 위한 상단 배치) -->
    <v-row class="summary-cards mb-6">
      <v-col cols="12" sm="6" md="3" v-for="n in 4" :key="`kpi-card-${n}`">
        <v-card class="neumorphic-card pa-4 text-center" v-if="loading">
          <v-skeleton-loader type="card" class="mx-auto" height="100px"></v-skeleton-loader>
        </v-card>
        <v-card class="neumorphic-card pa-4 text-center" v-else>
          <div class="text-subtitle-2 text-grey-darken-1 mb-1">
            {{
              n === 1
                ? '현재 총자산'
                : n === 2
                ? '현재 총부채'
                : n === 3
                ? '실질 순자산'
                : '전월비 순자산 변동'
            }}
          </div>
          <div
            class="text-h5 font-weight-bold"
            :class="{
              'text-kpiGreen': n === 1,
              'text-kpiRed': n === 2,
              'text-kpiBlue': n === 3,
              'text-default': n === 4,
            }"
          >
            {{
              n === 1
                ? formatCurrency(kpiTotalAssets)
                : n === 2
                ? formatCurrency(kpiTotalLiabilities)
                : n === 3
                ? formatCurrency(kpiNetAssets)
                : (kpiNetAssetsDiff > 0 ? '+' : '') + formatCurrency(kpiNetAssetsDiff)
            }}
          </div>
          <div class="text-caption text-grey mt-1">
            {{
              n === 1
                ? '보유 자산 합계'
                : n === 2
                ? '상환할 부채 합계'
                : n === 3
                ? '자산 - 부채'
                : kpiNetAssetsDiff >= 0 ? '자산 증가액' : '자산 감소액'
            }}
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 종합 비교 상세 내역 테이블 (클릭하여 히스토리 조회 가능) -->
    <v-row>
      <v-col cols="12">
        <v-card class="neumorphic-card pa-4" v-if="loading">
          <v-skeleton-loader type="table-heading, list-item-two-line, list-item-two-line, list-item-two-line" class="mx-auto"></v-skeleton-loader>
        </v-card>
        <v-card class="neumorphic-card pa-4" v-else>
          <div class="d-flex align-center justify-space-between mb-2">
            <v-card-title class="text-h6 font-weight-bold pa-0">전체 자산 및 부채 상세 명세</v-card-title>
            <span class="text-caption text-grey-darken-1">
              💡 표의 행을 클릭하면 과거 월별 자산 변동 히스토리를 볼 수 있습니다.
            </span>
          </div>
          <p class="text-caption text-grey-darken-1 mb-4">
            가장 최근 스냅샷과 이전 스냅샷 간의 개별 계좌/부채 증감액(Delta)을 대조합니다.
          </p>
          <div v-if="compareItems.length === 0" class="text-center py-10 text-slate-400">
            표시할 자산 및 부채 내역이 없습니다.
          </div>
          <v-data-table
            v-else
            :headers="compareHeaders"
            :items="compareItems"
            class="neumorphic-table clickable-table"
            hide-default-footer
            disable-pagination
            @click:row="handleRowClick"
          >
            <template v-slot:item.prevAmount="{ item }">
              {{ formatCurrency(item.prevAmount) }}
            </template>
            <template v-slot:item.currAmount="{ item }">
              {{ formatCurrency(item.currAmount) }}
            </template>
            <template v-slot:item.diff="{ item }">
              <span :class="getDiffColor(item.diff)">
                {{ item.diff > 0 ? '+' : '' }}{{ formatCurrency(item.diff) }}
              </span>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- 자산별 상세 히스토리 조회 모달 (UX/UI 프리미엄 보완) -->
    <v-dialog v-model="historyDialog" max-width="600px" transition="dialog-bottom-transition">
      <v-card class="history-dialog-card elevation-24">
        <!-- 모달 헤더 -->
        <v-card-title class="history-dialog-header d-flex justify-space-between align-center">
          <div class="d-flex align-center gap-2">
            <v-icon color="primary" class="mr-2">mdi-history</v-icon>
            <span class="font-weight-bold text-slate-800 text-h6">
              {{ selectedItemName }} <span class="text-caption text-grey-darken-1 font-weight-regular">({{ selectedItemCategory }})</span>
            </span>
          </div>
          <v-btn icon="mdi-close" variant="text" size="small" color="slate-500" @click="historyDialog = false"></v-btn>
        </v-card-title>

        <!-- 모달 바디 -->
        <v-card-text class="history-dialog-body" style="max-height: 500px; overflow-y: auto;">
          <!-- 1. 초간결 추이 차트 (Sparkline 적용) -->
          <div class="history-section mb-6">
            <div class="section-label font-weight-bold mb-3">변동 추이 그래프 (월별)</div>
            <div v-if="modalSeries[0] && modalSeries[0].data.length === 0" class="text-center py-6 text-slate-400">데이터가 없습니다.</div>
            <div v-else class="sparkline-container pa-2 bg-slate-50 rounded-lg">
              <apexchart type="area" height="130" :options="modalOptions" :series="modalSeries"></apexchart>
            </div>
          </div>

          <!-- 2. 과거 이력 테이블 -->
          <div class="history-section">
            <div class="section-label font-weight-bold mb-3">월별 잔액 변동 이력</div>
            <v-data-table
              :headers="modalHeaders"
              :items="modalItems"
              class="neumorphic-table compact-table"
              hide-default-footer
              disable-pagination
            >
              <template v-slot:item.amount="{ item }">
                {{ formatCurrency(item.amount) }}
              </template>
              <template v-slot:item.diff="{ item }">
                <span :class="getDiffColor(item.diff)">
                  {{ item.diff > 0 ? '+' : '' }}{{ formatCurrency(item.diff) }}
                </span>
              </template>
            </v-data-table>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/python';

const loading = ref(true);

// KPI State Variables
const kpiTotalAssets = ref(0);
const kpiTotalLiabilities = ref(0);
const kpiNetAssets = ref(0);
const kpiNetAssetsDiff = ref(0);

// Raw historical snapshot data
const rawHistoryAll = ref<any[]>([]);

// Dialog State for Asset History
const historyDialog = ref(false);
const selectedItemName = ref('');
const selectedItemCategory = ref('');

// Helper for formatting KRW currency
const formatCurrency = (value: number): string => {
  if (value === undefined || value === null || isNaN(value)) return '0원';
  return new Intl.NumberFormat('ko-KR').format(value) + '원';
};

// Color formatter for delta comparison
const getDiffColor = (diff: number): string => {
  if (diff > 0) return 'text-kpiRed font-weight-bold'; // Increase -> Red
  if (diff < 0) return 'text-kpiBlue font-weight-bold'; // Decrease -> Blue
  return 'text-grey';
};

// Helper to determine if category is a liability (debt)
const isDebt = (category: string): boolean => {
  if (!category) return false;
  return category.includes('부채') || category.includes('대출') || category.includes('카드');
};

// ==========================================
// Main Table Configuration
// ==========================================
const compareHeaders = [
  { title: '자산/부채 항목', value: 'itemName', align: 'start' as const },
  { title: '금융기관', value: 'institution', align: 'start' as const },
  { title: '대분류', value: 'category', align: 'center' as const },
  { title: '이전 잔액', value: 'prevAmount', align: 'end' as const },
  { title: '현재 잔액', value: 'currAmount', align: 'end' as const },
  { title: '변동액 (Delta)', value: 'diff', align: 'end' as const }
];
const compareItems = ref<any[]>([]);

// ==========================================
// Modal Chart & Table Configuration (Sparkline Style)
// ==========================================
const modalSeries = ref<any[]>([]);
const modalOptions = ref({
  chart: {
    height: 130,
    type: 'area',
    sparkline: { enabled: true }, // 💡 그리드/축선을 제거해 극도로 간결하게 선 그래프만 표시
    animations: { enabled: false }
  },
  colors: ['#2196f3'],
  stroke: { curve: 'smooth', width: 2.5 },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.35,
      opacityTo: 0.02,
      stops: [50, 100, 100]
    }
  },
  markers: { size: 3, hover: { size: 5 } },
  tooltip: {
    fixed: { enabled: false },
    x: { show: true },
    y: { formatter: (value: number) => formatCurrency(value) },
    marker: { show: false }
  }
});

const modalHeaders = [
  { title: '기준 월', value: 'date', align: 'start' as const }, // 💡 '스냅샷 날짜' ➡️ '기준 월'로 변경
  { title: '잔액', value: 'amount', align: 'end' as const },
  { title: '전월비 변동액', value: 'diff', align: 'end' as const }
];
const modalItems = ref<any[]>([]);

// ==========================================
// Row Click Handler (Show history Dialog)
// ==========================================
const handleRowClick = (event: any, row: any) => {
  const item = row.item;
  if (!item) return;

  selectedItemName.value = item.itemName;
  selectedItemCategory.value = `${item.category}${item.institution ? ' / ' + item.institution : ''}`;

  // Filter history records for this specific item
  const itemHistory = rawHistoryAll.value.filter(
    (h: any) => h.item_name === item.itemName && h.category === item.category
  );

  // 💡 월별 그룹화 (동일 월에 여러 스냅샷이 등록되어 있다면, 가장 최근 snapshot_id 데이터를 대표값으로 채택)
  const monthlyMap = new Map<string, any>();
  itemHistory.forEach((h: any) => {
    const month = h.date.substring(0, 7); // 'YYYY-MM'
    if (!monthlyMap.has(month) || h.snapshot_id > monthlyMap.get(month).snapshot_id) {
      monthlyMap.set(month, h);
    }
  });

  // snapshot_id 오름차순 정렬 (차트 렌더링 방향: 과거 -> 현재)
  const monthlyHistory = Array.from(monthlyMap.values()).sort(
    (a: any, b: any) => a.snapshot_id - b.snapshot_id
  );

  const dates = monthlyHistory.map((h: any) => h.date.substring(0, 7));
  const amounts = monthlyHistory.map((h: any) => Math.abs(h.amount));

  // Determine chart theme color (Green for asset, Red for debt)
  const themeColor = isDebt(item.category) ? '#ef5350' : '#4caf50';

  modalSeries.value = [{ name: '잔액', data: amounts }];
  modalOptions.value = {
    ...modalOptions.value,
    colors: [themeColor],
    xaxis: {
      ...modalOptions.value.xaxis,
      categories: dates
    }
  };

  // Build history table with delta calculations based on aggregated monthly values
  const historyTableItems = [];
  for (let i = 0; i < monthlyHistory.length; i++) {
    const curr = monthlyHistory[i];
    const prev = i > 0 ? monthlyHistory[i - 1] : null;
    let diff = 0;

    if (prev) {
      const prevAmt = Math.abs(prev.amount);
      const currAmt = Math.abs(curr.amount);
      diff = isDebt(item.category) ? -(currAmt - prevAmt) : (currAmt - prevAmt);
    }

    historyTableItems.push({
      date: curr.date.substring(0, 7),
      amount: Math.abs(curr.amount),
      diff: diff
    });
  }

  // Reverse list to show newest first in the table
  modalItems.value = historyTableItems.reverse();
  historyDialog.value = true;
};

// ==========================================
// API Fetch Logic
// ==========================================
const fetchHistoryData = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/financial_status/history`);
    const history = response.data;
    if (history && history.length > 0) {
      const latest = history[history.length - 1];
      kpiTotalAssets.value = latest.total_assets;
      kpiTotalLiabilities.value = latest.total_liabilities;
      kpiNetAssets.value = latest.net_assets;

      if (history.length > 1) {
        const prev = history[history.length - 2];
        kpiNetAssetsDiff.value = latest.net_assets - prev.net_assets;
      } else {
        kpiNetAssetsDiff.value = 0;
      }
    }
  } catch (error) {
    console.error('Error fetching financial history:', error);
  }
};

const fetchHistoryAllData = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/financial_status/history/all`);
    rawHistoryAll.value = response.data;
  } catch (error) {
    console.error('Error fetching all historical records:', error);
  }
};

const fetchCompareData = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/financial_status/compare`);
    const { current, previous } = response.data;

    if (!current || current.length === 0) {
      compareItems.value = [];
      return;
    }

    const prevMap = new Map();
    if (previous && Array.isArray(previous)) {
      previous.forEach(row => {
        const key = `${row.item_name}-${row.institution}-${row.category}`;
        prevMap.set(key, row.amount);
      });
    }

    const merged = [];
    const processedKeys = new Set();

    current.forEach(currRow => {
      const key = `${currRow.item_name}-${currRow.institution}-${currRow.category}`;
      processedKeys.add(key);
      const prevVal = prevMap.get(key) || 0;
      const currVal = currRow.amount;
      const diff = currVal - prevVal;

      merged.push({
        itemName: currRow.item_name,
        institution: currRow.institution,
        category: currRow.category,
        prevAmount: Math.abs(prevVal),
        currAmount: Math.abs(currVal),
        diff: isDebt(currRow.category) ? -diff : diff
      });
    });

    if (previous && Array.isArray(previous)) {
      previous.forEach(prevRow => {
        const key = `${prevRow.item_name}-${prevRow.institution}-${prevRow.category}`;
        if (!processedKeys.has(key)) {
          const prevVal = prevRow.amount;
          const currVal = 0;
          const diff = currVal - prevVal;

          merged.push({
            itemName: prevRow.item_name,
            institution: prevRow.institution,
            category: prevRow.category,
            prevAmount: Math.abs(prevVal),
            currAmount: Math.abs(currVal),
            diff: isDebt(prevRow.category) ? -diff : diff
          });
        }
      });
    }

    // Sort: assets top, liabilities bottom, larger balances first
    compareItems.value = merged.sort((a, b) => {
      const aDebt = isDebt(a.category);
      const bDebt = isDebt(b.category);
      if (aDebt === bDebt) {
        return b.currAmount - a.currAmount;
      }
      return aDebt ? 1 : -1;
    });
  } catch (error) {
    console.error('Error fetching financial comparison:', error);
    compareItems.value = [];
  }
};

const loadAllData = async () => {
  loading.value = true;
  await Promise.all([
    fetchHistoryData(),
    fetchHistoryAllData(),
    fetchCompareData()
  ]);
  loading.value = false;
};

onMounted(() => {
  loadAllData();
});
</script>

<style scoped lang="scss">
@use '../../styles/settings.scss' as *;

.dashboard-section {
  margin-top: 40px;
}

/* Modern Soft Minimal Card */
.neumorphic-card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03), 0 1px 3px rgba(0, 0, 0, 0.02);
  padding: 20px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  height: 100%;
}

/* Table styling matching Soft Minimal style */
.neumorphic-table.v-data-table {
  background-color: transparent !important;
}

.neumorphic-table.v-data-table :deep(table) {
  border-collapse: separate;
  border-spacing: 0 8px;
}

.neumorphic-table.v-data-table :deep(th) {
  background-color: $bg-color !important;
  color: $secondary-text !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  font-size: 0.75rem !important;
  padding: 12px 16px !important;
  border-bottom: none !important;
}

.neumorphic-table.v-data-table :deep(td) {
  background-color: #fff !important;
  color: $primary-text !important;
  padding: 12px 16px !important;
  border-bottom: none !important;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

/* Clickable rows indicator */
.clickable-table :deep(tbody tr) {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.clickable-table :deep(tbody tr:hover td) {
  background-color: #f8fafc !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.03);
}

/* Compact Modal Table Customization */
.compact-table.v-data-table :deep(table) {
  border-spacing: 0 4px;
}
.compact-table.v-data-table :deep(td) {
  padding: 8px 12px !important;
  font-size: 13px !important;
}
.compact-table.v-data-table :deep(th) {
  padding: 8px 12px !important;
  font-size: 11px !important;
}

/* Sparkline Chart Container */
.sparkline-container {
  border: 1px solid rgba(226, 232, 240, 0.8);
}

/* Dialog styles */
.history-dialog-card {
  border-radius: 16px !important;
  background: #ffffff;
  padding: 12px;
}

.history-dialog-header {
  border-bottom: 1px solid #e2e8f0;
  padding: 12px 16px !important;
}

.history-dialog-body {
  padding: 20px 16px !important;
}

.section-label {
  font-size: 14px;
  color: $primary-text;
}

.text-kpiRed {
  color: #ef5350 !important;
}

.text-kpiBlue {
  color: #2196f3 !important;
}

.text-kpiGreen {
  color: #4caf50 !important;
}

.text-default {
  color: $primary-text !important;
}
</style>