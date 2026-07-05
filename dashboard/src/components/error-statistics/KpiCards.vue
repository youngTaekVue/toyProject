<template>
  <div class="kpi-cards-container mb-6">
    <!-- 1) 총 실패 건수 -->
      <div class="premium-card">
        <div class="card-left">
          <span class="card-title-text">총 실패 건수</span>
          <div class="d-flex align-end mt-2">
            <span class="card-value-text">{{ formatNumber(kpiMetrics.rawFailures) }}</span>
            <span v-if="kpiMetrics.hasPrev" class="card-trend-badge" :class="kpiMetrics.failuresTrend > 0 ? 'trend-bad' : kpiMetrics.failuresTrend < 0 ? 'trend-good' : 'trend-neutral'">
              {{ kpiMetrics.failuresTrend > 0 ? '↑' : kpiMetrics.failuresTrend < 0 ? '↓' : '' }} {{ Math.abs(kpiMetrics.failuresTrend).toFixed(1) }}%
            </span>
            <span v-else class="card-trend-badge trend-neutral">최초 차수</span>
          </div>
          <span class="caption text-grey ml-0.5 mt-1 font-weight-medium block" style="font-size: 11px;">
            청구건수: <strong class="text-slate-700">{{ formatNumber(kpiMetrics.failures) }}건</strong>
          </span>
        </div>
        <div class="card-right icon-box-red">
          <v-icon size="small" color="white">mdi-alert-circle-outline</v-icon>
        </div>
      </div>

      <!-- 2) 대상 요양기관 수 -->
      <div class="premium-card">
        <div class="card-left">
          <span class="card-title-text">대상 요양기관 수</span>
          <div class="d-flex align-end mt-2">
            <span class="card-value-text">{{ formatNumber(kpiMetrics.hospitals) }}</span>
            <span v-if="kpiMetrics.hasPrev" class="card-trend-badge" :class="kpiMetrics.hospitalsTrend > 0 ? 'trend-bad' : kpiMetrics.hospitalsTrend < 0 ? 'trend-good' : 'trend-neutral'">
              {{ kpiMetrics.hospitalsTrend > 0 ? '↑' : kpiMetrics.hospitalsTrend < 0 ? '↓' : '' }} {{ Math.abs(kpiMetrics.hospitalsTrend).toFixed(1) }}%
            </span>
            <span v-else class="card-trend-badge trend-neutral">최초 차수</span>
          </div>
          <div class="mt-1" style="height: 16.5px;"></div>
        </div>
        <div class="card-right icon-box-orange">
          <v-icon size="small" color="white">mdi-domain</v-icon>
        </div>
      </div>

      <!-- 3) 조치 대기 건수 -->
      <div class="premium-card">
        <div class="card-left">
          <span class="card-title-text">조치 대기 건수</span>
          <div class="d-flex align-end mt-2">
            <span class="card-value-text">{{ formatNumber(kpiMetrics.rawUnconfirmed) }}</span>
            <span v-if="kpiMetrics.hasPrev" class="card-trend-badge" :class="kpiMetrics.unconfirmedTrend > 0 ? 'trend-bad' : kpiMetrics.unconfirmedTrend < 0 ? 'trend-good' : 'trend-neutral'">
              {{ kpiMetrics.unconfirmedTrend > 0 ? '↑' : kpiMetrics.unconfirmedTrend < 0 ? '↓' : '' }} {{ Math.abs(kpiMetrics.unconfirmedTrend).toFixed(1) }}%
            </span>
            <span v-else class="card-trend-badge trend-neutral">최초 차수</span>
          </div>
          <span class="caption text-grey ml-0.5 mt-1 font-weight-medium block" style="font-size: 11px;">
            청구건수: <strong class="text-slate-700">{{ formatNumber(kpiMetrics.unconfirmed) }}건</strong>
          </span>
        </div>
        <div class="card-right icon-box-purple">
          <v-icon size="small" color="white">mdi-database-plus</v-icon>
        </div>
      </div>

      <!-- 4) 회신 대기 건수 -->
      <div class="premium-card">
        <div class="card-left">
          <span class="card-title-text">회신 대기 건수</span>
          <div class="d-flex align-end mt-2">
            <span class="card-value-text">{{ formatNumber(kpiMetrics.rawPending) }}</span>
            <span v-if="kpiMetrics.hasPrev" class="card-trend-badge" :class="kpiMetrics.pendingTrend > 0 ? 'trend-bad' : kpiMetrics.pendingTrend < 0 ? 'trend-good' : 'trend-neutral'">
              {{ kpiMetrics.pendingTrend > 0 ? '↑' : kpiMetrics.pendingTrend < 0 ? '↓' : '' }} {{ Math.abs(kpiMetrics.pendingTrend).toFixed(1) }}%
            </span>
            <span v-else class="card-trend-badge trend-neutral">최초 차수</span>
          </div>
          <span class="caption text-grey ml-0.5 mt-1 font-weight-medium block" style="font-size: 11px;">
            청구건수: <strong class="text-slate-700">{{ formatNumber(kpiMetrics.pending) }}건</strong>
          </span>
        </div>
        <div class="card-right icon-box-blue">
          <v-icon size="small" color="white">mdi-lightning-bolt</v-icon>
        </div>
      </div>

      <!-- 5) 조치 완료 건수 -->
      <div class="premium-card">
        <div class="card-left">
          <span class="card-title-text">조치 완료 건수</span>
          <div class="d-flex align-end mt-2">
            <span class="card-value-text">{{ formatNumber(kpiMetrics.rawResolved) }}</span>
            <span v-if="kpiMetrics.hasPrev" class="card-trend-badge" :class="kpiMetrics.resolvedTrend > 0 ? 'trend-good' : kpiMetrics.resolvedTrend < 0 ? 'trend-bad' : 'trend-neutral'">
              {{ kpiMetrics.resolvedTrend > 0 ? '↑' : kpiMetrics.resolvedTrend < 0 ? '↓' : '' }} {{ Math.abs(kpiMetrics.resolvedTrend).toFixed(1) }}%
            </span>
            <span v-else class="card-trend-badge trend-neutral">최초 차수</span>
          </div>
          <span class="caption text-grey ml-0.5 mt-1 font-weight-medium block" style="font-size: 11px;">
            청구건수: <strong class="text-slate-700">{{ formatNumber(kpiMetrics.resolved) }}건</strong>
          </span>
        </div>
        <div class="card-right icon-box-green">
          <v-icon size="small" color="white">mdi-shield-check</v-icon>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
interface KpiMetrics {
  rawFailures: number;
  failures: number;
  hospitals: number;
  rawUnconfirmed: number;
  unconfirmed: number;
  rawPending: number;
  pending: number;
  rawResolved: number;
  resolved: number;
  hasPrev: boolean;
  failuresTrend: number;
  hospitalsTrend: number;
  unconfirmedTrend: number;
  pendingTrend: number;
  resolvedTrend: number;
}

defineProps<{
  kpiMetrics: KpiMetrics;
}>();

function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num || 0);
}
</script>

<style scoped>
/* 1. KPI 카드 시스템 */
.kpi-cards-container {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
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
.card-left { display: flex; flex-direction: column; width: 100%; overflow: hidden; }
.card-title-text { font-size: 11.5px; font-weight: 700; color: #64748b; letter-spacing: -0.1px; margin-bottom: 4px; }
.card-value-text { font-size: 21px; font-weight: 800; color: #0f172a; line-height: 1.1; }
.card-trend-badge { font-size: 10.5px; font-weight: 700; padding: 2px 6px; border-radius: 5px; margin-left: 6px; }
.trend-bad { background-color: #fef2f2; color: #ef4444; }
.trend-good { background-color: #f0fdf4; color: #22c55e; }
.trend-neutral { background-color: #f1f5f9; color: #64748b; }
.block { display: block; }

.card-right {
  width: 44px;
  height: 44px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.icon-box-red {
  background: linear-gradient(135deg, #f87171 0%, #dc2626 100%);
  box-shadow: 0 4px 10px rgba(220, 38, 38, 0.15);
}
.icon-box-orange {
  background: linear-gradient(135deg, #fb923c 0%, #ea580c 100%);
  box-shadow: 0 4px 10px rgba(234, 88, 12, 0.15);
}
.icon-box-purple {
  background: linear-gradient(135deg, #c084fc 0%, #9333ea 100%);
  box-shadow: 0 4px 10px rgba(147, 51, 234, 0.15);
}
.icon-box-blue {
  background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%);
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.15);
}
.icon-box-green {
  background: linear-gradient(135deg, #4ade80 0%, #16a34a 100%);
  box-shadow: 0 4px 10px rgba(22, 163, 74, 0.15);
}

@media (max-width: 1400px) {
  .kpi-cards-container {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 960px) {
  .kpi-cards-container {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 600px) {
  .kpi-cards-container {
    grid-template-columns: 1fr;
  }
}

.skeleton-loading {
  pointer-events: none;
}
.skeleton-circle {
  background-color: #f1f5f9 !important;
  box-shadow: none !important;
}
</style>
