<script setup>
import AppIcon from './AppIcon.vue'
import StatusBadge from './StatusBadge.vue'
import { dateLabel, dueState } from '../utils/pipeline'
defineProps({ rows: Array, count: Number })
defineEmits(['open'])
</script>
<template>
  <section class="panel work-queue" aria-label="Tindak lanjut hari ini">
    <div class="panel-heading">
      <div>
        <h2>
          Perlu ditindaklanjuti <span class="count-badge">{{ count }}</span>
        </h2>
      </div>
      <RouterLink to="/pipeline?followup=1" class="text-button"
        >Lihat semua <AppIcon name="arrow" :size="16"
      /></RouterLink>
    </div>
    <div v-if="!count" class="queue-empty">
      <span class="metric-icon"><AppIcon name="success" :size="19" /></span>
      <div>
        <strong>Semua tindak lanjut terpantau</strong>
        <p>Belum ada jadwal yang jatuh tempo. Anda bisa melanjutkan peluang aktif.</p>
      </div>
      <RouterLink to="/pipeline" class="text-button">Buka Pipeline</RouterLink>
    </div>
    <article v-for="row in rows" :key="row.id" class="queue-row">
      <div class="queue-customer">
        <strong>{{ row.customer }}</strong>
        <p>{{ row.pic }} · {{ row.product }}</p>
      </div>
      <StatusBadge :status="row.status" />
      <div class="queue-due" :class="dueState(row)">
        <strong>{{ dueState(row) === 'overdue' ? 'Terlambat' : 'Hari ini' }}</strong
        ><span>{{ dateLabel(row.followUpDate) }}</span>
      </div>
      <button
        type="button"
        class="button secondary"
        :aria-label="'Tindak lanjut ' + row.customer"
        @click="$emit('open', row.id)"
      >
        <AppIcon name="edit" :size="16" />Catat tindak lanjut
      </button>
    </article>
  </section>
</template>
