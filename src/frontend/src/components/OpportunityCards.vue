<script setup>
import StatusBadge from './StatusBadge.vue'
import AppIcon from './AppIcon.vue'
import { compactMoney, money, dateLabel, dueState, isClosed } from '../utils/pipeline'
defineProps({ rows: Array, history: Boolean })
defineEmits(['select'])
const dueLabels = { overdue: 'Terlambat', today: 'Hari ini', upcoming: 'Terjadwal' }
</script>
<template>
  <div class="opportunity-mobile" aria-label="Daftar peluang">
    <article v-for="row in rows" :key="row.id" class="mobile-opportunity">
      <div class="mobile-opportunity-heading">
        <div>
          <button class="customer-link" @click="$emit('select', row.id)">{{ row.customer }}</button>
          <p>{{ row.product }} · {{ row.pic }}</p>
        </div>
        <StatusBadge :status="isClosed(row) ? row.outcome : row.status" />
      </div>
      <dl class="mobile-opportunity-values">
        <div>
          <dt>Nominal peluang</dt>
          <dd :title="money(row.nominal)">{{ compactMoney(row.nominal) }}</dd>
        </div>
        <div v-if="history">
          <dt>Realisasi Won</dt>
          <dd :title="money(row.realization)">{{ compactMoney(row.realization) }}</dd>
        </div>
      </dl>
      <div class="mobile-opportunity-footer">
        <p v-if="history">Closing {{ dateLabel(row.closedDate) }}</p>
        <p v-else :class="dueState(row)">
          <AppIcon name="calendar" :size="15" />{{
            row.completed
              ? 'Tindak lanjut selesai'
              : row.followUpDate
                ? (dueLabels[dueState(row)] || 'Terjadwal') + ' · ' + dateLabel(row.followUpDate)
                : 'Belum ada jadwal tindak lanjut'
          }}
        </p>
        <button
          type="button"
          class="text-button"
          :aria-label="'Detail ' + row.customer + ' ' + row.id"
          @click="$emit('select', row.id)"
        >
          Detail <AppIcon name="right" :size="15" />
        </button>
      </div>
    </article>
    <div v-if="!rows.length" class="empty-state">
      <AppIcon name="search" :size="28" />
      <h3>{{ history ? 'Belum ada hasil yang sesuai' : 'Peluang tidak ditemukan' }}</h3>
      <p>Periksa pencarian atau filter yang sedang digunakan.</p>
    </div>
  </div>
</template>
