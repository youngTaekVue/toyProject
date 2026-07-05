<template>
  <v-card class="table-card chart-card-fixed pa-5" elevation="0">
    <div class="d-flex justify-space-between align-center mb-1 flex-wrap gap-y-2">
      <div>
        <span class="table-card-title block">가장 많이 발생한 에러 유형 TOP 5</span>
        <p class="text-caption text-grey-darken-1 mb-0 mt-0.5">
          실패 사유별 누적 건수 랭킹 (총 {{ formatNumber(totalSum) }} 건)
        </p>
      </div>
      <!-- Metric Toggle Buttons -->
      <div class="custom-tab-group">
        <button 
          class="custom-tab-btn" 
          :class="{ active: chartMetric === 'count' }" 
          @click="chartMetric = 'count'"
        >
          오류 건수
        </button>
        <button 
          class="custom-tab-btn" 
          :class="{ active: chartMetric === 'cases' }" 
          @click="chartMetric = 'cases'"
        >
          청구 건수
        </button>
      </div>
    </div>
    <div class="chart-container-inner" style="padding: 12px 6px 6px 6px;">
      <apexchart type="bar" width="100%" height="260" :options="chartOptions" :series="chartSeries"></apexchart>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import VueApexCharts from 'vue3-apexcharts';

const apexchart = VueApexCharts;

interface ClaimCase {
  key: string;
  hospital: string;
  institutionId: string;
  emr: string;
  category: string;
  patient: string;
  birthDate: string;
  count: number;
  state: string;
  fileKey: string;
  rows: any[];
}

const props = defineProps<{
  claimCases: ClaimCase[];
}>();

const chartMetric = ref<'count' | 'cases'>('count');

const totalSum = computed(() => {
  return props.claimCases.reduce((sum, c) => {
    return sum + (chartMetric.value === 'count' ? c.count : 1);
  }, 0);
});

// Group claim cases by category, sum values, sort descending, slice top 5
const topCategories = computed(() => {
  const categoryMap: Record<string, number> = {};
  
  props.claimCases.forEach(c => {
    let cat = c.category || '미분류';
    if (cat.trim() === '') cat = '미분류';
    
    const valueToAdd = chartMetric.value === 'count' ? c.count : 1;
    if (!categoryMap[cat]) categoryMap[cat] = 0;
    categoryMap[cat] += valueToAdd;
  });
  
  return Object.entries(categoryMap)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 5);
});

const chartSeries = computed(() => [
  {
    name: chartMetric.value === 'count' ? '오류 건수' : '청구 건수',
    data: topCategories.value.map(c => c.value)
  }
]);

const chartOptions = computed(() => ({
  chart: {
    type: 'bar' as const,
    fontFamily: 'Plus Jakarta Sans, Pretendard, sans-serif',
    toolbar: { show: false }
  },
  plotOptions: {
    bar: {
      barHeight: '45%',
      distributed: true,
      horizontal: true,
      borderRadius: 4,
      dataLabels: {
        position: 'right'
      }
    }
  },
  colors: ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'],
  legend: { show: false },
  grid: {
    borderColor: '#f1f5f9',
    xaxis: { lines: { show: true } },
    yaxis: { lines: { show: false } }
  },
  xaxis: {
    categories: topCategories.value.map(c => {
      // Shorten label if it's too long
      const name = c.name;
      return name.length > 18 ? name.substring(0, 18) + '...' : name;
    }),
    labels: {
      style: { colors: '#64748b', fontSize: '10px' }
    },
    axisBorder: { show: false },
    axisTicks: { show: false }
  },
  yaxis: {
    labels: {
      style: { colors: '#334155', fontWeight: 600, fontSize: '11px' }
    }
  },
  dataLabels: {
    enabled: true,
    textAnchor: 'start' as const,
    style: {
      colors: ['#0f172a'],
      fontSize: '11px',
      fontWeight: 'bold'
    },
    formatter: function(val: number) {
      return ` ${val.toLocaleString()} 건`;
    },
    offsetX: 5
  },
  tooltip: {
    custom: function({ series, seriesIndex, dataPointIndex, w }: any) {
      const fullCategoryName = topCategories.value[dataPointIndex]?.name || '';
      const val = series[seriesIndex][dataPointIndex];
      return `
        <div class="pa-2 font-weight-medium text-caption" style="background:#fff; border:1px solid #e2e8f0; border-radius:6px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
          <div style="font-weight:700; color:#0f172a; margin-bottom:4px;">${fullCategoryName}</div>
          <div style="color:#2563eb;">건수: <strong>${val.toLocaleString()}건</strong></div>
        </div>
      `;
    }
  }
}));

function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num || 0);
}
</script>

<style scoped>
.table-card {
  background: #ffffff;
  border-radius: 9px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}
.table-card-title { font-size: 14px; font-weight: 800; color: #0f172a; }
.block { display: block; }
.chart-container-inner {
  background-color: #f1f5f9;
  border-radius: 9px;
  margin-top: 8px;
  border: 1px solid #cbd5e1;
  width: 100%;
}

/* custom-tab-group */
.custom-tab-group {
  display: flex;
  background-color: #f1f5f9;
  padding: 3px;
  border-radius: 8px;
  gap: 2px;
  height: 28px;
  box-sizing: border-box;
  align-items: center;
}
.custom-tab-btn {
  border: none;
  background: transparent;
  padding: 0 12px;
  height: 100%;
  font-size: 10.5px;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  outline: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}
.custom-tab-btn.active {
  background-color: #ffffff;
  color: #2563eb;
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
</style>
