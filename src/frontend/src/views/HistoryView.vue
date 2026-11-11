<script setup>
import { ref } from 'vue'
import OpportunityList from '../components/OpportunityList.vue'
import OpportunityDrawer from '../components/OpportunityDrawer.vue'
import { usePipeline } from '../composables/usePipeline'
const { closedRows } = usePipeline()
const selected = ref(null)
</script>
<template>
  <div class="page-heading">
    <div>
      <h1>Riwayat closing</h1>
    </div>
    <RouterLink to="/pipeline" class="button secondary">Kembali ke Pipeline</RouterLink>
  </div>
  <section class="panel pipeline-panel">
    <div class="panel-heading">
      <div>
        <h2>
          Hasil peluang <span class="count-badge">{{ closedRows.length }}</span>
        </h2>
      </div>
    </div>
    <OpportunityList :rows="closedRows" history @select="selected = $event" />
  </section>
  <OpportunityDrawer v-if="selected !== null" :id="selected" @close="selected = null" />
</template>
