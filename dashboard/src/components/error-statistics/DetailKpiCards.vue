<template>
  <div class="kpi-cards-container" v-if="targetSummary">
    <!-- 1) 총 청구오류 건수 -->
    <div class="premium-card">
      <div class="card-left">
        <span class="card-title-text">총 청구오류 건수</span>
        <div class="d-flex align-end mt-2">
          <span class="card-value-text text-blue">{{ formatNumber(targetSummary.count) }}</span>
          <span class="caption text-grey ml-1.5 pb-0.5 font-weight-medium">건</span>
        </div>
      </div>
      <div class="card-right icon-box-blue">
        <v-icon size="small" color="white">mdi-alert-circle-outline</v-icon>
      </div>
    </div>

    <!-- 2) 회신대기 건수 -->
    <div class="premium-card">
      <div class="card-left">
        <span class="card-title-text">회신대기 건수</span>
        <div class="d-flex align-end mt-2">
          <span class="card-value-text text-orange">{{ formatNumber(targetSummary.sentCount) }}</span>
          <span class="caption text-grey ml-1.5 pb-0.5 font-weight-medium">건</span>
        </div>
      </div>
      <div class="card-right icon-box-orange">
        <v-icon size="small" color="white">mdi-message-text-outline</v-icon>
      </div>
    </div>

    <!-- 3) 최종완료 건수 -->
    <div class="premium-card">
      <div class="card-left">
        <span class="card-title-text">최종완료 건수</span>
        <div class="d-flex align-end mt-2">
          <span class="card-value-text text-green">{{ formatNumber(targetSummary.confirmedCount) }}</span>
          <span class="caption text-grey ml-1.5 pb-0.5 font-weight-medium">건</span>
        </div>
      </div>
      <div class="card-right icon-box-green">
        <v-icon size="small" color="white">mdi-shield-check-outline</v-icon>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  targetSummary: {
    count: number;
    sentCount: number;
    confirmedCount: number;
  } | null;
}>();

function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num || 0);
}
</script>

<style scoped>
.kpi-cards-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  width: 100%;
}

.premium-card {
  width: 100%;
  background: #ffffff;
  border-radius: 9px;
  border: 1px solid #cbd5e1;
  padding: 16px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 94px;
  box-shadow: 0 4px 18px -4px rgba(0, 0, 0, 0.03), 0 1px 3px rgba(0, 0, 0, 0.01);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.premium-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 20px -8px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.01);
}

.card-left {
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow: hidden;
}

.card-title-text {
  font-size: 11.5px;
  font-weight: 700;
  color: #64748b;
  letter-spacing: -0.1px;
  margin-bottom: 4px;
}

.card-value-text {
  font-size: 21px;
  font-weight: 800;
  line-height: 1.1;
}

.text-blue { color: #2563eb !important; }
.text-orange { color: #ea580c !important; }
.text-green { color: #16a34a !important; }

.card-right {
  width: 44px;
  height: 44px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-box-blue {
  background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%);
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.15);
}

.icon-box-orange {
  background: linear-gradient(135deg, #fb923c 0%, #ea580c 100%);
  box-shadow: 0 4px 10px rgba(234, 88, 12, 0.15);
}

.icon-box-green {
  background: linear-gradient(135deg, #4ade80 0%, #16a34a 100%);
  box-shadow: 0 4px 10px rgba(22, 163, 74, 0.15);
}

@media (max-width: 960px) {
  .kpi-cards-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}

@media (max-width: 600px) {
  .kpi-cards-container {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>
