<script setup>
import { usePipeline } from '../composables/usePipeline'
const { selectedYear, years } = usePipeline()
defineProps({ label: { type: String, default: 'Tahun target & realisasi' } })
</script>
<template>
  <label class="year-filter"
    >{{ label }}
    <select v-model.number="selectedYear" aria-label="Tahun laporan">
      <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
    </select></label
  >
</template>
