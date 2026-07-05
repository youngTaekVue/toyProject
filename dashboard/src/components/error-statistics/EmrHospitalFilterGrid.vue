<template>
  <div v-if="targetType === 'emr' && emrHospitalsSummary.length > 0">
    <div class="text-caption font-weight-bold mb-2.5 text-slate-800 d-flex align-center">
      <v-icon size="x-small" class="mr-1.5" color="primary">mdi-hospital-building</v-icon> EMR 사용 요양기관 필터
    </div>
    <v-row class="g-3 mx-n1.5">
      <v-col cols="12" sm="6" md="3" class="px-1.5 py-1.5">
        <v-card
            :class="['metric-filter-card', selectedHospitalFilter === 'all' ? 'active-card' : '']"
            @click="filterModel = 'all'"
            elevation="0"
        >
          <div class="d-flex flex-column py-3 px-4">
            <span class="filter-card-title">요양기관 전체</span>
            <div class="d-flex align-baseline mt-1 justify-space-between" v-if="targetSummary">
              <span class="filter-card-value">{{ allRowsLength }} 건</span>
              <span class="filter-card-badge bg-blue-light">{{ targetSummary.confirmedCount }} / {{ targetSummary.count }} 완료</span>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3" v-for="h in emrHospitalsSummary" :key="h.hospital" class="px-1.5 py-1.5">
        <v-card
            :class="['metric-filter-card', selectedHospitalFilter === h.hospital ? 'active-card' : '']"
            @click="filterModel = h.hospital"
            elevation="0"
        >
          <div class="d-flex flex-column py-3 px-4">
            <span class="filter-card-title text-truncate" style="max-width: 100%;">{{ h.hospital }}</span>
            <div class="d-flex align-baseline mt-1 justify-space-between">
              <span class="filter-card-value">{{ h.casesCount }} 건</span>
              <span class="filter-card-badge" :class="h.resolutionRate === 100 ? 'bg-green-light' : 'bg-orange-light'">
                {{ h.resolutionRate.toFixed(0) }}% 완료
              </span>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  targetType: string;
  emrHospitalsSummary: any[];
  selectedHospitalFilter: string;
  allRowsLength: number;
  targetSummary: any;
}>();

const emit = defineEmits<{
  (e: 'update:selectedHospitalFilter', filter: string): void;
}>();

const filterModel = computed({
  get: () => props.selectedHospitalFilter,
  set: (val) => emit('update:selectedHospitalFilter', val)
});
</script>

<style scoped>
.metric-filter-card {
  border: 1px solid #cbd5e1 !important;
  border-radius: 9px !important;
  cursor: pointer;
  background-color: #ffffff !important;
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.02) !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.metric-filter-card:hover {
  border-color: #3b82f6 !important;
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
}

.metric-filter-card.active-card {
  border-color: #2563eb !important;
  border-width: 1.5px !important;
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.08) !important;
  background-color: #eff6ff !important;
}

.filter-card-title {
  font-size: 11.5px;
  font-weight: 700;
  color: #64748b;
}

.filter-card-value {
  font-size: 16px;
  font-weight: 800;
  color: #0f172a;
}

.filter-card-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.bg-blue-light {
  background-color: #eff6ff;
  color: #2563eb;
}

.bg-orange-light {
  background-color: #fffbeb;
  color: #d97706;
}

.bg-green-light {
  background-color: #ecfdf5;
  color: #059669;
}
</style>
