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
  border-radius: 12px; /* Adjusted to match AppLayout */
  box-shadow: 0 10px 15px 0 rgba(0,0,0,0.03); /* Adjusted to match AppLayout */
  padding: 16px; /* Adjusted to match AppLayout */
  border: 1px solid rgba(255, 255, 255, 0.3);
  height: 100%;
  display: flex; /* Changed to flex for horizontal layout */
  justify-content: space-between; /* Space between content and icon */
  align-items: center; /* Vertically center content and icon */
}

.neumorphic-skeleton {
  width: 100%;
}

.card-content {
  /* No specific width needed, flex will handle it */
  margin-right: 10px; /* Space between content and icon */
}

.summary-cards h4 {
  font-size: clamp(12px, 1.2vw, 14px); /* Responsive typography */
  color: var(--secondary-text);
  margin-bottom: 3px; /* Adjusted margin */
}
.card-value {
  font-size: clamp(16px, 2vw, 20px); /* Responsive typography */
  font-weight: 700;
}
.growth-positive, .growth-negative {
  font-size: clamp(10px, 1vw, 12px); /* Responsive typography */
  margin-left: 4px;
}
.growth-positive { color: #28a745; }
.growth-negative { color: #dc3545; }

.card-icon {
  width: clamp(36px, 4vw, 48px); /* Responsive width */
  height: clamp(36px, 4vw, 48px); /* Responsive height */
  background: linear-gradient(310deg, #007bff 0%, #00c6ff 100%);
  border-radius: 8px; /* Adjusted border-radius */
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: clamp(16px, 2vw, 20px); /* Responsive icon size */
  flex-shrink: 0; /* Prevent icon from shrinking */
}

/* Removed all previous media queries as clamp() and v-col handle responsiveness */
</style>
