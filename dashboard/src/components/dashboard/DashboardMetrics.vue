<template>
  <v-row class="summary-cards">
    <v-col cols="12" sm="6" md="4" lg="3" v-for="n in 5" :key="n">
      <div class="card neumorphic-card">
        <v-skeleton-loader
          v-if="loading"
          type="card-heading, list-item-two-line"
          class="neumorphic-skeleton"
        ></v-skeleton-loader>
        <template v-else>
          <div class="card-content">
            <h4>{{ metrics[n-1].title }}</h4>
            <p class="card-value">{{ metrics[n-1].value }} <span :class="metrics[n-1].growthClass">{{ metrics[n-1].growth }}</span></p>
          </div>
          <div class="card-icon"><v-icon>{{ metrics[n-1].icon }}</v-icon></div>
        </template>
      </div>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

interface Metric {
  title: string;
  value: string;
  growth: string;
  growthClass: string;
  icon: string;
}

const loading = ref(true);
const metrics = ref<Metric[]>([]);

const fetchedMetrics: Metric[] = [
  { title: '총 설치 수', value: '150,000', growth: '+12%', growthClass: 'growth-positive', icon: 'mdi-download' },
  { title: '일일 활성 사용자 (DAU)', value: '25,000', growth: '+5%', growthClass: 'growth-positive', icon: 'mdi-account-group' },
  { title: '월간 활성 사용자 (MAU)', value: '75,000', growth: '+8%', growthClass: 'growth-positive', icon: 'mdi-account-check' },
  { title: '평균 평점', value: '4.5', growth: '(1.2만 리뷰)', growthClass: 'growth-positive', icon: 'mdi-star' },
  { title: '예상 수익', value: '$1,200', growth: '+15%', growthClass: 'growth-positive', icon: 'mdi-currency-usd' },
];

onMounted(() => {
  // Simulate data fetching
  setTimeout(() => {
    metrics.value = fetchedMetrics;
    loading.value = false;
  }, 2000); // Simulate a 2-second network request
});
</script>

<style scoped>
/* Styles specific to DashboardMetrics */
.neumorphic-card {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 15px 20px 0 rgba(0,0,0,0.04);
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  height: 100%;
  display: flex;
  flex-direction: column; /* Changed to column for better stacking of content and icon */
  justify-content: space-between;
  align-items: flex-start; /* Align content to start */
}

.neumorphic-skeleton {
  width: 100%;
}

.card-content {
  width: 100%; /* Ensure content takes full width */
  margin-bottom: 10px; /* Add some space between content and icon */
}

.summary-cards .card {
  /* This style is now mostly handled by .neumorphic-card directly */
}

.summary-cards h4 {
  font-size: 12px;
  color: var(--secondary-text);
  margin-bottom: 4px;
}
.card-value { font-size: 16px; font-weight: 700; }
.growth-positive, .growth-negative {
  font-size: 11px;
  margin-left: 4px;
}
.growth-positive { color: #28a745; }
.growth-negative { color: #dc3545; }

.card-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(310deg, #007bff 0%, #00c6ff 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  align-self: flex-end; /* Align icon to the end */
}

/* Responsive styles for these cards */
@media (min-width: 600px) {
  .summary-cards h4 { font-size: 13px; }
  .card-value { font-size: 17px; }
  .growth-positive, .growth-negative { font-size: 12px; }
  .card-icon { width: 42px; height: 42px; font-size: 17px; }
}

@media (min-width: 840px) {
  .summary-cards h4 { font-size: 14px; }
  .card-value { font-size: 18px; }
  .growth-positive, .growth-negative { font-size: 13px; }
  .card-icon { width: 44px; height: 44px; font-size: 18px; }
}

@media (min-width: 1145px) {
  .summary-cards h4 { font-size: 15px; }
  .card-value { font-size: 20px; }
  .growth-positive, .growth-negative { font-size: 14px; }
  .card-icon { width: 48px; height: 48px; font-size: 20px; }
}

@media (min-width: 1545px) {
  .summary-cards h4 { font-size: 16px; }
  .card-value { font-size: 22px; }
  .growth-positive, .growth-negative { font-size: 15px; }
  .card-icon { width: 52px; height: 52px; font-size: 22px; }
}

@media (min-width: 2138px) {
  .summary-cards h4 { font-size: 18px; }
  .card-value { font-size: 24px; }
  .growth-positive, .growth-negative { font-size: 16px; }
  .card-icon { width: 56px; height: 56px; font-size: 24px; }
}
</style>