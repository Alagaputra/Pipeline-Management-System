<script setup>
import AppIcon from './AppIcon.vue'
import StatusBadge from './StatusBadge.vue'
import { dateLabel, dueState, compactMoney, isClosed } from '../utils/pipeline'
defineProps({ rows: Array, history: Boolean })
defineEmits(['select'])
const labels = { overdue: 'Terlambat', today: 'Hari ini', upcoming: 'Terjadwal' }
</script>
<template>
  <div class="table-scroll">
    <table>
      <thead>
        <tr>
          <th>{{ history ? 'Tanggal closing' : 'Tanggal' }}</th>
          <th>PIC</th>
          <th>Nasabah / Produk</th>
          <th v-if="!history">Segmentasi</th>
          <th class="number">Nominal peluang</th>
          <th v-if="history" class="number">Realisasi</th>
          <th>{{ history ? 'Hasil' : 'Status' }}</th>
          <th v-if="!history">Tindak lanjut</th>
          <th v-if="!history">Catatan</th>
          <th><span class="sr-only">Detail</span></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.id">
          <td class="date-cell">{{ dateLabel(history ? row.closedDate : row.date) }}</td>
          <td>
            <span class="pic-cell"
              ><span class="avatar tiny" :class="row.pic.toLowerCase()">{{ row.pic[0] }}</span
              >{{ row.pic }}</span
            >
          </td>
          <td>
            <button class="customer-link" @click="$emit('select', row.id)">
              {{ row.customer }}</button
            ><small class="cell-subtitle">{{ row.product }} · {{ row.division }}</small>
          </td>
          <td v-if="!history">{{ row.segment }}</td>
          <td class="number nominal">{{ compactMoney(row.nominal) }}</td>
          <td v-if="history" class="number nominal">{{ compactMoney(row.realization) }}</td>
          <td><StatusBadge :status="isClosed(row) ? row.outcome : row.status" /></td>
          <td v-if="!history">
            <span v-if="row.completed" class="due-label completed">Selesai</span
            ><span v-else-if="dueState(row)" class="due-label" :class="dueState(row)">{{
              labels[dueState(row)]
            }}</span
            ><span v-else class="muted">—</span
            ><small v-if="row.followUpDate" class="cell-subtitle">{{
              dateLabel(row.followUpDate)
            }}</small>
          </td>
          <td v-if="!history" class="cell-note" :title="row.notes || ''">{{ row.notes || '—' }}</td>
          <td>
            <button
              class="icon-button"
              :aria-label="`Detail ${row.customer} ${row.id}`"
              @click="$emit('select', row.id)"
            >
              <AppIcon name="right" :size="17" />
            </button>
          </td>
        </tr>
        <tr v-if="!rows.length">
          <td :colspan="history ? 8 : 9">
            <div class="empty-state">
              <AppIcon name="search" :size="30" />
              <h3>
                {{ history ? 'Belum ada closing yang sesuai' : 'Peluang tidak ditemukan' }}
              </h3>
              <p>
                {{
                  history
                    ? 'Peluang Won/Lost akan tersimpan di sini. Periksa filter jika data tidak terlihat.'
                    : 'Ubah pencarian atau filter, atau catat peluang baru.'
                }}
              </p>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
