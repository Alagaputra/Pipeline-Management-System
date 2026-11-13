import { computed, ref, watch, nextTick } from 'vue'
import { DIVISIONS } from '../data/access'
import {
  validatePipeline,
  validateTargets as validatePipelineTargets,
  isClosed,
  PRODUCTS as PRODUCT_ORDER,
} from '../utils/pipeline'
import { validateUnitEntry } from '../utils/divisions'
import { api } from '../services/api'
import { useSession } from './useSession'
// Pusat alur data: sesi/divisi/tahun -> muat API -> state bersama -> tampilan.
// State di tingkat modul membuat semua pemanggil usePipeline berbagi data yang sama.
const rowsState = ref([]),
  masterDivisions = ref([]),
  masterProducts = ref([]),
  masterPics = ref([])
const annualState = ref({}),
  dashboard = ref(null),
  unitState = ref({}),
  targetRecords = ref(new Map()),
  branchRecords = ref(new Map())
const storageError = ref(''),
  storageNotice = ref(''),
  loading = ref(false)
const selectedYear = ref(new Date().getFullYear()),
  headDivision = ref('all')
const { user } = useSession()
// Nomor urut menolak respons lama yang selesai setelah permintaan baru dimulai.
const sequences = { lookups: 0, rows: 0, targets: 0, dashboard: 0, refresh: 0 }
let lookupKey = ''
const isHead = computed(() => user.value?.role === 'head')
// Head dapat memilih semua divisi; aksi edit memerlukan satu divisi dan data siap.
const division = computed(() => (isHead.value ? headDivision.value : user.value?.division || ''))
const canEdit = computed(() =>
  Boolean(user.value && !loading.value && DIVISIONS.includes(division.value)),
)
const divisionLabel = computed(() => (division.value === 'all' ? 'Semua Divisi' : division.value))
const products = computed(() =>
  masterProducts.value
    .filter(
      (item) =>
        item.measure === 'IDR' &&
        (division.value === 'all' ||
          item.divisions?.some((entry) => entry.name === division.value)),
    )
    .map((item) => item.name)
    .sort((a, b) => PRODUCT_ORDER.indexOf(a) - PRODUCT_ORDER.indexOf(b)),
)
const people = computed(() => masterPics.value.map((item) => item.name))
const rows = computed(() => rowsState.value)
const activeRows = computed(() => rows.value.filter((row) => !isClosed(row)))
const closedRows = computed(() => rows.value.filter(isClosed))
const annualTargets = computed(() => annualState.value)
function capture() {
  // Bekukan konteks sebelum await agar hasil request tetap terkait akun/divisi/tahun asal.
  return {
    userId: user.value?.backendId,
    scope: division.value,
    year: Number(selectedYear.value),
    head: isHead.value,
    divisionId:
      masterDivisions.value.find((item) => item.name === division.value)?.id ||
      user.value?.divisionId,
  }
}
function current(context, year = true) {
  // Respons dari konteks lama tidak boleh menimpa tampilan setelah pengguna berganti filter.
  return Boolean(
    user.value &&
    context.userId === user.value.backendId &&
    context.scope === division.value &&
    (!year || context.year === Number(selectedYear.value)),
  )
}
function queryScope(context) {
  return context.head && context.scope !== 'all' ? `&division_id=${context.divisionId}` : ''
}
const mapOpportunity = (item) => ({
  // Normalisasi nama field API, angka, dan relasi menjadi bentuk yang dipakai komponen.
  id: String(item.id),
  version: item.version,
  division: item.division?.name || '',
  customer: item.customer_name,
  date: item.recorded_date,
  pic: item.pic?.name || '',
  product: item.product?.name || '',
  segment: item.segment,
  nominal: Number(item.nominal),
  status: item.interest_status,
  outcome: item.outcome,
  followUpDate: item.follow_up_date || '',
  completed: Boolean(item.follow_up_completed),
  closedDate: item.closed_date || '',
  realization: Number(item.realization),
  notes: item.notes || '',
  lostReason: item.lost_reason || '',
  handledBy: [
    ...new Set(
      [...(item.assignments || []).map((entry) => entry.pic?.name), item.pic?.name].filter(Boolean),
    ),
  ],
  updatedAt: item.updated_at,
})

async function loadLookups(context) {
  // Master divisi/produk/PIC dimuat per akun dan cakupan, lalu dipakai form serta pemetaan ID.
  const key = `${context.userId}:${context.scope}`
  if (lookupKey === key) return
  const request = ++sequences.lookups
  const [divisions, allProducts] = await Promise.all([api('/divisions'), api('/products')])
  context.divisionId =
    divisions.find((item) => item.name === context.scope)?.id || context.divisionId
  if (!current(context, false) || request !== sequences.lookups) return
  const pics = await api(
    `/pics${context.head && context.scope !== 'all' ? `?division_id=${context.divisionId}` : ''}`,
  )
  if (!current(context, false) || request !== sequences.lookups) return
  masterDivisions.value = divisions
  masterProducts.value = allProducts
  masterPics.value = pics
  lookupKey = key
}
async function loadOpportunities(context) {
  // API membatasi 100 baris per halaman; kumpulkan seluruh halaman sebelum memperbarui state.
  const request = ++sequences.rows,
    records = []
  let page = 1,
    lastPage = 1
  do {
    const response = await api(`/opportunities?per_page=100&page=${page}${queryScope(context)}`)
    if (!current(context) || request !== sequences.rows) return
    records.push(...response.data)
    lastPage = response.last_page || 1
    page++
  } while (page <= lastPage)
  if (current(context) && request === sequences.rows) rowsState.value = records.map(mapOpportunity)
}
function applyTargets(targets, branches, context) {
  // Pisahkan target rupiah dari target unit. Map menyimpan record beserta version
  // untuk penyimpanan berikutnya; angka ringkasan disusun untuk kebutuhan tampilan.
  if (!current(context)) return
  const annual = { Tabungan: 0, Giro: 0, Deposito: 0, bekasi: 0, monthly: {} },
    units = {},
    map = new Map(),
    branchMap = new Map()
  for (const target of targets) {
    const product = target.product.name
    map.set(`${target.scope_code}:${target.product.code}`, target)
    if (target.product.measure === 'IDR') {
      annual[product] = (annual[product] || 0) + Number(target.target_value)
      for (const item of target.monthly_targets || [])
        (annual.monthly[item.month] ||= { Tabungan: 0, Giro: 0, Deposito: 0 })[product] += Number(
          item.target_value,
        )
    } else {
      const entry = (units[product] ||= { target: 0, monthly: {} })
      entry.target += Number(target.target_value)
      for (const item of target.monthly_targets || [])
        (entry.monthly[item.month] ||= { target: 0, realization: 0 }).target += Number(
          item.target_value,
        )
      for (const item of target.unit_realizations || [])
        (entry.monthly[item.month] ||= { target: 0, realization: 0 }).realization += Number(
          item.units,
        )
    }
  }
  for (const branch of branches) {
    annual.bekasi += Number(branch.target_value)
    branchMap.set(`${branch.division.code}:${branch.branch_code}`, branch)
  }
  annualState.value = { ...annualState.value, [context.year]: annual }
  unitState.value = units
  targetRecords.value = map
  branchRecords.value = branchMap
}
async function loadTargets(context) {
  const request = ++sequences.targets
  const targetsRequest =
    // Saat head memilih satu divisi, target CMS pada scope shared tetap disertakan.
    context.head && context.scope !== 'all'
      ? Promise.all([
          api(`/targets?year=${context.year}&scope=${context.scope.toLowerCase()}`),
          api(`/targets?year=${context.year}&scope=shared`),
        ]).then((groups) => groups.flat())
      : api(`/targets?year=${context.year}`)
  const [targets, branches] = await Promise.all([
    targetsRequest,
    api(`/branch-targets?year=${context.year}${queryScope(context)}`),
  ])
  if (current(context) && request === sequences.targets) applyTargets(targets, branches, context)
}
async function loadDashboard(context) {
  const request = ++sequences.dashboard
  const report = await api(`/dashboard?year=${context.year}${queryScope(context)}`)
  if (current(context) && request === sequences.dashboard)
    dashboard.value = { ...report, follow_ups: report.follow_ups.map(mapOpportunity) }
}
async function refresh() {
  // Master harus tersedia lebih dulu agar ID divisi benar; data lainnya dimuat paralel.
  if (!user.value) return
  const context = capture(),
    request = ++sequences.refresh
  loading.value = true
  storageError.value = ''
  try {
    await loadLookups(context)
    if (!current(context) || request !== sequences.refresh) return
    await Promise.all([loadOpportunities(context), loadTargets(context), loadDashboard(context)])
    if (current(context) && request === sequences.refresh) storageNotice.value = ''
  } catch (error) {
    if (current(context) && request === sequences.refresh) storageError.value = error.message
  } finally {
    if (current(context) && request === sequences.refresh) loading.value = false
  }
}
function reset(scopeChanged = true) {
  // Naikkan semua nomor urut untuk mengabaikan respons yang masih berjalan.
  // Jika hanya tahun berubah, master data tetap dapat dipakai.
  for (const key of Object.keys(sequences)) sequences[key]++
  rowsState.value = []
  dashboard.value = null
  unitState.value = {}
  targetRecords.value = new Map()
  branchRecords.value = new Map()
  storageError.value = ''
  storageNotice.value = ''
  if (scopeChanged) {
    annualState.value = {}
    masterPics.value = []
    masterDivisions.value = []
    masterProducts.value = []
    lookupKey = ''
  }
}
watch(
  user,
  () => {
    reset()
    headDivision.value = 'all'
    loading.value = Boolean(user.value)
    if (user.value) refresh()
  },
  { immediate: true },
)
watch([headDivision, selectedYear], ([scope], previous) => {
  // Pergantian filter membersihkan data lama sebelum memuat konteks baru.
  reset(scope !== previous?.[0])
  if (user.value) refresh()
})
function requireDivision() {
  if (!canEdit.value) throw new Error('Pilih divisi dan tunggu data selesai dimuat.')
}
async function afterWrite(context, target = false) {
  // Penyimpanan sudah berhasil sebelum fungsi ini dipanggil. Jika pemuatan ringkasan
  // gagal, tampilkan pemberitahuan tanpa menyatakan bahwa proses simpan gagal.
  if (!current(context)) return
  try {
    await Promise.all(
      target
        ? [loadTargets(context), loadDashboard(context)]
        : [loadOpportunities(context), loadDashboard(context)],
    )
    if (current(context)) storageNotice.value = ''
  } catch {
    if (current(context)) storageNotice.value = 'Perubahan tersimpan. Ringkasan belum diperbarui.'
  }
}
function rememberRow(saved, context) {
  const mapped = mapOpportunity(saved)
  if (current(context)) {
    const previous = rowsState.value.find((row) => row.id === mapped.id)
    if (previous) mapped.handledBy = [...new Set([...previous.handledBy, ...mapped.handledBy])]
    rowsState.value = [mapped, ...rowsState.value.filter((row) => row.id !== mapped.id)]
  }
  return mapped
}
function rememberTargets(saved, context) {
  if (!current(context)) return
  const map = new Map(targetRecords.value)
  for (const record of saved) map.set(`${record.scope_code}:${record.product.code}`, record)
  applyTargets([...map.values()], [...branchRecords.value.values()], context)
}
export function usePipeline() {
  // Komponen memanggil aksi di bawah; validasi awal dilakukan di sini dan
  // backend tetap memeriksa otorisasi, aturan bisnis, serta version data.
  async function save(row, { requestKey = crypto.randomUUID() } = {}) {
    requireDivision()
    const context = capture(),
      previous = rows.value.find((item) => item.id === row.id)
    if (previous && isClosed(previous))
      throw new Error('Peluang sudah selesai dan tersedia di Riwayat.')
    const error = validatePipeline(row, {
      legacy: previous?.segment === 'Small' && row.segment === 'Small',
      people: people.value,
      products: products.value,
    })
    if (error) throw new Error(error)
    let saved
    if (row.outcome !== 'Active' && previous) {
      // Closing punya endpoint khusus; Won mengirim realisasi, Lost mengirim alasan.
      saved = await api(`/opportunities/${previous.id}/closing`, {
        method: 'POST',
        requestKey,
        body: JSON.stringify({
          outcome: row.outcome,
          realization: row.outcome === 'Won' ? Number(row.realization) : 0,
          closed_date: row.closedDate,
          lost_reason: row.outcome === 'Lost' ? row.lostReason?.trim() : null,
          notes: row.notes?.trim() || null,
          version: previous.version,
        }),
      })
    } else {
      const payload = {
        division_id: context.divisionId,
        pic_id: masterPics.value.find((item) => item.name === row.pic)?.id,
        product_id: masterProducts.value.find((item) => item.name === row.product)?.id,
        customer_name: row.customer.trim(),
        segment: row.segment,
        nominal: Number(row.nominal),
        interest_status: row.status,
        recorded_date: row.date,
        follow_up_date: row.followUpDate || null,
        notes: row.notes?.trim() || null,
      }
      if (previous) payload.version = previous.version
      // version mencegah isian lama menimpa perubahan pengguna lain (konflik HTTP 409).
      saved = await api(previous ? `/opportunities/${previous.id}` : '/opportunities', {
        method: previous ? 'PATCH' : 'POST',
        requestKey,
        body: JSON.stringify(payload),
      })
    }
    const mapped = rememberRow(saved, context)
    await afterWrite(context)
    return mapped
  }
  async function complete(id, { requestKey = crypto.randomUUID() } = {}) {
    // Menyelesaikan follow-up hanya menandai tugas; status peluang tetap Active.
    requireDivision()
    const context = capture(),
      row = rows.value.find((item) => item.id === id)
    if (!row) throw new Error('Peluang tidak ditemukan.')
    const saved = await api(`/opportunities/${id}/follow-up-completion`, {
      method: 'POST',
      requestKey,
      body: JSON.stringify({ version: row.version }),
    })
    rememberRow(saved, context)
    await afterWrite(context)
  }
  async function saveTargets(year, values, { requestKey = crypto.randomUUID() } = {}) {
    // Kirim target produk dalam satu batch beserta version; 0 berarti record belum ada.
    requireDivision()
    const error = validatePipelineTargets(year, values)
    if (error) throw new Error(error)
    const context = { ...capture(), year: Number(year) },
      scope = context.scope.toLowerCase()
    const records =
      context.year === Number(selectedYear.value)
        ? [...targetRecords.value.values()]
        : await api(`/targets?year=${context.year}&scope=${scope}`)
    const targets = products.value.map((name) => {
      const product = masterProducts.value.find((item) => item.name === name)
      const record = records.find(
        (item) => item.scope_code === scope && Number(item.product_id) === Number(product.id),
      )
      return {
        product: product.code,
        target_value: Number(values[name]),
        version: Number(record?.version || 0),
      }
    })
    const saved = await api('/targets/batch', {
      method: 'POST',
      requestKey,
      body: JSON.stringify({ year: context.year, scope, targets }),
    })
    selectedYear.value = context.year
    // Tunggu watcher pergantian tahun mereset state sebelum memasang hasil simpan.
    await nextTick()
    rememberTargets(saved, context)
    await afterWrite(context, true)
  }
  function getUnitTarget(product) {
    return unitState.value[product] || { target: 0, monthly: {} }
  }
  async function saveUnitTarget(product, year, entry, { requestKey = crypto.randomUUID() } = {}) {
    // CMS memakai scope shared; layanan lainnya mengikuti divisi yang sedang dipilih.
    // Target tahunan dan 12 realisasi bulanan dikirim sebagai satu batch.
    if (!user.value || loading.value || (product !== 'CMS' && !canEdit.value))
      throw new Error('Tunggu data selesai dimuat dan pilih divisi.')
    validateUnitEntry(entry)
    const context = capture(),
      productRecord = masterProducts.value.find((item) => item.name === product),
      scope = product === 'CMS' ? 'shared' : context.scope.toLowerCase()
    const record = targetRecords.value.get(`${scope}:${productRecord.code}`)
    const versions = new Map(
      (record?.unit_realizations || []).map((item) => [item.month, Number(item.version)]),
    )
    const saved = await api('/targets/batch', {
      method: 'POST',
      requestKey,
      body: JSON.stringify({
        year: Number(year),
        scope,
        targets: [
          {
            product: productRecord.code,
            target_value: entry.target,
            version: Number(record?.version || 0),
            monthly: Array.from({ length: 12 }, (_, i) => ({
              month: i + 1,
              target_value: entry.monthly[i + 1]?.target || 0,
              units: entry.monthly[i + 1]?.realization || 0,
              version: versions.get(i + 1) || 0,
            })),
          },
        ],
      }),
    })
    rememberTargets(saved, context)
    await afterWrite(context, true)
  }
  const years = computed(() =>
    [
      ...new Set([
        new Date().getFullYear() - 1,
        new Date().getFullYear(),
        new Date().getFullYear() + 1,
        Number(selectedYear.value),
        ...Object.keys(annualState.value).map(Number),
      ]),
    ].sort((a, b) => b - a),
  )
  return {
    picRecords: masterPics,
    dashboard,
    rows,
    activeRows,
    closedRows,
    annualTargets,
    selectedYear,
    years,
    storageError,
    storageNotice,
    loading,
    refresh,
    save,
    complete,
    saveTargets,
    division,
    divisionLabel,
    headDivision,
    isHead,
    canEdit,
    products,
    people,
    getUnitTarget,
    saveUnitTarget,
  }
}
