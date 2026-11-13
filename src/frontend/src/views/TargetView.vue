<script setup>
import { computed, reactive, ref, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { confirmAction } from '../composables/useConfirm'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import MoneyInput from '../components/MoneyInput.vue'
import AppIcon from '../components/AppIcon.vue'
import YearFilter from '../components/YearFilter.vue'
import AppDrawer from '../components/AppDrawer.vue'
import TargetCardGrid from '../components/TargetCardGrid.vue'
import TargetProgress from '../components/TargetProgress.vue'
import UnitTargets from '../components/UnitTargets.vue'
import { usePipeline } from '../composables/usePipeline'
import { PRODUCTS, compactMoney, percent, validateTargets } from '../utils/pipeline'
const {
  dashboard,
  annualTargets,
  selectedYear,
  saveTargets,
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
const fieldErrors = ref({})
const editing = ref(false)
const saving = ref(false)
const uncertain = ref(false)
const conflict = ref(false)
const requestKey = ref(crypto.randomUUID())
const error = ref('')
const success = ref('')
const draft = reactive({ year: selectedYear.value, Tabungan: 0, Giro: 0, Deposito: 0 })
// Draft terpisah dari target tersimpan; baseline dipakai untuk mendeteksi perubahan.
let baseline = ''
useUnsavedChanges(
  computed(() => editing.value && (uncertain.value || JSON.stringify(draft) !== baseline)),
  saving,
)
function edit() {
  requestKey.value = crypto.randomUUID()
  uncertain.value = false
  conflict.value = false
  const stored = annualTargets.value[selectedYear.value] || {}
  Object.assign(draft, {
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
    const query = { ...route.query }
    delete query.edit
    delete query.product
    delete query.year
    await router.replace({ query })
    await nextTick()
    formElement.value?.querySelector(`[name="${product}"]`)?.focus()
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
    await saveTargets(Number(draft.year), values, { requestKey: requestKey.value })
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
      <span>Total target {{ selectedYear }}</span
      ><strong>{{ compactMoney(dashboard.total_target) }}</strong>
    </article>
    <article class="panel">
      <span>Realisasi Won</span><strong>{{ compactMoney(dashboard.realization) }}</strong>
    </article>
    <article class="panel">
      <span>Pencapaian</span><strong>{{ percent(dashboard.percentage) }}</strong>
    </article>
  </div>
  <section class="panel target-products-panel">
    <div class="panel-heading">
      <div>
        <h2>Target dan realisasi tahunan</h2>
      </div>
    </div>
    <TargetCardGrid
      ><TargetProgress v-for="item in summary" :key="item.product" :item="item"
    /></TargetCardGrid>
  </section>
  <UnitTargets />
  <AppDrawer
    v-if="editing"
    title="Atur target tahunan"
    subtitle="Target berdasarkan jenis produk"
    @close="close"
  >
    <form ref="formElement" novalidate :aria-busy="saving" @submit.prevent="save">
      <fieldset class="form-fields" :disabled="saving || uncertain">
        <div class="form-grid">
          <label class="full"
            >Tahun<input
              v-model="draft.year"
              name="year"
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
.target-products-panel {
  padding: 0 26px 24px;
}
.target-products-panel > .panel-heading {
  padding-left: 0;
  padding-right: 0;
}
@media (max-width: 760px) {
  .target-summary {
    grid-template-columns: minmax(0, 1fr);
  }
  .target-products-panel {
    padding: 0 18px 18px;
  }
}
</style>
