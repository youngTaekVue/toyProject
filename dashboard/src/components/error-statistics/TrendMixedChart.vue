<template>
  <v-card class="table-card chart-card-fixed pa-5" elevation="0">
    <div class="mb-1">
      <span class="table-card-title block">에러 발생 트렌드 분석</span>
      <p class="text-caption text-grey-darken-1 mb-0 mt-0.5">에러 건수(막대)와 요양기관 수(선)의 연동 추이 모니터링</p>
    </div>
    <div class="chart-container-inner">
      <apexchart type="line" height="260" :options="options" :series="series"></apexchart>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import VueApexCharts from 'vue3-apexcharts';
const apexchart = VueApexCharts;

defineProps<{
  options: any;
  series: any[];
}>();
</script>
