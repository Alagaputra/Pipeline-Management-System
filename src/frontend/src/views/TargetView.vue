<script setup>
import { computed, reactive, ref, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { confirmAction } from '../composables/useConfirm'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import MoneyInput from '../components/MoneyInput.vue'
import AppIcon from '../components/AppIcon.vue'
import YearFilter from '../components/YearFilter.vue'
import AppDrawer from '../components/AppDrawer.vue'
import TargetProgress from '../components/TargetProgress.vue'
import UnitTargets from '../components/UnitTargets.vue'
import { usePipeline } from '../composables/usePipeline'
import { PRODUCTS, moneyInMillions, percent, validateTargets } from '../utils/pipeline'
const {
  dashboard,
  annualTargets,
  selectedYear,
  saveTargets,
  captureTargetDraft,
  products,
  canEdit,
  loading,
  refresh,
  storageError,
} = usePipeline()
const summary = computed(() => dashboard.value?.summary || [])
const route = useRoute()
const router = useRouter()
const formElement = ref(null)
const monthNames = Array.from({ length: 12 }, (_, i) =>
  new Intl.DateTimeFormat('id-ID', { month: 'long' }).format(new Date(2024, i, 1)),
)
const allocationProduct = ref('')
const fieldErrors = ref({})
const editing = ref(false)
const saving = ref(false)
const uncertain = ref(false)
const conflict = ref(false)
const requestKey = ref(crypto.randomUUID())
const error = ref('')
const success = ref('')
const draft = reactive({ year: selectedYear.value, monthly: [], Tabungan: 0, Giro: 0, Deposito: 0 })
// Draft terpisah dari target tersimpan; baseline dipakai untuk mendeteksi perubahan.
let baseline = ''
let targetDraft
useUnsavedChanges(
  computed(() => editing.value && (uncertain.value || JSON.stringify(draft) !== baseline)),
  saving,
)
function edit() {
  targetDraft = captureTargetDraft()
  requestKey.value = crypto.randomUUID()
  uncertain.value = false
  conflict.value = false
  const stored = annualTargets.value[selectedYear.value] || {}
  allocationProduct.value = products.value[0]
  Object.assign(draft, {
    monthly: monthNames.map((_, i) =>
      Object.fromEntries(
        products.value.map((name) => [name, stored.monthly?.[i + 1]?.[name] || 0]),
      ),
    ),
    year: selectedYear.value,
    ...Object.fromEntries(PRODUCTS.map((product) => [product, Number(stored[product]) || 0])),
  })
  baseline = JSON.stringify(draft)
  error.value = ''
  fieldErrors.value = {}
  editing.value = true
}
watch(
  () => [route.query.edit, canEdit.value, loading.value],
  async () => {
    if (route.query.edit !== '1' || !canEdit.value || loading.value) return
    // Tautan dari kartu target menunggu tahun/data siap, lalu membuka dan memfokuskan form.
    const year = Number(route.query.year)
    if (Number.isInteger(year) && year >= 2000 && year <= 2100 && year !== selectedYear.value) {
      selectedYear.value = year
      return
    }
    edit()
    const product = products.value.includes(route.query.product)
      ? route.query.product
      : products.value[0]
    const month = Number(route.query.month)
    const monthly = Number.isInteger(month) && month >= 1 && month <= 12
    if (monthly) allocationProduct.value = product
    const query = { ...route.query }
    delete query.month
    delete query.edit
    delete query.product
    delete query.year
    await router.replace({ query })
    await nextTick()
    formElement.value
      ?.querySelector(monthly ? `[data-target-month="${month}"]` : `[name="${product}"]`)
      ?.focus()
  },
  { immediate: true },
)
async function close() {
  if (saving.value) return
  if ((!uncertain.value && JSON.stringify(draft) === baseline) || (await confirmAction()))
    editing.value = false
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
  selectedYear.value = Number(draft.year)
  await nextTick()
  await refresh()
  if (storageError.value) {
    error.value = storageError.value
    return
  }
  edit()
}
async function save() {
  // Validasi isian, ubah angka, lalu simpan semua target produk lewat satu batch.
  // requestKey tetap dipakai saat hasil belum pasti; konflik memerlukan muat ulang.
  if (saving.value) return
  fieldErrors.value = {}
  if (
    !Number.isInteger(Number(draft.year)) ||
    Number(draft.year) < 2000 ||
    Number(draft.year) > 2100
  )
    fieldErrors.value.year = 'Tahun harus antara 2000 dan 2100.'
  for (const product of products.value) {
    if (
      String(draft[product]).trim() === '' ||
      !Number.isSafeInteger(Number(draft[product])) ||
      Number(draft[product]) < 0
    )
      fieldErrors.value[product] = 'Isi rupiah bulat minimal nol.'
  }
  for (const [i, row] of draft.monthly.entries()) {
    for (const product of products.value) {
      if (!/^\d+$/.test(String(row[product])) || !Number.isSafeInteger(Number(row[product]))) {
        if (!Object.keys(fieldErrors.value).length) allocationProduct.value = product
        fieldErrors.value[product + i] = 'Isi rupiah bulat minimal nol.'
      }
    }
  }
  if (Object.keys(fieldErrors.value).length) {
    await nextTick()
    formElement.value?.querySelector('[aria-invalid="true"]')?.focus()
    return
  }
  const values = Object.fromEntries(PRODUCTS.map((product) => [product, Number(draft[product])]))
  error.value = validateTargets(Number(draft.year), values)
  if (error.value || saving.value) return
  saving.value = true
  try {
    await saveTargets(Number(draft.year), values, {
      requestKey: requestKey.value,
      draft: targetDraft,
      monthly: draft.monthly,
    })
    editing.value = false
    success.value = 'Target tahun ' + draft.year + ' berhasil disimpan.'
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
  <div class="page-heading">
    <div>
      <h1>Target tahunan</h1>
    </div>
    <div class="heading-actions">
      <YearFilter /><button v-if="canEdit" class="button primary" @click="edit">
        <AppIcon name="edit" :size="17" />Atur target
      </button>
    </div>
  </div>
  <p v-if="!canEdit && !loading" class="notice closing-note">
    Ringkasan kedua divisi. Pilih satu divisi untuk mengatur target tahunan.
  </p>
  <p v-if="success" class="notice success" role="status">{{ success }}</p>
  <div v-if="dashboard" class="monitor-cards target-summary">
    <article class="panel">
      <span>Total target dana {{ selectedYear }}</span
      ><strong>{{ moneyInMillions(dashboard.total_target) }}</strong>
    </article>
    <article class="panel">
      <span>Realisasi dana Won</span><strong>{{ moneyInMillions(dashboard.realization) }}</strong>
    </article>
    <article class="panel">
      <span>Pencapaian target dana</span><strong>{{ percent(dashboard.percentage) }}</strong>
    </article>
  </div>
  <UnitTargets v-slot="{ month }">
    <TargetProgress
      v-for="item in summary"
      :key="item.product"
      :item="item"
      :month-label="monthNames[month - 1]"
      :monthly-target="annualTargets[selectedYear]?.monthly?.[month]?.[item.product] || 0"
    />
  </UnitTargets>
  <AppDrawer v-if="editing" title="Atur target tahunan" @close="close">
    <form ref="formElement" novalidate :aria-busy="saving" @submit.prevent="save">
      <fieldset class="form-fields" :disabled="saving || uncertain">
        <div class="form-grid">
          <label class="full"
            >Tahun<input
              v-model="draft.year"
              name="year"
              readonly
              :aria-invalid="Boolean(fieldErrors.year)"
              :aria-describedby="fieldErrors.year ? 'target-error-year' : undefined"
              type="number"
              min="2000"
              max="2100"
              required
              :disabled="saving"
            /><small v-if="fieldErrors.year" id="target-error-year" class="field-error">{{
              fieldErrors.year
            }}</small></label
          ><label v-for="product in products" :key="product" class="full"
            >Target {{ product }} (rupiah)<MoneyInput
              v-model="draft[product]"
              :name="product"
              :aria-invalid="Boolean(fieldErrors[product])"
              :aria-describedby="fieldErrors[product] ? 'target-error-' + product : undefined"
              required
              :disabled="saving"
            /><small
              v-if="fieldErrors[product]"
              :id="'target-error-' + product"
              class="field-error"
              >{{ fieldErrors[product] }}</small
            ></label
          >
        </div>
        <h3 class="allocation-heading">Target bulanan</h3>
        <label class="allocation-picker"
          >Produk untuk alokasi bulanan
          <select v-model="allocationProduct">
            <option v-for="product in products" :key="product">{{ product }}</option>
          </select>
        </label>
        <div class="form-grid">
          <label v-for="(name, i) in monthNames" :key="name">
            {{ name }} (rupiah)
            <MoneyInput
              v-model="draft.monthly[i][allocationProduct]"
              :data-target-month="i + 1"
              :aria-label="'Target ' + allocationProduct + ' ' + name + ' (rupiah)'"
              :aria-invalid="Boolean(fieldErrors[allocationProduct + i])"
            />
            <small v-if="fieldErrors[allocationProduct + i]" class="field-error">{{
              fieldErrors[allocationProduct + i]
            }}</small>
          </label>
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
          {{ saving ? 'Menyimpan...' : uncertain ? 'Coba lagi' : 'Simpan target' }}
        </button>
      </div>
    </form>
  </AppDrawer>
</template>
<style scoped>
.allocation-heading {
  margin: 24px 0 12px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
}
.allocation-picker {
  display: grid;
  gap: 6px;
  margin-bottom: 16px;
  font-size: 13px;
}

.target-summary {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.target-summary article {
  min-width: 0;
}
.target-summary article > span {
  margin-top: 0;
}
.target-summary strong {
  overflow-wrap: anywhere;
}
.target-summary small {
  display: block;
  line-height: 1.6;
}
@media (max-width: 760px) {
  .target-summary {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
