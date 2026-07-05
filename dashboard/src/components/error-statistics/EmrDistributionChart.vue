<template>
  <v-card class="table-card pa-5" elevation="0">
    <div class="d-flex justify-space-between align-center mb-1 flex-wrap gap-y-2">
      <div>
        <span class="table-card-title block">EMR사별 에러 분포</span>
        <p class="text-caption text-grey-darken-1 mb-0 mt-0.5">
          각 EMR 소프트웨어별 에러 비중 (총 {{ formatNumber(totalSum) }} 건)
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
    <div class="chart-container-inner d-flex justify-center align-center" style="padding: 12px;">
      <apexchart type="treemap" width="100%" height="260" :options="chartOptions" :series="chartSeries"></apexchart>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import VueApexCharts from 'vue3-apexcharts';

const apexchart = VueApexCharts;

interface EmrGroup {
  emr: string;
  count: number;
  casesCount: number;
  resolutionRate: number;
  cases: any[];
}

const props = defineProps<{
  groupedEmrs: EmrGroup[];
}>();

const chartMetric = ref<'count' | 'cases'>('count');

const totalSum = computed(() => {
  return props.groupedEmrs.reduce((sum, e) => {
    return sum + (chartMetric.value === 'count' ? e.count : e.casesCount);
  }, 0);
});

const chartData = computed(() => {
  const list = [...props.groupedEmrs].sort((a, b) => {
    const valA = chartMetric.value === 'count' ? a.count : a.casesCount;
    const valB = chartMetric.value === 'count' ? b.count : b.casesCount;
    return valB - valA;
  });
  
  return list.map(e => ({
    x: e.emr,
    y: chartMetric.value === 'count' ? e.count : e.casesCount
  }));
});

const chartSeries = computed(() => [
  {
    data: chartData.value
  }
]);

const chartOptions = computed(() => ({
  legend: { show: false },
  chart: { 
    type: 'treemap' as const, 
    fontFamily: 'Plus Jakarta Sans, Pretendard, sans-serif',
    toolbar: { show: false }
  },
  colors: ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#94a3b8', '#14b8a6', '#f43f5e', '#a855f7'],
  plotOptions: {
    treemap: {
      distributed: true,
      enableShades: false
    }
  },
  dataLabels: {
    enabled: true,
    style: {
      fontSize: '11px',
      fontWeight: 'bold',
      fontFamily: 'Plus Jakarta Sans, Pretendard, sans-serif'
    },
    formatter: function(text: string, op: any) {
      return `${text}: ${op.value.toLocaleString()} 건`;
    }
  },
  tooltip: {
    y: {
      formatter: (val: number) => `${val.toLocaleString()} 건`
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
