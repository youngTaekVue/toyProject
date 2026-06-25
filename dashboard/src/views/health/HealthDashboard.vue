<template>
  <v-container fluid class="health-dashboard-section pt-0">
    <h1 class="text-h5 mb-4">Google Fit 대시보드</h1>

    <!-- Date Selector -->
    <v-row class="mb-4">
      <v-col cols="12" md="4">
        <v-menu
            v-model="dateMenu"
            :close-on-content-click="false"
            :nudge-right="40"
            transition="scale-transition"
            offset-y
            min-width="auto"
        >
          <template v-slot:activator="{ props }">
            <v-text-field
                v-model="selectedDate"
                label="날짜 선택"
                prepend-icon="mdi-calendar"
                readonly
                v-bind="props"
                class="neumorphic-select"
                hide-details
            ></v-text-field>
          </template>
          <v-date-picker
              v-model="datePickerDate"
              @update:model-value="selectDate"
              color="primary"
              :max="new Date().toISOString().substr(0, 10)"
          ></v-date-picker>
        </v-menu>
      </v-col>
    </v-row>

    <!-- Loading State for all sections -->
    <template v-if="loading">
      <v-row class="summary-cards">
        <v-col cols="12" sm="6" md="3" v-for="n in 4" :key="`kpi-skeleton-${n}`">
          <v-card class="neumorphic-card pa-3 text-center">
            <v-skeleton-loader type="card-heading, list-item-two-line" class="mx-auto" height="100px"></v-skeleton-loader>
          </v-card>
        </v-col>
      </v-row>

      <h2 class="dashboard-section-title mt-4">활동 요약</h2>
      <v-row>
        <v-col cols="12" sm="6" md="4" v-for="n in 3" :key="`activity-skeleton-${n}`">
          <v-card class="neumorphic-card pa-3 text-center">
            <v-skeleton-loader type="card-heading, list-item-two-line" class="mx-auto" height="100px"></v-skeleton-loader>
          </v-card>
        </v-col>
      </v-row>

      <h2 class="dashboard-section-title mt-4">신체 지표</h2>
      <v-row>
        <v-col cols="12" sm="6" md="4" v-for="n in 2" :key="`body-skeleton-${n}`">
          <v-card class="neumorphic-card pa-3 text-center">
            <v-skeleton-loader type="card-heading, list-item-two-line" class="mx-auto" height="100px"></v-skeleton-loader>
          </v-card>
        </v-col>
      </v-row>

      <h2 class="dashboard-section-title mt-4">수면</h2>
      <v-row>
        <v-col cols="12" sm="6" md="4">
          <v-card class="neumorphic-card pa-3 text-center">
            <v-skeleton-loader type="card-heading, list-item-two-line" class="mx-auto" height="100px"></v-skeleton-loader>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Actual Data Display -->
    <template v-else-if="error">
      <v-alert type="error" class="mt-4">{{ error }}</v-alert>
      <v-btn v-if="isAuthRequired" color="primary" class="mt-4" @click="redirectToGoogleAuth">Google Fit 인증하기</v-btn>
    </template>

    <template v-else>
      <!-- Activity Summary -->
      <h2 class="dashboard-section-title mt-4">활동 요약</h2>
      <v-row class="summary-cards">
        <v-col cols="12" sm="6" md="3">
          <v-card class="neumorphic-card pa-3 text-center">
            <v-icon size="36" color="blue-darken-2">mdi-walk</v-icon>
            <div class="text-subtitle-2 text-grey">걸음 수</div>
            <div class="text-h5 font-weight-bold text-blue-darken-2">{{ formatNumber(dailyData.activity.steps) }}</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="neumorphic-card pa-3 text-center">
            <v-icon size="36" color="green-darken-2">mdi-map-marker-distance</v-icon>
            <div class="text-subtitle-2 text-grey">이동 거리</div>
            <div class="text-h5 font-weight-bold text-green-darken-2">{{ formatDistance(dailyData.activity.distance) }}</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="neumorphic-card pa-3 text-center">
            <v-icon size="36" color="orange-darken-2">mdi-fire</v-icon>
            <div class="text-subtitle-2 text-grey">소모 칼로리</div>
            <div class="text-h5 font-weight-bold text-orange-darken-2">{{ formatNumber(dailyData.activity.caloriesBurned) }} kcal</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="neumorphic-card pa-3 text-center">
            <v-icon size="36" color="purple-darken-2">mdi-timer-outline</v-icon>
            <div class="text-subtitle-2 text-grey">활동 시간</div>
            <div class="text-h5 font-weight-bold text-purple-darken-2">{{ formatMinutes(dailyData.activity.activeMinutes) }}</div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Body Metrics -->
      <h2 class="dashboard-section-title mt-4">신체 지표</h2>
      <v-row class="summary-cards">
        <v-col cols="12" sm="6" md="3">
          <v-card class="neumorphic-card pa-3 text-center">
            <v-icon size="36" color="teal-darken-2">mdi-weight-kilogram</v-icon>
            <div class="text-subtitle-2 text-grey">체중</div>
            <div class="text-h5 font-weight-bold text-teal-darken-2">{{ formatNumber(dailyData.body.weight) }} kg</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="neumorphic-card pa-3 text-center">
            <v-icon size="36" color="red-darken-2">mdi-heart-pulse</v-icon>
            <div class="text-subtitle-2 text-grey">평균 심박수</div>
            <div class="text-h5 font-weight-bold text-red-darken-2">{{ formatNumber(dailyData.body.heartRateAvg) }} bpm</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3" v-if="dailyData.body.bloodPressureSystolic">
          <v-card class="neumorphic-card pa-3 text-center">
            <v-icon size="36" color="indigo-darken-2">mdi-blood-pressure</v-icon>
            <div class="text-subtitle-2 text-grey">혈압</div>
            <div class="text-h5 font-weight-bold text-indigo-darken-2">
              {{ dailyData.body.bloodPressureSystolic }} / {{ dailyData.body.bloodPressureDiastolic }} mmHg
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Sleep Data -->
      <h2 class="dashboard-section-title mt-4">수면</h2>
      <v-row class="summary-cards">
        <v-col cols="12" sm="6" md="3">
          <v-card class="neumorphic-card pa-3 text-center">
            <v-icon size="36" color="deep-purple-darken-2">mdi-sleep</v-icon>
            <div class="text-subtitle-2 text-grey">총 수면 시간</div>
            <div class="text-h5 font-weight-bold text-deep-purple-darken-2">{{ formatMinutes(dailyData.sleep.totalSleepMinutes) }}</div>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import { VSkeletonLoader } from 'vuetify/lib/components/index.mjs'; // VSkeletonLoader 명시적 임포트

// API_BASE_URL은 .env 파일에서 가져오거나 기본값 설정
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/health';

// --- 반응형 상태 변수 ---
const loading = ref<boolean>(true); // 로딩 상태
const error = ref<string | null>(null); // 오류 메시지
const isAuthRequired = ref<boolean>(false); // Google Fit 인증 필요 여부
const dailyData = ref<DailyFitData | null>(null); // 현재 선택된 날짜의 Google Fit 데이터

const dateMenu = ref<boolean>(false); // 날짜 선택기 메뉴 상태
const selectedDate = ref<string>(new Date().toISOString().substr(0, 10)); // 선택된 날짜 (YYYY-MM-DD)
const datePickerDate = ref<Date>(new Date()); // v-date-picker용 Date 객체

// --- 헬퍼 함수 ---
const formatNumber = (value: number | undefined): string => {
  return value !== undefined ? new Intl.NumberFormat('ko-KR').format(value) : 'N/A';
};

const formatDistance = (value: number | undefined): string => {
  if (value === undefined) return 'N/A';
  const km = value / 1000;
  return new Intl.NumberFormat('ko-KR', { maximumFractionDigits: 2 }).format(km) + ' km';
};

const formatMinutes = (value: number | undefined): string => {
  if (value === undefined) return 'N/A';
  const hours = Math.floor(value / 60);
  const minutes = value % 60;
  if (hours > 0) {
    return `${hours}시간 ${minutes}분`;
  }
  return `${minutes}분`;
};

const selectDate = (date: Date) => {
  selectedDate.value = date.toISOString().substr(0, 10);
  dateMenu.value = false;
};

const redirectToGoogleAuth = () => {
  // 백엔드에서 받은 리디렉션 URL이 있다면 그곳으로 이동
  // 여기서는 백엔드 엔드포인트를 다시 호출하여 리디렉션 응답을 받도록 가정
  fetchGoogleFitData();
};

// --- 데이터 가져오기 로직 ---
const fetchGoogleFitData = async () => {
  loading.value = true;
  error.value = null;
  isAuthRequired.value = false;
  dailyData.value = null;

  try {
    // 백엔드에 선택된 날짜를 파라미터로 전달
    const response = await axios.get(`${API_BASE_URL}/health/google-fit/auth`, {
      params: { date: selectedDate.value }
    });

    if (response.data && response.data.status === 'redirect' && response.data.redirect_url) {
      console.log('Google 인증으로 리디렉션합니다:', response.data.redirect_url);
      isAuthRequired.value = true;
      error.value = 'Google Fit 데이터에 접근하려면 인증이 필요합니다.';
      // 실제 리디렉션은 버튼 클릭 시 또는 사용자에게 알린 후 진행
      // window.location.href = response.data.redirect_url;
    } else if (response.data && response.data.status === 'success' && response.data.data) {
      dailyData.value = response.data.data;
      console.log('Google Fit 데이터 가져오기 성공:', dailyData.value);
    } else {
      console.warn('백엔드로부터 예상치 못한 응답:', response.data);
      error.value = 'Google Fit 데이터를 가져오는 중 예상치 못한 오류가 발생했습니다.';
    }
  } catch (err: any) {
    console.error('Google Fit 데이터 가져오기 오류:', err);
    if (err.response) {
      error.value = `데이터 가져오기 오류: ${err.response.status} - ${err.response.data.message || err.response.statusText}`;
      if (err.response.status === 401 || err.response.status === 403) { // 인증 관련 오류
        isAuthRequired.value = true;
      }
    } else if (err.request) {
      error.value = '백엔드에 연결할 수 없습니다. CORS 설정 또는 네트워크 연결을 확인하세요.';
    } else {
      error.value = `요청 설정 오류: ${err.message}`;
    }
  } finally {
    loading.value = false;
  }
};

// --- 라이프사이클 훅 및 Watcher ---
onMounted(() => {
  fetchGoogleFitData(); // 컴포넌트 마운트 시 데이터 가져오기
});

watch(selectedDate, (newDate, oldDate) => {
  if (newDate !== oldDate) {
    fetchGoogleFitData(); // 선택 날짜 변경 시 데이터 다시 가져오기
  }
});

// --- 임시 데이터 (백엔드 연동 전 테스트용) ---
// 백엔드에서 실제 데이터를 가져오기 전까지는 이 데이터를 사용하여 UI를 테스트할 수 있습니다.
// dailyData.value = {
//   date: '2023-10-26',
//   activity: {
//     steps: 8500,
//     distance: 6200, // meters
//     caloriesBurned: 450,
//     activeMinutes: 90,
//   },
//   body: {
//     weight: 70.5, // kg
//     heartRateAvg: 75, // bpm
//     bloodPressureSystolic: 120,
//     bloodPressureDiastolic: 80,
//   },
//   sleep: {
//     totalSleepMinutes: 480, // minutes
//   },
// };
</script>

<style scoped lang="scss">
// Import global variables - MUST BE FIRST
@use '../../styles/settings.scss' as *;

/* Main container styling */
.health-dashboard-section {
  margin-top: 40px;
}

/* Section titles */
.dashboard-section-title {
  font-size: 18px; /* Base for xs */
  font-weight: 700;
  margin-bottom: 20px;
  margin-top: 40px; /* Consistent spacing for sections */
  color: $primary-text;
}

/* Neumorphic Card style (copied from AppLayout for self-containment, or can be imported) */
.neumorphic-card {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 15px 20px 0 rgba(0,0,0,0.04);
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  height: 100%; /* Ensure cards in v-col take full height */
}

/* Vuetify v-row adds negative margins, so we need to adjust */
.summary-cards {
  margin-bottom: 25px; /* Reduced margin */
}

/* Custom styling for v-select to give a soft, integrated look */
.neumorphic-select.v-select :deep(.v-field) {
  background-color: $bg-color; /* Use background color from theme */
  border-radius: 10px;
  box-shadow: inset 2px 2px 5px $shadow-dark, inset -3px -3px 7px $shadow-light; /* Inner shadow for embossed effect */
  border: none; /* Remove default border */
  transition: all 0.3s ease;
  min-height: 48px; /* Standard Vuetify input height */
}

.neumorphic-select.v-select :deep(.v-field__outline) {
  display: none; /* Hide default outline */
}

.neumorphic-select.v-select :deep(.v-field__input) {
  color: $primary-text;
  font-size: 14px;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  min-height: unset !important;
  height: auto !important;
  display: flex;
  align-items: center;
}

.neumorphic-select.v-select :deep(.v-field__label) {
  color: $secondary-text;
  font-size: 14px;
  top: 50% !important;
  transform: translateY(-50%) !important;
  left: 12px !important;
  transition: all 0.3s ease;
}

.neumorphic-select.v-select.v-field--active :deep(.v-field__label),
.neumorphic-select.v-select.v-field--dirty :deep(.v-field__label) {
  top: 0 !important;
  transform: translateY(-100%) scale(0.75) !important;
  left: 12px !important;
  background: $accent-gradient; /* Use accent color for active label */
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.neumorphic-select.v-select:hover :deep(.v-field) {
  box-shadow: inset 1px 1px 3px $shadow-dark, inset -1px -1px 3px $shadow-light; /* Subtle hover effect */
}

.neumorphic-select.v-select :deep(.v-field__append-inner) {
  align-self: center;
  padding-top: 0 !important;
}

/* General text colors for consistency */
.text-h5, .text-h6, .text-body-1 {
  color: $primary-text;
}
.text-subtitle-1, .text-subtitle-2, .text-caption, .text-grey, .text-grey-darken-1 {
  color: $secondary-text;
}

/* Responsive Font Sizes (Copied from AppDashboard.vue) */
/* Small (sm) - 600px and up */
@media (min-width: 600px) {
  .dashboard-section-title { font-size: 19px; }
  .summary-cards .text-h5 { font-size: 17px; }
  .summary-cards .text-subtitle-2, .summary-cards .text-caption { font-size: 13px; }
}

/* Medium (md) - 840px and up */
@media (min-width: 840px) {
  .dashboard-section-title { font-size: 20px; }
  .summary-cards .text-h5 { font-size: 18px; }
  .summary-cards .text-subtitle-2, .summary-cards .text-caption { font-size: 14px; }
}

/* Large (lg) - 1145px and up */
@media (min-width: 1145px) {
  .dashboard-section-title { font-size: 22px; }
  .summary-cards .text-h5 { font-size: 20px; }
  .summary-cards .text-subtitle-2, .summary-cards .text-caption { font-size: 15px; }
}

/* Extra Large (xl) - 1545px and up */
@media (min-width: 1545px) {
  .dashboard-section-title { font-size: 24px; }
  .summary-cards .text-h5 { font-size: 22px; }
  .summary-cards .text-subtitle-2, .summary-cards .text-caption { font-size: 16px; }
}

/* Extra Extra Large (xxl) - 2138px and up */
@media (min-width: 2138px) {
  .dashboard-section-title { font-size: 26px; }
  .summary-cards .text-h5 { font-size: 24px; }
  .summary-cards .text-subtitle-2, .summary-cards .text-caption { font-size: 17px; }
}
</style>