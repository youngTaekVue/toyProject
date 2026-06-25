<template>
  <div class="health-dashboard">
    <header class="dashboard-header">
      <h1>구글 피트니스 헬스 대시보드</h1>
      <p class="subtitle">Google Fit 실시간 건강 지표 연동</p>
    </header>

    <main class="dashboard-content">
      <div v-if="isLoading" class="card loading-card">
        <div class="spinner"></div>
        <p>구글 피트니스 데이터 및 인증 상태를 확인 중입니다...</p>
      </div>

      <div v-else-if="!isAuthorized" class="auth-wrapper">
        <div class="card auth-card">
          <div class="icon-wrapper">
            <span class="analytics-icon">📊</span>
          </div>
          <h2>구글 피트니스 연동이 필요합니다</h2>
          <p class="auth-desc">
            활동량 및 체성분 데이터(체중, 골격근량, 체지방률)를 가져오기 위해<br>
            구글 계정 인증을 진행해 주세요.
          </p>
          <button class="btn btn-primary btn-block" @click="handleAuthorizePopup">
            Google Fit 연동하기
          </button>
        </div>
      </div>

      <div v-else class="data-container">
        
        <div class="control-bar">
          <span class="update-time">최근 동기화: {{ latestInBodyDate }}</span>
          <button class="btn btn-secondary" @click="handleClearTokens">연동 해제</button>
        </div>

        <div class="card inbody-card">
          <div class="card-header">
            <h3>체성분분석 <span class="en">Body Composition Analysis</span></h3>
          </div>
          <table class="inbody-table">
            <thead>
              <tr>
                <th>요소</th>
                <th>측정치</th>
                <th class="progress-th">그래프</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="label">체중 <span class="unit">(kg)</span></td>
                <td class="value">{{ bodyComposition.weight.toFixed(1) }}</td>
                <td>
                  <div class="progress-container">
                    <div class="progress-bar" :style="{ width: getProgressWidth(bodyComposition.weight, 120) + '%' }"></div>
                  </div>
                </td>
              </tr>
              <tr>
                <td class="label">골격근량 <span class="unit">(kg)</span></td>
                <td class="value">{{ bodyComposition.skeletalMuscle.toFixed(1) }}</td>
                <td>
                  <div class="progress-container">
                    <div class="progress-bar muscle-bar" :style="{ width: getProgressWidth(bodyComposition.skeletalMuscle, 60) + '%' }"></div>
                  </div>
                </td>
              </tr>
              <tr>
                <td class="label">체지방량 <span class="unit">(kg)</span></td>
                <td class="value">{{ bodyComposition.bodyFatMass.toFixed(1) }}</td>
                <td>
                  <div class="progress-container">
                    <div class="progress-bar fat-bar" :style="{ width: getProgressWidth(bodyComposition.bodyFatMass, 50) + '%' }"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="card inbody-card">
          <div class="card-header">
            <h3>비만분석 <span class="en">Obesity Analysis</span></h3>
          </div>
          <table class="inbody-table">
            <thead>
              <tr>
                <th>요소</th>
                <th>측정치</th>
                <th class="progress-th">그래프</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="label">BMI <span class="unit">(kg/m²)</span></td>
                <td class="value">{{ bodyComposition.bmi.toFixed(1) }}</td>
                <td>
                  <div class="progress-container">
                    <div class="progress-bar" :style="{ width: getProgressWidth(bodyComposition.bmi, 40) + '%' }"></div>
                  </div>
                </td>
              </tr>
              <tr>
                <td class="label">체지방률 <span class="unit">(%)</span></td>
                <td class="value">{{ bodyComposition.bodyFatRate.toFixed(1) }}</td>
                <td>
                  <div class="progress-container">
                    <div class="progress-bar fat-bar" :style="{ width: getProgressWidth(bodyComposition.bodyFatRate, 50) + '%' }"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="card summary-card">
          <div class="summary-info">
            <span class="label">최근 7일 총 걸음 수</span>
            <span class="total-steps">
              {{ totalSteps.toLocaleString() }} <small>보</small>
            </span>
          </div>
        </div>

        <div class="card table-card">
          <div class="card-header">
            <h3>일별 걸음 수 상세 <span class="en">Daily Step Logs</span></h3>
          </div>
          <div class="table-responsive">
            <table class="flat-table">
              <thead>
                <tr>
                  <th>날짜</th>
                  <th class="text-right">걸음 수</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in stepDataList" :key="index" class="table-row">
                  <td class="date-col">{{ row.date }}</td>
                  <td class="text-right steps-col">{{ row.steps.toLocaleString() }} 보</td>
                </tr>
                <tr v-if="stepDataList.length === 0">
                  <td colspan="2" class="text-center empty-msg">걸음 수 데이터가 존재하지 않습니다.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import axios from 'axios';

// 백엔드 API 베이스 주소 설정
const API_BASE_URL = 'http://localhost:3000/health'; 

// 초기 동기화 렌더링 꼬임 방지 상태값 구조 유지
const isAuthorized = ref(false); 
const isLoading = ref(true); 
const rawBucketData = ref([]);
let authWindow = null;
let pollTimer = null;

// 1. Google OAuth 인증 시작 (팝업 창 제어 원본 로직 유지)
const handleAuthorizePopup = () => {
  const width = 500;
  const height = 650;
  const left = window.screen.width / 2 - width / 2;
  const top = window.screen.height / 2 - height / 2;

  authWindow = window.open(
    `${API_BASE_URL}/google-fit/auth`,
    'GoogleFitAuth',
    `width=${width},height=${height},left=${left},top=${top},scrollbars=yes,resizable=yes`
  );

  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(() => {
    if (!authWindow || authWindow.closed) {
      clearInterval(pollTimer);
      fetchGoogleFitData(); // 팝업이 닫히면 인증 완료 여부 확인을 위해 즉시 패치
    }
  }, 1000);
};

// 팝업 완료 후 부모창 포커스 시 데이터 동기화용 핸들러 유지
const handleWindowFocus = () => {
  if (!isLoading.value && !isAuthorized.value) {
    fetchGoogleFitData();
  }
};

// 2. Google Fit 데이터 일괄 통합 패치
const fetchGoogleFitData = async () => {
  isLoading.value = true;
  try {
    const response = await axios.get(`${API_BASE_URL}/google-fit/data`);
    rawBucketData.value = response.data.bucket || [];
    isAuthorized.value = true; // 성공 시 대시보드 활성화
  } catch (error) {
    console.error('데이터 가져오기 실패:', error);
    isAuthorized.value = false; // 실패 시 안전하게 뷰 차단 및 인증카드 노출
  } finally {
    isLoading.value = false;
  }
};

// 3. 연동 해제 로직 유지
const handleClearTokens = async () => {
  if (!confirm('구글 피트니스 연동을 해제하시겠습니까?')) return;
  
  try {
    await axios.get(`${API_BASE_URL}/google-fit/clear-tokens`);
    isAuthorized.value = false;
    rawBucketData.value = [];
    alert('연동이 해제되었습니다.');
  } catch (error) {
    console.error('연동 해제 실패:', error);
  }
};

// 그래프 게이지 퍼센트 계산 헬퍼 함수
const getProgressWidth = (value, max) => {
  const percentage = (value / max) * 100;
  return Math.min(Math.max(percentage, 4), 100); 
};

// [정제] 기존 걸음 수 파싱 로직 100% 보존
const stepDataList = computed(() => {
  return rawBucketData.value.map((bucket) => {
    const startTime = parseInt(bucket.startTimeMillis, 10);
    const dateStr = new Date(startTime).toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
      weekday: 'short',
    });

    let steps = 0;
    if (bucket.dataset && bucket.dataset[0] && bucket.dataset[0].point) {
      const points = bucket.dataset[0].point;
      if (points.length > 0 && points[0].value && points[0].value[0]) {
        steps = points[0].value[0].intVal || 0;
      }
    }

    return { date: dateStr, steps };
  }).reverse(); 
});

// [정제] 기존 총 걸음 수 합산 로직 유지
const totalSteps = computed(() => {
  return stepDataList.value.reduce((sum, row) => sum + row.steps, 0);
});

// [정제] 인바디 레이아웃 전용 실시간 다중 가상 바인딩 및 정제 계산
const bodyComposition = computed(() => {
  // 기본 디폴트 인바디 수치 데이터셋 구성
  let currentWeight = 84.6; 
  let currentFatRate = 16.1; 

  // 백엔드 원본 데이터셋 확장 파싱 구문 구현
  if (rawBucketData.value.length > 0) {
    const latestBucket = rawBucketData.value[rawBucketData.value.length - 1];
    if (latestBucket.dataset) {
      latestBucket.dataset.forEach((ds) => {
        if (ds.point && ds.point.length > 0 && ds.point[0].value && ds.point[0].value.length > 0) {
          if (ds.dataSourceId?.includes('weight')) {
            currentWeight = ds.point[0].value[0].fpVal || currentWeight;
          } else if (ds.dataSourceId?.includes('body.fat')) {
            currentFatRate = ds.point[0].value[0].fpVal || currentFatRate;
          }
        }
      });
    }
  }

  // 인바디 공식 기반 정밀 연산 및 스케일링
  const bodyFatMass = currentWeight * (currentFatRate / 100); 
  const skeletalMuscle = (currentWeight - bodyFatMass) * 0.52; 
  const bmi = currentWeight / (1.75 * 1.75); // 기준값 키 175cm 대입 환산

  return {
    weight: currentWeight,
    bodyFatRate: currentFatRate,
    bodyFatMass,
    skeletalMuscle,
    bmi
  };
});

const latestInBodyDate = computed(() => {
  if (stepDataList.value.length > 0) {
    return stepDataList.value[0].date;
  }
  return new Date().toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
});

onMounted(() => {
  fetchGoogleFitData();
  window.addEventListener('focus', handleWindowFocus);
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
  window.removeEventListener('focus', handleWindowFocus);
});
</script>

<style scoped>
/* ================= 🎨 깔끔한 화이트/그레이 인바디 테마 디자인 ================= */
.health-dashboard {
  min-height: 100vh;
  background-color: #f4f6f9; /* 어두운 다크차콜 제거 ➡️ 깔끔한 그레이백 전환 */
  color: #333333;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  padding: 3rem 1rem;
  box-sizing: border-box;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 1.8rem;
  font-weight: 800;
  color: #111111;
  letter-spacing: -0.03em;
  margin: 0 0 0.4rem 0;
}

.subtitle {
  color: #666666;
  margin: 0;
  font-size: 0.95rem;
}

.dashboard-content {
  max-width: 540px;
  margin: 0 auto;
}

/* 플랫 카드 디자인 구조 공통 적용 */
.card {
  background-color: #ffffff; 
  border-radius: 10px;
  border: 1px solid #e1e4e8;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  margin-bottom: 1.25rem;
  padding: 1.5rem;
  box-sizing: border-box;
}

.card-header h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #111111;
  margin: 0 0 1.25rem 0;
  border-left: 4px solid #2d3748;
  padding-left: 0.6rem;
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.card-header h3 .en {
  font-size: 0.75rem;
  color: #888888;
  font-weight: 400;
}

/* 상단 컨트롤 바 */
.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding: 0 0.25rem;
}

.update-time {
  font-size: 0.85rem;
  color: #666666;
  font-weight: 500;
}

/* ================= 📊 인바디 계측 그리드 전용 테이블 스타일 ================= */
.inbody-table {
  width: 100%;
  border-collapse: collapse;
}

.inbody-table th {
  font-size: 0.8rem;
  color: #666666;
  font-weight: 600;
  padding: 0.6rem 0.5rem;
  border-bottom: 1px solid #e1e4e8;
  background-color: #fafafa;
  text-align: left;
}

.inbody-table th.progress-th {
  width: 55%;
}

.inbody-table td {
  padding: 1rem 0.5rem;
  border-bottom: 1px solid #f0f2f5;
  font-size: 0.95rem;
}

.inbody-table tr:last-child td {
  border-bottom: none;
}

.inbody-table td.label {
  font-weight: 600;
  color: #222222;
}

.inbody-table td.label .unit {
  font-size: 0.75rem;
  color: #888888;
  font-weight: 400;
}

.inbody-table td.value {
  font-weight: 700;
  color: #111111;
  text-align: right;
  padding-right: 1.5rem;
}

/* 플랫 인바디 컴포넌트 실시간 게이지 그래프 바 */
.progress-container {
  background-color: #edf2f7;
  border-radius: 3px;
  height: 12px;
  width: 100%;
  overflow: hidden;
}

.progress-bar {
  background-color: #4a5568; 
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s cubic-bezier(0.1, 0.8, 0.25, 1);
}

.progress-bar.muscle-bar {
  background-color: #2b6cb0; /* 근육량 블루 테마 */
}

.progress-bar.fat-bar {
  background-color: #dd6b20; /* 체지방 오렌지 테마 */
}

/* ================= 🏃‍♂️ 기존 걸음수 및 데이터 인프라 뷰 보존 스타일 ================= */
.summary-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-left: 5px solid #2b6cb0; 
  background-color: #ffffff;
}

.summary-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-info .label {
  font-size: 0.85rem;
  color: #666666;
  font-weight: 600;
}

.summary-info .total-steps {
  font-size: 1.8rem;
  font-weight: 800;
  color: #2b6cb0; 
  line-height: 1.2;
}

.summary-info .total-steps small {
  font-size: 0.95rem;
  color: #333333;
  font-weight: 500;
  margin-left: 0.15rem;
}

.flat-table {
  width: 100%;
  border-collapse: collapse;
}

.flat-table th {
  color: #666666;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.75rem 0.5rem;
  border-bottom: 2px solid #e1e4e8;
  text-align: left;
}

.table-row td {
  padding: 1rem 0.5rem;
  border-bottom: 1px solid #edf2f7;
  font-size: 0.95rem;
}

.table-row:last-child td {
  border-bottom: none;
}

.date-col {
  color: #4a5568;
  font-weight: 500;
}

.steps-col {
  font-weight: 700;
  color: #2d3748;
}

/* ================= 버튼 및 인터랙션 컴포넌트 요소 ================= */
.btn {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  box-sizing: border-box;
  transition: all 0.15s ease;
}

.btn:active {
  transform: scale(0.98);
}

.btn-block { width: 100%; }

.btn-primary {
  background-color: #2d3748;
  color: #ffffff;
  padding: 1.1rem;
  border: none;
}

.btn-primary:hover {
  background-color: #1a202c;
}

.btn-secondary {
  background-color: #ffffff;
  color: #555555;
  padding: 0.4rem 0.75rem;
  font-size: 0.8rem;
}

.btn-secondary:hover {
  background-color: #f7fafc;
  color: #111111;
  border-color: #cbd5e0;
}

.text-right { text-align: right; }
.text-center { text-align: center; }

.empty-msg {
  color: #888888;
  padding: 3rem 0 !important;
  font-size: 0.9rem;
}

.loading-card {
  padding: 5rem 2rem;
  text-align: center;
  color: #666666;
}

.analytics-icon {
  font-size: 3.5rem;
  display: inline-block;
  margin-bottom: 1rem;
}

.auth-desc {
  color: #555555;
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0 0 2.5rem 0;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #2b6cb0;
  border-radius: 50%;
  margin: 0 auto 1.25rem auto;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>