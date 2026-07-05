<template>
  <div class="d-flex align-center mt-1 px-1">
    <v-btn
        icon="mdi-arrow-left"
        variant="flat"
        class="back-btn mr-4"
        color="white"
        @click="$emit('back')"
    ></v-btn>
    <div class="header-title-container">
      <div class="d-flex align-center flex-wrap" style="gap: 8px;">
        <span class="type-tag">{{ targetType === 'hospital' ? '요양기관 상세내역' : 'EMR사 상세내역' }}</span>
        <h1 class="target-title">{{ targetName }}</h1>
      </div>
      <div class="d-flex align-center mt-1.5">
        <span class="caption-label">조회 차수:</span>
        <span class="period-badge">
          {{ currentFileKey ? currentFileKey.replace(/_/g, '-') : '전체 기간' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  targetType: string;
  targetName: string;
  currentFileKey: string;
}>();

defineEmits<{
  (e: 'back'): void;
}>();
</script>

<style scoped>
.back-btn {
  border: 1px solid #e2e8f0 !important;
  border-radius: 50% !important;
  width: 40px !important;
  height: 40px !important;
  min-width: 40px !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-btn:hover {
  background-color: #f8fafc !important;
  transform: translateX(-3px);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08) !important;
  border-color: #cbd5e1 !important;
}

.header-title-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  font-family: 'Plus Jakarta Sans', 'Pretendard', sans-serif;
}

.type-tag {
  font-size: 11px;
  font-weight: 700;
  color: #2563eb;
  background-color: #eff6ff;
  padding: 2px 8px;
  border-radius: 6px;
  letter-spacing: -0.2px;
  line-height: 1.2;
}

.target-title {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.5px;
  line-height: 1.2;
}

.caption-label {
  font-size: 11.5px;
  font-weight: 600;
  color: #64748b;
  line-height: 1.2;
}

.period-badge {
  font-size: 11px;
  font-weight: 700;
  color: #334155;
  background-color: #f1f5f9;
  border: 1px solid #e2e8f0;
  padding: 1px 8px;
  border-radius: 4px;
  margin-left: 6px;
  line-height: 1.2;
}
</style>
