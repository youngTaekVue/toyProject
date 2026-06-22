<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h5 mb-4">자산 내역 Treemap</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card outlined class="pa-4">
          <v-card-title>자산 및 부채 현황</v-card-title>
          <v-card-subtitle v-if="loading">데이터 로딩 중...</v-card-subtitle>
          <v-card-subtitle v-else-if="!treemapSeries[0] || !treemapSeries[0].data.length">표시할 데이터가 없습니다. 엑셀을 업로드해주세요.</v-card-subtitle>
          <apexchart v-else type="treemap" height="500" :options="treemapOptions" :series="treemapSeries"></apexchart>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import VueApexCharts from 'vue3-apexcharts'; // ApexCharts 임포트

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/python';

const loading = ref(true);
const treemapSeries = ref<any[]>([]);
const treemapOptions = ref({
  legend: {
    show: false
  },
  chart: {
    height: 500,
    type: 'treemap',
    events: {
      // 클릭 이벤트 핸들러 (필요시 추가)
      dataPointSelection: (event: any, chartContext: any, config: any) => {
        // config.w.config.series[config.seriesIndex].data[config.dataPointIndex]는 최하위 노드 데이터
        // Multi-dimensional Treemap에서 클릭된 노드의 실제 데이터를 가져오려면 좀 더 복잡한 로직이 필요할 수 있습니다.
        // 여기서는 간단히 콘솔에 출력합니다.
        const clickedNode = config.w.globals.series[config.seriesIndex][config.dataPointIndex];
        console.log('Treemap data point clicked:', clickedNode);
        console.log('Category:', clickedNode.x);
        console.log('Amount:', clickedNode.y);
      }
    }
  },
  title: {
    text: '자산 및 부채 상세',
    align: 'center'
  },
  dataLabels: {
    enabled: true,
    formatter: function(text: string, op: any) {
      // op.value는 백엔드에서 음수로 보낸 부채 값일 수 있으므로 Math.abs 적용
      return [text, new Intl.NumberFormat('ko-KR').format(Math.abs(op.value)) + '원'];
    },
    style: {
      fontSize: '15px',
      fontFamily: 'Malgun Gothic, sans-serif',
      colors: ['#fff']
    },
  },
  plotOptions: {
    treemap: {
      enableShades: true,
      shadeIntensity: 0.5,
      reverseNegativeShade: true,
      distributed: true, // 각 최상위 노드에 다른 색상 적용
      colorScale: {
        ranges: [
          {
            from: 0.001, // 0보다 큰 값 (자산)
            to: 1000000000000, // 충분히 큰 양수
            color: '#28a745', // 초록색 계열 (자산)
            name: '자산'
          },
          {
            from: -1000000000000, // 충분히 작은 음수
            to: -0.001, // 0보다 작은 값 (부채)
            color: '#dc3545', // 빨간색 계열 (부채)
            name: '부채'
          }
        ]
      }
    }
  },
  tooltip: {
    y: {
      formatter: function(value: number) {
        // value는 백엔드에서 음수로 보낸 부채 값일 수 있으므로 Math.abs 적용
        return new Intl.NumberFormat('ko-KR').format(Math.abs(value)) + '원';
      }
    }
  }
});

const fetchTreemapData = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`${API_BASE_URL}/financial_treemap_data`);
    const data = response.data;

    // ApexCharts Treemap은 series가 [{ data: [...] }] 형태를 기대합니다.
    // 백엔드에서 이미 적절한 계층 구조를 반환하므로 그대로 사용합니다.
    if (data && data.length > 0) {
      treemapSeries.value = [{ data: data }];
    } else {
      treemapSeries.value = [];
    }
  } catch (error) {
    console.error('Error fetching treemap data:', error);
    treemapSeries.value = [];
    // 사용자에게 오류 메시지 표시
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchTreemapData();
});
</script>

<style scoped>
/* Scoped styles for FinancialStatus Treemap View */
.v-card {
  border-radius: 8px;
}
</style>