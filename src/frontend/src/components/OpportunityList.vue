<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from './AppIcon.vue'
import OpportunityTable from './OpportunityTable.vue'
import OpportunityCards from './OpportunityCards.vue'
import { STATUSES, dueState } from '../utils/pipeline'
import { usePipeline } from '../composables/usePipeline'
const { people: PEOPLE, products: PRODUCTS, loading } = usePipeline()
const props = defineProps({ rows: Array, history: Boolean, dueOnly: Boolean })
defineEmits(['select'])
const search = ref(''),
  pic = ref(''),
  product = ref(''),
  status = ref(''),
  sort = ref('updated'),
  from = ref(''),
  to = ref(''),
  due = ref(props.dueOnly || false),
  page = ref(1)
const filtersOpen = ref(false)
const filterCount = computed(
  () =>
    [
      pic.value,
      product.value,
      status.value,
      from.value,
      to.value,
      due.value,
      sort.value !== 'updated',
    ].filter(Boolean).length,
)
const filtered = computed(() =>
  props.rows
    .filter((row) => {
      return (
        (!search.value ||
          (row.customer + ' ' + row.pic + ' ' + row.product)
            .toLowerCase()
            .includes(search.value.toLowerCase())) &&
        (!pic.value || row.pic === pic.value) &&
        (!product.value || row.product === product.value) &&
        (!status.value || (props.history ? row.outcome : row.status) === status.value) &&
        (!due.value || ['today', 'overdue'].includes(dueState(row))) &&
        (!from.value || row.closedDate >= from.value) &&
        (!to.value || row.closedDate <= to.value)
      )
    })
    .sort((a, b) =>
      sort.value === 'nominal'
        ? b.nominal - a.nominal
        : sort.value === 'followup'
          ? (a.followUpDate || '9999').localeCompare(b.followUpDate || '9999')
          : props.history
            ? b.closedDate.localeCompare(a.closedDate)
            : b.updatedAt.localeCompare(a.updatedAt),
    ),
)
const pages = computed(() => Math.max(1, Math.ceil(filtered.value.length / 8)))
const displayed = computed(() => filtered.value.slice((page.value - 1) * 8, page.value * 8))
const route = useRoute()
const router = useRouter()
const filterKeys = ['q', 'pic', 'product', 'status', 'sort', 'from', 'to', 'followup', 'page']
const routePath = route.path
let hydrating = false
function readQuery() {
  if (route.path !== routePath) return
  hydrating = true
  const text = (key) => (typeof route.query[key] === 'string' ? route.query[key] : '')
  search.value = text('q')
  pic.value = text('pic')
  product.value = text('product')
  status.value = (props.history ? ['Won', 'Lost'] : STATUSES).includes(text('status'))
    ? text('status')
    : ''
  sort.value = (props.history
    ? ['updated', 'nominal']
    : ['updated', 'nominal', 'followup']
  ).includes(text('sort'))
    ? text('sort')
    : 'updated'
  from.value = props.history && /^\d{4}-\d{2}-\d{2}$/.test(text('from')) ? text('from') : ''
  to.value = props.history && /^\d{4}-\d{2}-\d{2}$/.test(text('to')) ? text('to') : ''
  due.value = !props.history && text('followup') === '1'
  page.value = Math.max(1, Math.min(100000, Number.parseInt(text('page'), 10) || 1))
  if (pic.value || product.value || from.value || to.value || sort.value !== 'updated')
    filtersOpen.value = true
  hydrating = false
}
function writeQuery() {
  if (hydrating || route.path !== routePath) return
  const query = { ...route.query }
  for (const key of filterKeys) delete query[key]
  for (const [key, value] of Object.entries({
    q: search.value,
    pic: pic.value,
    product: product.value,
    status: status.value,
    sort: sort.value === 'updated' ? '' : sort.value,
    from: from.value,
    to: to.value,
    followup: due.value ? '1' : '',
    page: page.value > 1 ? String(page.value) : '',
  })) {
    if (value) query[key] = value
  }
  if (JSON.stringify(query) !== JSON.stringify(route.query)) router.replace({ query })
}
watch(() => route.query, readQuery, { immediate: true })
watch(
  [search, pic, product, status, sort, from, to, due],
  () => {
    if (hydrating) return
    page.value = 1
    writeQuery()
  },
  { flush: 'sync' },
)
watch(page, writeQuery)
watch([pages, loading], ([value, busy]) => {
  if (!busy) page.value = Math.min(page.value, value)
})
function reset() {
  search.value = ''
  pic.value = ''
  product.value = ''
  status.value = ''
  from.value = ''
  to.value = ''
  due.value = false
  sort.value = 'updated'
}
function chooseQuick(mode) {
  if (mode === 'due') {
    due.value = !due.value
    status.value = ''
  } else if (mode === 'hot') {
    status.value = status.value === 'Hot' ? '' : 'Hot'
    due.value = false
  } else {
    due.value = false
    status.value = ''
  }
}
</script>
<template>
  <div class="table-toolbar opportunity-toolbar">
    <div class="input-icon search-input">
      <AppIcon name="search" :size="18" /><input
        v-model="search"
        aria-label="Cari peluang"
        placeholder="Cari nasabah, PIC, produk..."
      />
    </div>
    <button
      type="button"
      class="button secondary filters-toggle"
      :aria-expanded="filtersOpen"
      aria-controls="opportunity-filters"
      @click="filtersOpen = !filtersOpen"
    >
      <AppIcon name="filter" :size="17" />Filter
      <span v-if="filterCount" class="count-badge">{{ filterCount }}</span>
    </button>
  </div>
  <div class="quick-filters" v-if="!history" aria-label="Pilih daftar peluang">
    <button
      type="button"
      :class="{ selected: !due && !status }"
      :aria-pressed="!due && !status"
      @click="chooseQuick('all')"
    >
      Semua peluang
    </button>
    <button
      type="button"
      :class="{ selected: due }"
      :aria-pressed="due"
      @click="chooseQuick('due')"
    >
      Perlu tindak lanjut
    </button>
    <button
      type="button"
      :class="{ selected: status === 'Hot' && !due }"
      :aria-pressed="status === 'Hot' && !due"
      @click="chooseQuick('hot')"
    >
      Hot
    </button>
  </div>
  <div v-if="filtersOpen" id="opportunity-filters" class="advanced-filters">
    <label
      >PIC
      <select v-model="pic" aria-label="Filter PIC">
        <option value="">Semua PIC</option>
        <option v-for="person in PEOPLE" :key="person">{{ person }}</option>
      </select></label
    >
    <label
      >Produk<select v-model="product" aria-label="Filter produk">
        <option value="">Semua produk</option>
        <option v-for="item in PRODUCTS" :key="item">{{ item }}</option>
      </select></label
    >
    <label
      >{{ history ? 'Hasil' : 'Ketertarikan'
      }}<select v-model="status" :aria-label="history ? 'Filter hasil' : 'Filter status'">
        <option value="">{{ history ? 'Won & Lost' : 'Semua status' }}</option>
        <option v-for="item in history ? ['Won', 'Lost'] : STATUSES" :key="item">
          {{ item }}
        </option>
      </select></label
    >
    <label
      >Urutkan<select v-model="sort" aria-label="Urutkan peluang">
        <option value="updated">{{ history ? 'Closing terbaru' : 'Update terbaru' }}</option>
        <option value="nominal">Nominal terbesar</option>
        <option v-if="!history" value="followup">Tindak lanjut terdekat</option>
      </select></label
    >
    <template v-if="history"
      ><label
        >Dari tanggal<input
          v-model="from"
          type="date"
          aria-label="Closing dari tanggal"
          :max="to || undefined" /></label
      ><label
        >Sampai tanggal<input
          v-model="to"
          type="date"
          aria-label="Closing sampai tanggal"
          :min="from || undefined" /></label
    ></template>
  </div>
  <div class="active-filter-summary" v-if="search || filterCount">
    <span
      >{{ filtered.length }} peluang sesuai{{
        filterCount ? ' · ' + filterCount + ' filter aktif' : ' pencarian'
      }}</span
    ><button v-if="search || filterCount" class="text-button" @click="reset">Hapus filter</button>
  </div>
  <p v-if="from && to && from > to" class="notice error" role="alert">
    Tanggal awal tidak boleh melewati tanggal akhir.
  </p>
  <div class="opportunity-desktop">
    <OpportunityTable :rows="displayed" :history="history" @select="$emit('select', $event)" />
  </div>
  <OpportunityCards :rows="displayed" :history="history" @select="$emit('select', $event)" />
  <div class="table-footer">
    <span
      >Menampilkan
      <b
        >{{ filtered.length ? (page - 1) * 8 + 1 : 0 }}–{{ Math.min(page * 8, filtered.length) }}</b
      >
      dari <b>{{ filtered.length }}</b> peluang · M = miliar rupiah</span
    >
    <div class="pagination">
      <button
        :disabled="page === 1"
        class="icon-button"
        aria-label="Halaman sebelumnya"
        @click="page--"
      >
        <AppIcon name="left" :size="16" /></button
      ><span class="current-page">{{ page }}</span
      ><span>/ {{ pages }}</span
      ><button
        :disabled="page === pages"
        class="icon-button"
        aria-label="Halaman berikutnya"
        @click="page++"
      >
        <AppIcon name="right" :size="16" />
      </button>
    </div>
  </div>
</template>
