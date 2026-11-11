<script setup>
import { computed, reactive, ref } from 'vue'
import { confirmAction } from '../composables/useConfirm'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import { UNIT_PRODUCTS } from '../data/access'
import { percent } from '../utils/pipeline'
import { usePipeline } from '../composables/usePipeline'
import TargetCard from './TargetCard.vue'
import TargetCardGrid from './TargetCardGrid.vue'
import AppDrawer from './AppDrawer.vue'
defineProps({ readOnly: { type: Boolean, default: false } })
const {
  selectedYear,
  division,
  divisionLabel,
  canEdit,
  isHead,
  getUnitTarget,
  saveUnitTarget,
  refresh,
  storageError,
  loading,
} = usePipeline()
const months = [
  'Januari',
  'Februari',
  'Maret',
  'April',
  'Mei',
  'Juni',
  'Juli',
  'Agustus',
  'September',
  'Oktober',
  'November',
  'Desember',
]
const month = ref(new Date().getMonth() + 1)
const unit = (value) => new Intl.NumberFormat('id-ID').format(value) + ' unit'
const percentage = (actual, target) => (target > 0 ? (actual / target) * 100 : null)
const entries = computed(() =>
  UNIT_PRODUCTS.filter((product) => division.value !== 'Komersil' || product === 'CMS').map(
    (product) => {
      const entry = getUnitTarget(product, selectedYear.value)
      const realization = Object.values(entry.monthly).reduce(
        (sum, item) => sum + item.realization,
        0,
      )
      const monthly = entry.monthly[month.value] || { target: 0, realization: 0 }
      return {
        product,
        ...entry,
        realization,
        monthly,
        percentage: percentage(realization, entry.target),
      }
    },
  ),
)
const editing = ref(''),
  error = ref(''),
  success = ref('')
const saving = ref(false)
const uncertain = ref(false)
const conflict = ref(false)
const requestKey = ref(crypto.randomUUID())
const draft = reactive({ target: 0, monthly: {} })
let baseline = ''
useUnsavedChanges(
  computed(() => Boolean(editing.value) && (uncertain.value || JSON.stringify(draft) !== baseline)),
  saving,
)
function edit(product) {
  if (loading.value) return
  requestKey.value = crypto.randomUUID()
  uncertain.value = false
  conflict.value = false
  const entry = getUnitTarget(product, selectedYear.value)
  draft.target = entry.target
  draft.monthly = Object.fromEntries(
    months.map((_, i) => [i + 1, { target: 0, realization: 0, ...entry.monthly[i + 1] }]),
  )
  baseline = JSON.stringify(draft)
  editing.value = product
  error.value = ''
}
async function close() {
  if (saving.value) return
  if ((!uncertain.value && JSON.stringify(draft) === baseline) || (await confirmAction()))
    editing.value = ''
}
async function reloadConflict() {
  if (
    !(await confirmAction({
      title: 'Muat data terbaru?',
      message: 'Isian saat ini akan diganti dengan data terbaru.',
      confirmLabel: 'Muat data terbaru',
    }))
  )
    return
  await refresh()
  if (storageError.value) {
    error.value = storageError.value
    return
  }
  edit(editing.value)
}
async function save() {
  if (saving.value) return
  saving.value = true
  error.value = ''
  try {
    const entry = {
      target: Number(draft.target),
      monthly: Object.fromEntries(
        Object.entries(draft.monthly).map(([m, item]) => [
          m,
          { target: Number(item.target), realization: Number(item.realization) },
        ]),
      ),
    }
    const previous = getUnitTarget(editing.value, selectedYear.value)
    const changed = Object.keys(entry.monthly)
      .map(Number)
      .filter((m) =>
        ['target', 'realization'].some(
          (key) => entry.monthly[m][key] !== (previous.monthly[m]?.[key] || 0),
        ),
      )
    await saveUnitTarget(editing.value, selectedYear.value, entry, { requestKey: requestKey.value })
    if (changed.length && !changed.includes(month.value)) month.value = changed[0]
    success.value = editing.value + ' tahun ' + selectedYear.value + ' berhasil disimpan.'
    editing.value = ''
  } catch (e) {
    error.value = e.message
    uncertain.value = Boolean(e.uncertain)
    conflict.value = e.status === 409
  } finally {
    saving.value = false
  }
}
</script>
<template>
  <section class="panel unit-target-panel" aria-label="Target layanan dalam unit">
    <div class="panel-heading">
      <div>
        <h2>Target layanan {{ selectedYear }}</h2>
      </div>
      <div class="unit-heading-actions">
        <label
          >Bulan<select v-model.number="month" aria-label="Bulan target unit">
            <option v-for="(name, i) in months" :key="name" :value="i + 1">{{ name }}</option>
          </select></label
        >
        <RouterLink v-if="readOnly" to="/target" class="text-button"
          >Kelola target layanan</RouterLink
        >
      </div>
    </div>
    <p v-if="success" class="notice success" role="status">{{ success }}</p>
    <TargetCardGrid class="unit-cards">
      <TargetCard
        v-for="entry in entries"
        :key="entry.product"
        :item="entry"
        unit
        :label="'Target unit ' + entry.product"
        :badge="entry.product === 'CMS' ? 'Bersama' : 'Per divisi'"
      >
        <dl class="service-month-values unit-month-values">
          <div>
            <dt>Target {{ months[month - 1] }}</dt>
            <dd>{{ unit(entry.monthly.target) }}</dd>
          </div>
          <div>
            <dt>Realisasi {{ months[month - 1] }}</dt>
            <dd>{{ unit(entry.monthly.realization) }}</dd>
          </div>
        </dl>
        <p class="service-month-percentage">
          Pencapaian bulan:
          {{ percent(percentage(entry.monthly.realization, entry.monthly.target)) }}
        </p>
        <template #actions v-if="!readOnly">
          <button
            v-if="entry.product === 'CMS' ? canEdit || isHead : canEdit"
            class="button secondary service-edit"
            :disabled="loading"
            @click="edit(entry.product)"
          >
            Atur {{ entry.product }}
          </button>
          <p v-else class="service-permission">Pilih satu divisi untuk mengatur target.</p>
        </template>
      </TargetCard>
    </TargetCardGrid>
  </section>
  <AppDrawer
    v-if="!readOnly && editing"
    :title="'Atur ' + editing"
    :subtitle="selectedYear + ' · ' + (editing === 'CMS' ? 'BERSAMA KEDUA DIVISI' : divisionLabel)"
    @close="close"
  >
    <form :aria-busy="saving" @submit.prevent="save">
      <fieldset class="form-fields" :disabled="saving || uncertain">
        <label class="unit-annual-input"
          >Target tahunan {{ editing }} (unit)<input
            v-model="draft.target"
            type="number"
            min="0"
            max="9007199254740991"
            step="1"
            required
        /></label>
        <div class="month-form-scroll">
          <table class="month-form-table">
            <thead>
              <tr>
                <th>Bulan</th>
                <th>Target (unit)</th>
                <th>Realisasi (unit)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(name, i) in months" :key="name">
                <td>{{ name }}</td>
                <td>
                  <input
                    v-model="draft.monthly[i + 1].target"
                    :aria-label="'Target ' + editing + ' ' + name + ' (unit)'"
                    type="number"
                    min="0"
                    max="9007199254740991"
                    step="1"
                    required
                  />
                </td>
                <td>
                  <input
                    v-model="draft.monthly[i + 1].realization"
                    :aria-label="'Realisasi ' + editing + ' ' + name + ' (unit)'"
                    type="number"
                    min="0"
                    max="9007199254740991"
                    step="1"
                    required
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </fieldset>
      <p v-if="error" class="notice error" role="alert">
        {{ error }}
        <button v-if="conflict" type="button" class="text-button" @click="reloadConflict">
          Muat data terbaru
        </button>
      </p>
      <div class="form-actions">
        <button type="button" class="button secondary" :disabled="saving" @click="close">
          Batal</button
        ><button class="button primary" :disabled="saving">
          {{ saving ? 'Menyimpan...' : uncertain ? 'Coba lagi' : 'Simpan target unit' }}
        </button>
      </div>
    </form>
  </AppDrawer>
</template>
<style scoped>
.unit-cards {
  margin: 0 26px 24px;
}
.unit-heading-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 14px;
}
.unit-heading-actions label {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
}
.service-month-values {
  margin: 0;
  padding: 0;
  border: 0;
}
.service-month-values dt {
  color: #716b80;
  font-size: 12px;
}
.service-month-values dd {
  margin: 5px 0 0;
  font-size: 14px;
}
.service-month-values > div:last-child {
  text-align: right;
}
.service-month-percentage,
.service-permission {
  margin: 12px 0 0;
  font-size: 12px;
  color: #716b80;
  line-height: 1.6;
}
.service-edit {
  width: 100%;
}
@media (max-width: 600px) {
  .unit-target-panel > .panel-heading > div {
    flex-basis: 100%;
  }
  .unit-heading-actions {
    justify-content: space-between;
  }
  .unit-heading-actions label {
    width: 100%;
    justify-content: space-between;
  }
  .unit-heading-actions select {
    flex: 1;
    max-width: 220px;
  }
  .unit-cards {
    margin: 0 18px 18px;
  }
}
</style>
