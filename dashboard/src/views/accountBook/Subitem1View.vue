<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h5 mb-4">월별 지출 관리</h1>
      </v-col>
    </v-row>

    <!-- KPI Section -->
    <v-row v-if="displaySections.includes('kpi')">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-3 text-center" outlined>
          <div class="text-subtitle-2 text-grey">선택 월 총지출</div>
          <div class="text-h5 font-weight-bold">{{ formatCurrency(currentMonthTotalSpending) }}</div>
          <div :class="momChangeColor" class="text-caption">
            {{ momChangeText }}
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-3 text-center" outlined>
          <div class="text-subtitle-2 text-grey">일평균 지출</div>
          <div class="text-h5 font-weight-bold text-blue-darken-1">{{ formatCurrency(dailyAverageSpending) }}</div>
          <div class="text-caption text-grey">(해당 월 기준)</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-3 text-center" outlined>
          <div class="text-subtitle-2 text-grey">전체 월평균</div>
          <div class="text-h5 font-weight-bold text-green-darken-1">{{ formatCurrency(overallMonthlyAverage) }}</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-3 text-center" outlined>
          <div class="text-subtitle-2 text-grey">최대 지출 월</div>
          <div class="text-h5 font-weight-bold text-orange-darken-1">{{ maxSpendingMonth }}</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Month Selector -->
    <v-row class="mt-4">
      <v-col cols="12" md="4">
        <v-select
          v-model="selectedMonth"
          :items="availableMonths"
          label="조회 월 선택"
          outlined
          dense
        ></v-select>
      </v-col>
    </v-row>

    <!-- Chart Section -->
    <v-row v-if="displaySections.includes('chart')">
      <v-col cols="12">
        <v-card outlined class="pa-4">
          <v-card-title>월별 지출 추이</v-card-title>
          <apexchart type="line" height="350" :options="chartOptions" :series="chartSeries"></apexchart>
        </v-card>
      </v-col>
    </v-row>

    <!-- Category Analysis & Top Merchants Section -->
    <v-row class="mt-4">
      <v-col cols="12" md="6" v-if="displaySections.includes('category_analysis')">
        <v-card outlined class="pa-4">
          <v-card-title>전월 대비 카테고리별 증감</v-card-title>
          <v-data-table
            :headers="categoryAnalysisHeaders"
            :items="categoryAnalysisData"
            hide-default-footer
            disable-pagination
            class="elevation-1"
          >
            <template v-slot:item.diff="{ item }">
              <span :class="getDiffColor(item.diff)">{{ item.diff }}</span>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" v-if="displaySections.includes('top_merchants')">
        <v-card outlined class="pa-4">
          <v-card-title>선택 월 주요 소비처 Top 5</v-card-title>
          <v-data-table
            :headers="topMerchantsHeaders"
            :items="topMerchantsData"
            hide-default-footer
            disable-pagination
            class="elevation-1"
          ></v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- AI Advice Section -->
    <v-row v-if="displaySections.includes('ai_advice')">
      <v-col cols="12">
        <v-card outlined class="pa-4">
          <v-card-title>AI 소비 진단</v-card-title>
          <v-card-subtitle>상태: {{ aiStatus }}</v-card-subtitle>
          <v-card-text>{{ aiAdvice }}</v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import VueApexCharts from 'vue3-apexcharts'; // ApexCharts 임포트

interface Transaction {
  transaction_date: string;
  amount: number;
  description: string;
  transaction_type: string;
  payment_method: string;
  category?: string; // Added for processed data
  sub_category?: string; // Added for processed data
}

interface CategoryRule {
  id: number;
  merchant: string;
  category: string;
  sub_category: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/python';

const allTransactions = ref<Transaction[]>([]);
const categoryRules = ref<CategoryRule[]>([]);
const filteredTransactions = ref<Transaction[]>([]); // Transactions filtered by type '지출' and processed
const availableMonths = ref<string[]>([]);
const selectedMonth = ref<string | null>(null);
const monthlySummary = ref<{ month: string; amount: number }[]>([]);

// KPI Data
const currentMonthTotalSpending = ref<number>(0);
const momChangeText = ref<string>('-');
const momChangeColor = ref<string>('text-grey');
const dailyAverageSpending = ref<number>(0);
const overallMonthlyAverage = ref<number>(0);
const maxSpendingMonth = ref<string>('-');

// Chart Data (ApexCharts specific)
const chartSeries = ref([{
  name: '월별 지출',
  data: [] as { x: string; y: number }[],
}]);
const chartOptions = ref({
  chart: {
    height: 350,
    type: 'line',
    toolbar: {
      show: false,
    },
    events: {
      markerClick: (event: any, chartContext: any, { dataPointIndex }: { dataPointIndex: number }) => {
        if (monthlySummary.value[dataPointIndex]) {
          selectedMonth.value = monthlySummary.value[dataPointIndex].month;
        }
      },
    },
  },
  stroke: {
    curve: 'smooth',
    width: 2,
  },
  markers: {
    size: 5,
    hover: {
      size: 7,
    },
  },
  xaxis: {
    type: 'category',
    categories: [] as string[],
    title: {
      text: '월',
    },
    labels: {
      rotate: -45,
    },
  },
  yaxis: {
    title: {
      text: '지출 금액',
    },
    labels: {
      formatter: (value: number) => formatCurrency(value),
    },
  },
  tooltip: {
    y: {
      formatter: (value: number) => formatCurrency(value),
    },
  },
  grid: {
    row: {
      colors: ['#f3f3f3', 'transparent'],
      opacity: 0.5,
    },
  },
  annotations: {
    points: [] as any[],
  },
});

// Category Analysis Data
const categoryAnalysisHeaders = [
  { title: '카테고리', value: 'category', align: 'start' },
  { title: '지난달', value: 'prevMonthAmount', align: 'end' },
  { title: '선택달', value: 'currentMonthAmount', align: 'end' },
  { title: '증감', value: 'diff', align: 'end' },
];
const categoryAnalysisData = ref<any[]>([]);

// Top Merchants Data
const topMerchantsHeaders = [
  { title: '카테고리', value: 'category', align: 'start' },
  { title: '소비처', value: 'merchant', align: 'start' },
  { title: '금액', value: 'amount', align: 'end' },
];
const topMerchantsData = ref<any[]>([]);

// AI Advice Data
const aiStatus = ref<string>('대기 중');
const aiAdvice = ref<string>('AI 조언을 생성하려면 월을 선택해주세요.');

// Display sections (can be passed as props if this component is reused)
const displaySections = ref<string[]>(['kpi', 'chart', 'category_analysis', 'top_merchants', 'ai_advice']);

// --- Helper Functions ---

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' }).format(value);
};

const getDiffColor = (diff: string): string => {
  if (diff.startsWith('+')) return 'text-red-darken-1';
  if (diff.startsWith('-')) return 'text-blue-darken-1';
  return 'text-grey';
};

// Auto-classify logic (re-implemented from Python's TransactionUtil)
const autoClassify = (description: string, originalType: string, rules: CategoryRule[]) => {
  const content = description.toLowerCase().trim();
  let category = '미분류';
  let subCategory = '미분류';
  let type = originalType;

  const financialKws = ['카드대금', '결제대금', '보험', '이자', '적금', '송금', '이체', '대출', '상환', '현금서비스'];
  if (financialKws.some(kw => content.includes(kw))) {
    return { category: '금융/이체', subCategory: '자동분류', type: '이체' };
  }

  for (const rule of rules) {
    const kw = rule.merchant ? String(rule.merchant).toLowerCase().trim() : '';
    if (kw && content.includes(kw)) {
      category = rule.category ? String(rule.category).trim() : '미분류';
      subCategory = rule.sub_category ? String(rule.sub_category).trim() : '미분류';
      if (['이체', '자산이동', '금융/이체'].includes(category)) {
        type = '이체';
      }
      return { category, subCategory, type };
    }
  }
  return { category, subCategory, type };
};

// --- Data Loading & Processing ---

const loadData = async () => {
  try {
    // Fetch category rules
    const categoriesResponse = await axios.get(`${API_BASE_URL}/categories`);
    categoryRules.value = categoriesResponse.data;

    // Fetch transactions
    const transactionsResponse = await axios.get(`${API_BASE_URL}/transactions`);
    const rawTransactions: Transaction[] = transactionsResponse.data;

    // Process transactions (similar to Python's process_transactions_dataframe)
    const processed = rawTransactions.map(t => {
      const classified = autoClassify(t.description, t.transaction_type, categoryRules.value);
      const transactionDate = new Date(t.transaction_date);
      return {
        ...t,
        DT: transactionDate, // Add DT for date operations
        month: `${transactionDate.getFullYear()}-${(transactionDate.getMonth() + 1).toString().padStart(2, '0')}`,
        category: classified.category,
        sub_category: classified.subCategory,
        transaction_type: classified.type, // Update type if classified as '이체'
        amount: Math.abs(t.amount), // Use absolute amount for spending analysis
      };
    }).filter(t => t.transaction_type === '지출'); // Only '지출' for spending management

    filteredTransactions.value = processed;

    // Calculate monthly summary
    const summaryMap = new Map<string, number>();
    processed.forEach(t => {
      if (t.transaction_type === '지출') {
        summaryMap.set(t.month, (summaryMap.get(t.month) || 0) + t.amount);
      }
    });
    monthlySummary.value = Array.from(summaryMap.entries())
      .map(([month, amount]) => ({ month, amount }))
      .sort((a, b) => a.month.localeCompare(b.month));

    availableMonths.value = monthlySummary.value.map(s => s.month).reverse(); // Newest first
    if (availableMonths.value.length > 0) {
      selectedMonth.value = availableMonths.value[0]; // Select the latest month
    }

  } catch (error) {
    console.error('Error loading data:', error);
    // Optionally show an alert to the user
  }
};

// --- Analysis & UI Updates ---

const updateAnalysis = () => {
  if (!selectedMonth.value || filteredTransactions.value.length === 0) {
    resetKpiData();
    updateChart([]);
    categoryAnalysisData.value = [];
    topMerchantsData.value = [];
    aiAdvice.value = '데이터가 없어 AI 조언을 생성할 수 없습니다.';
    aiStatus.value = '데이터 없음';
    return;
  }

  const currentMonthData = filteredTransactions.value.filter(t => t.month === selectedMonth.value);
  const currentMonthTotal = currentMonthData.reduce((sum, t) => sum + t.amount, 0);
  currentMonthTotalSpending.value = currentMonthTotal;

  // Calculate MoM Change
  const currentMonthIndex = monthlySummary.value.findIndex(s => s.month === selectedMonth.value);
  if (currentMonthIndex > 0) {
    const prevMonthTotal = monthlySummary.value[currentMonthIndex - 1].amount;
    const diff = currentMonthTotal - prevMonthTotal;
    const pct = prevMonthTotal !== 0 ? (diff / prevMonthTotal) * 100 : 0;
    momChangeText.value = `전월대비 ${diff > 0 ? '+' : ''}${formatCurrency(diff)} (${diff > 0 ? '+' : ''}${pct.toFixed(1)}%)`;
    momChangeColor.value = diff > 0 ? 'text-red-darken-1' : 'text-blue-darken-1';
  } else {
    momChangeText.value = '전월 데이터 없음';
    momChangeColor.value = 'text-grey';
  }

  // Calculate Daily Average Spending
  const [year, month] = selectedMonth.value.split('-').map(Number);
  const daysInMonth = new Date(year, month, 0).getDate(); // Get days in selected month
  dailyAverageSpending.value = daysInMonth > 0 ? currentMonthTotal / daysInMonth : 0;

  // Calculate Overall Monthly Average
  overallMonthlyAverage.value = monthlySummary.value.reduce((sum, s) => sum + s.amount, 0) / monthlySummary.value.length;

  // Calculate Max Spending Month
  if (monthlySummary.value.length > 0) {
    const maxMonth = monthlySummary.value.reduce((max, s) => (s.amount > max.amount ? s : max), monthlySummary.value[0]);
    maxSpendingMonth.value = maxMonth.month;
  }

  // Update Chart
  updateChart(monthlySummary.value);

  // Update Category Analysis
  updateCategoryAnalysisData(selectedMonth.value);

  // Update Top Merchants
  updateTopMerchantsData(selectedMonth.value);

  // Get AI Advice
  getAiSpendingAdvice(selectedMonth.value);
};

const resetKpiData = () => {
  currentMonthTotalSpending.value = 0;
  momChangeText.value = '-';
  momChangeColor.value = 'text-grey';
  dailyAverageSpending.value = 0;
  overallMonthlyAverage.value = 0;
  maxSpendingMonth.value = '-';
};

const updateChart = (summary: { month: string; amount: number }[]) => {
  const chartData = summary.map(s => ({ x: s.month, y: s.amount }));
  const categories = summary.map(s => s.month);

  chartSeries.value = [{
    name: '월별 지출',
    data: chartData,
  }];

  const currentMonthIndex = categories.findIndex(month => month === selectedMonth.value);
  const annotations = [];

  if (currentMonthIndex !== -1) {
    annotations.push({
      points: [{
        x: categories[currentMonthIndex],
        y: chartData[currentMonthIndex].y,
        marker: {
          size: 8,
          fillColor: '#ffd700',
          strokeColor: '#fbc02d',
          strokeWidth: 2,
        },
        label: {
          borderColor: '#fbc02d',
          style: {
            color: '#fff',
            background: '#fbc02d',
          },
          text: formatCurrency(chartData[currentMonthIndex].y),
        },
      }],
    });
  }

  chartOptions.value = {
    ...chartOptions.value,
    xaxis: {
      ...chartOptions.value.xaxis,
      categories: categories,
    },
    annotations: {
      points: annotations.flatMap(a => a.points), // Flatten points from all annotations
    },
  };
};

const updateCategoryAnalysisData = (month: string) => {
  const currentMonthData = filteredTransactions.value.filter(t => t.month === month);
  const currentMonthCategorySpending = currentMonthData.reduce((acc, t) => {
    acc[t.category || '미분류'] = (acc[t.category || '미분류'] || 0) + t.amount;
    return acc;
  }, {} as Record<string, number>);

  const currentMonthIndex = monthlySummary.value.findIndex(s => s.month === month);
  let prevMonthCategorySpending: Record<string, number> = {};

  if (currentMonthIndex > 0) {
    const prevMonth = monthlySummary.value[currentMonthIndex - 1].month;
    const prevMonthData = filteredTransactions.value.filter(t => t.month === prevMonth);
    prevMonthCategorySpending = prevMonthData.reduce((acc, t) => {
      acc[t.category || '미분류'] = (acc[t.category || '미분류'] || 0) + t.amount;
      return acc;
    }, {} as Record<string, number>);
  }

  const analysis: any[] = [];
  const allCategories = new Set([...Object.keys(currentMonthCategorySpending), ...Object.keys(prevMonthCategorySpending)]);

  allCategories.forEach(cat => {
    const currentAmount = currentMonthCategorySpending[cat] || 0;
    const prevAmount = prevMonthCategorySpending[cat] || 0;
    const diff = currentAmount - prevAmount;

    analysis.push({
      category: cat,
      prevMonthAmount: formatCurrency(prevAmount),
      currentMonthAmount: formatCurrency(currentAmount),
      diff: `${diff > 0 ? '+' : ''}${formatCurrency(diff)}`,
    });
  });

  categoryAnalysisData.value = analysis.sort((a, b) => b.currentMonthAmount.localeCompare(a.currentMonthAmount));
};

const updateTopMerchantsData = (month: string) => {
  const currentMonthData = filteredTransactions.value.filter(t => t.month === month);
  const merchantSpendingMap = currentMonthData.reduce((acc, t) => {
    const key = `${t.category || '미분류'}-${t.description}`;
    acc[key] = (acc[key] || { category: t.category || '미분류', merchant: t.description, amount: 0 });
    acc[key].amount += t.amount;
    return acc;
  }, {} as Record<string, { category: string; merchant: string; amount: number }>);

  topMerchantsData.value = Object.values(merchantSpendingMap)
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 5)
    .map(item => ({
      category: item.category,
      merchant: item.merchant,
      amount: formatCurrency(item.amount),
    }));
};

const getAiSpendingAdvice = async (month: string) => {
  aiStatus.value = '분석 중...';
  aiAdvice.value = `'${month}' 조언 생성 중...`;

  // This part would ideally call a backend API endpoint that then calls Gemini API
  // For now, it's a placeholder.
  try {
    // Example: await axios.post(`${API_BASE_URL}/ai-advice`, { month });
    // And then update aiAdvice.value with the response.
    aiAdvice.value = `AI 조언 기능은 백엔드 연동이 필요합니다. (현재 월: ${month})`;
    aiStatus.value = '백엔드 연동 필요';
  } catch (error) {
    console.error('Error fetching AI advice:', error);
    aiAdvice.value = 'AI 조언을 가져오는 데 실패했습니다.';
    aiStatus.value = '분석 실패';
  }
};

// --- Lifecycle Hooks & Watchers ---

onMounted(() => {
  loadData();
});

watch(selectedMonth, () => {
  updateAnalysis();
});

// Optional: Watch filteredTransactions if it can change independently
// watch(filteredTransactions, () => {
//   updateAnalysis();
// }, { deep: true });
</script>

<style scoped>
/* Add any specific styles for this component */
.v-card {
  border-radius: 8px;
}
.text-red-darken-1 {
  color: #ef5350; /* Material Design Red */
}
.text-blue-darken-1 {
  color: #42a5f5; /* Material Design Blue */
}
.text-green-darken-1 {
  color: #66bb6a; /* Material Design Green */
}
.text-orange-darken-1 {
  color: #ffa726; /* Material Design Orange */
}
</style>
