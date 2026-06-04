<!--<template>-->
<!--  <v-row class="summary-cards">-->
<!--    <v-col cols="12" sm="6" md="4" lg="3" v-for="n in 5" :key="n">-->
<!--      <div class="card neumorphic-card">-->
<!--        <v-skeleton-loader-->
<!--          v-if="loading"-->
<!--          type="card-heading, list-item-two-line"-->
<!--          class="neumorphic-skeleton"-->
<!--        ></v-skeleton-loader>-->
<!--        <template v-else>-->
<!--          <div class="card-content">-->
<!--            <h4>{{ metrics[n-1].title }}</h4>-->
<!--            <p class="card-value">{{ metrics[n-1].value }} <span :class="metrics[n-1].growthClass">{{ metrics[n-1].growth }}</span></p>-->
<!--          </div>-->
<!--          <div class="card-icon"><v-icon>{{ metrics[n-1].icon }}</v-icon></div>-->
<!--        </template>-->
<!--      </div>-->
<!--    </v-col>-->
<!--  </v-row>-->

<!--  &lt;!&ndash; ApexCharts Section &ndash;&gt;-->
<!--  <v-row class="chart-section mt-5">-->
<!--    <v-col cols="12">-->
<!--      <div class="neumorphic-card chart-container">-->
<!--        <v-skeleton-loader-->
<!--          v-if="loading"-->
<!--          type="article"-->
<!--          class="neumorphic-skeleton"-->
<!--        ></v-skeleton-loader>-->
<!--        <template v-else>-->
<!--          <h3>월별 사용자 증가 추이</h3>-->
<!--          &lt;!&ndash; 차트 컨테이너가 보이는지 확인하기 위해 배경색 추가 &ndash;&gt;-->
<!--          <div style="background-color: #e0e0e0; padding: 10px; border-radius: 8px;">-->
<!--            <apexchart type="line" height="350" :options="chartOptions" :series="series"></apexchart>-->
<!--          </div>-->
<!--        </template>-->
<!--      </div>-->
<!--    </v-col>-->
<!--  </v-row>-->
<!--</template>-->

<!--<script setup lang="ts">-->
<!--import { ref, onMounted } from 'vue';-->

<!--interface Metric {-->
<!--  title: string;-->
<!--  value: string;-->
<!--  growth: string;-->
<!--  growthClass: string;-->
<!--  icon: string;-->
<!--}-->

<!--const loading = ref(true);-->
<!--const metrics = ref<Metric[]>([]);-->

<!--const fetchedMetrics: Metric[] = [-->
<!--  { title: '총 설치 수', value: '150,000', growth: '+12%', growthClass: 'growth-positive', icon: 'mdi-download' },-->
<!--  { title: '일일 활성 사용자 (DAU)', value: '25,000', growth: '+5%', growthClass: 'growth-positive', icon: 'mdi-account-group' },-->
<!--  { title: '월간 활성 사용자 (MAU)', value: '75,000', growth: '+8%', growthClass: 'growth-positive', icon: 'mdi-account-check' },-->
<!--  { title: '평균 평점', value: '4.5', growth: '(1.2만 리뷰)', growthClass: 'growth-positive', icon: 'mdi-star' },-->
<!--  { title: '예상 수익', value: '$1,200', growth: '+15%', growthClass: 'growth-positive', icon: 'mdi-currency-usd' },-->
<!--];-->

<!--// ApexCharts 데이터 및 옵션 (더 간단한 샘플)-->
<!--const series = ref([-->
<!--  {-->
<!--    name: "Sample Data",-->
<!--    data: [30, 40, 35, 50, 49, 60, 70, 91, 125]-->
<!--  }-->
<!--]);-->

<!--const chartOptions = ref({-->
<!--  chart: {-->
<!--    height: 350,-->
<!--    type: 'line',-->
<!--    toolbar: {-->
<!--      show: false-->
<!--    }-->
<!--  },-->
<!--  xaxis: {-->
<!--    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],-->
<!--  },-->
<!--  stroke: {-->
<!--    curve: 'smooth'-->
<!--  },-->
<!--  title: {-->
<!--    text: 'Sample Line Chart',-->
<!--    align: 'left',-->
<!--    style: {-->
<!--      fontSize: '16px',-->
<!--      color: '#252f40'-->
<!--    }-->
<!--  },-->
<!--  grid: {-->
<!--    row: {-->
<!--      colors: ['#f3f3f3', 'transparent'],-->
<!--      opacity: 0.5-->
<!--    },-->
<!--  },-->
<!--  colors: ['#007bff'],-->
<!--});-->


<!--onMounted(() => {-->
<!--  console.log('DashboardMetrics mounted. Initial loading state:', loading.value);-->
<!--  // Simulate data fetching-->
<!--  setTimeout(() => {-->
<!--    metrics.value = fetchedMetrics;-->
<!--    loading.value = false;-->
<!--    console.log('DashboardMetrics loading finished. New loading state:', loading.value);-->
<!--  }, 2000); // Simulate a 2-second network request-->
<!--});-->
<!--</script>-->

<!--<style scoped>-->
<!--/* Styles specific to DashboardMetrics */-->
<!--.neumorphic-card {-->
<!--  background: #fff;-->
<!--  border-radius: 12px;-->
<!--  box-shadow: 0 10px 15px 0 rgba(0,0,0,0.03);-->
<!--  padding: 16px;-->
<!--  border: 1px solid rgba(255, 255, 255, 0.3);-->
<!--  height: 100%;-->
<!--  display: flex;-->
<!--  justify-content: space-between;-->
<!--  align-items: center;-->
<!--}-->

<!--.neumorphic-skeleton {-->
<!--  width: 100%;-->
<!--}-->

<!--.card-content {-->
<!--  margin-right: 10px;-->
<!--}-->

<!--.summary-cards h4 {-->
<!--  font-size: clamp(12px, 1.2vw, 14px);-->
<!--  color: var(&#45;&#45;secondary-text);-->
<!--  margin-bottom: 3px;-->
<!--}-->
<!--.card-value {-->
<!--  font-size: clamp(16px, 2vw, 20px);-->
<!--  font-weight: 700;-->
<!--}-->
<!--.growth-positive, .growth-negative {-->
<!--  font-size: clamp(10px, 1vw, 12px);-->
<!--  margin-left: 4px;-->
<!--}-->
<!--.growth-positive { color: #28a745; }-->
<!--.growth-negative { color: #dc3545; }-->

<!--.card-icon {-->
<!--  width: clamp(36px, 4vw, 48px);-->
<!--  height: clamp(36px, 4vw, 48px);-->
<!--  background: linear-gradient(310deg, #007bff 0%, #00c6ff 100%);-->
<!--  border-radius: 8px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  justify-content: center;-->
<!--  color: white;-->
<!--  font-size: clamp(16px, 2vw, 20px);-->
<!--  flex-shrink: 0;-->
<!--}-->

<!--.chart-container {-->
<!--  padding: 20px;-->
<!--}-->

<!--.chart-container h3 {-->
<!--  font-size: clamp(16px, 2vw, 20px);-->
<!--  font-weight: 700;-->
<!--  margin-bottom: 15px;-->
<!--  color: var(&#45;&#45;primary-text);-->
<!--}-->
<!--</style>-->