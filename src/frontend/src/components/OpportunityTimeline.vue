<script setup>
import { ref, watch } from 'vue'
import { api } from '../services/api'
import { money, timeLabel, dateLabel } from '../utils/pipeline'
const props = defineProps({ id: { type: String, required: true }, version: Number })
const events = ref([])
const loading = ref(false)
const error = ref('')
let sequence = 0
const labels = {
  created: 'Peluang dicatat',
  updated: 'Peluang diperbarui',
  follow_up_completed: 'Tindak lanjut selesai',
  closed_won: 'Closing Won',
  closed_lost: 'Closing Lost',
}
const fields = {
  customer_name: 'Nasabah',
  interest_status: 'Status',
  pic_id: 'PIC',
  product_id: 'Produk',
  nominal: 'Nominal peluang',
  notes: 'Catatan',
  follow_up_date: 'Jadwal tindak lanjut',
  follow_up_completed: 'Tindak lanjut selesai',
  outcome: 'Hasil',
  realization: 'Realisasi',
  closed_date: 'Tanggal closing',
  lost_reason: 'Alasan Lost',
  segment: 'Segmentasi',
  recorded_date: 'Tanggal pencatatan',
}
function format(key, value, event, side) {
  if (value === null || value === undefined || value === '') return 'Belum diisi'
  if (key === 'nominal' || key === 'realization') return money(Number(value))
  if (key.endsWith('_date')) return dateLabel(value)
  if (key === 'follow_up_completed') return value ? 'Ya' : 'Belum'
  if (key === 'pic_id') return event[side]?.pic?.name || `PIC #${value}`
  if (key === 'product_id') return event[side]?.product?.name || `Produk #${value}`
  return String(value)
}
function changes(event) {
  const before = event.before_data || {}
  const after = event.after_data || {}
  return Object.keys(fields)
    .filter((key) => String(before[key] ?? '') !== String(after[key] ?? ''))
    .map((key) => ({
      key,
      label: fields[key],
      before: format(key, before[key], event, 'before_data'),
      after: format(key, after[key], event, 'after_data'),
    }))
}
async function load() {
  const request = ++sequence
  loading.value = true
  error.value = ''
  events.value = []
  try {
    const detail = await api(`/opportunities/${props.id}`)
    if (request === sequence) events.value = detail.timeline || []
  } catch (e) {
    if (request === sequence) error.value = e.message
  } finally {
    if (request === sequence) loading.value = false
  }
}
watch(() => [props.id, props.version], load, { immediate: true })
</script>
<template>
  <section class="opportunity-timeline" aria-label="Riwayat perkembangan">
    <h3>Riwayat perkembangan</h3>
    <p v-if="loading" role="status">Memuat riwayat...</p>
    <div v-else-if="error" class="notice error" role="alert">
      {{ error }} <button type="button" class="text-button" @click="load">Coba lagi</button>
    </div>
    <p v-else-if="!events.length">Belum ada riwayat perubahan yang tercatat.</p>
    <ol v-else>
      <li v-for="event in events" :key="event.id">
        <strong>{{ labels[event.action] || event.action }}</strong>
        <p class="event-meta">
          {{ timeLabel(event.occurred_at) }} · {{ event.actor?.name || 'Pengguna tidak tersedia' }}
        </p>
        <details v-if="changes(event).length">
          <summary>Lihat {{ changes(event).length }} perubahan</summary>
          <dl>
            <div v-for="change in changes(event)" :key="change.key">
              <dt>{{ change.label }}</dt>
              <dd>
                <span v-if="event.before_data">{{ change.before }} → </span>{{ change.after }}
              </dd>
            </div>
          </dl>
        </details>
      </li>
    </ol>
  </section>
</template>
<style scoped>
.opportunity-timeline {
  margin-top: 24px;
  border-top: 1px solid #e9e5f0;
  padding-top: 20px;
}
ol {
  list-style: none;
  padding: 0;
}
li {
  border-left: 2px solid #ddd4f2;
  padding: 0 0 20px 16px;
}
.event-meta {
  color: #747083;
  font-size: 12px;
  margin: 6px 0 12px;
}
summary {
  cursor: pointer;
  color: #70529c;
  font-size: 13px;
  padding: 6px 0;
}
dl {
  margin: 0;
}
dl > div {
  margin: 8px 0;
}
dt {
  font-size: 12px;
  color: #747083;
}
dd {
  margin: 3px 0 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
</style>
