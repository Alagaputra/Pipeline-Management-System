export const PRODUCTS = ['Tabungan', 'Giro', 'Deposito']
import { ACCOUNTS } from '../data/access.js'
export const PEOPLE = ACCOUNTS.filter((account) => account.role === 'pic').map(
  (account) => account.name,
)
export const STATUSES = ['Cold', 'Warm', 'Hot']
export const SEGMENTS = ['Mid', 'Large']
export const OUTCOMES = ['Active', 'Won', 'Lost']
export const isClosed = (row) => ['Won', 'Lost'].includes(row.outcome)
export function localDate(date = new Date()) {
  return (
    date.getFullYear() +
    '-' +
    String(date.getMonth() + 1).padStart(2, '0') +
    '-' +
    String(date.getDate()).padStart(2, '0')
  )
}
export function validDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false
  const d = new Date(value + 'T00:00:00')
  return Number.isFinite(d.getTime()) && localDate(d) === value
}
export function dateLabel(value) {
  return validDate(value)
    ? new Intl.DateTimeFormat('id-ID', { day: 'numeric', month: 'short', year: 'numeric' }).format(
        new Date(value + 'T00:00:00'),
      )
    : 'Belum dijadwalkan'
}
export function timeLabel(value) {
  const d = new Date(value)
  return Number.isFinite(d.getTime())
    ? new Intl.DateTimeFormat('id-ID', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }).format(d)
    : '—'
}
export const money = (value) =>
  new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0,
  }).format(value)
export const compactMoney = (value) => {
  const billions = value / 1e9
  // Keep small amounts visible while using the same billion unit throughout the app.
  const decimals =
    billions === 0 ? 2 : Math.min(9, Math.max(2, 2 - Math.floor(Math.log10(Math.abs(billions)))))
  return (
    'Rp ' +
    new Intl.NumberFormat('id-ID', { maximumFractionDigits: decimals }).format(billions) +
    ' M'
  )
}
export const percent = (value) =>
  value === null
    ? 'Belum ada target'
    : new Intl.NumberFormat('id-ID', { maximumFractionDigits: 1 }).format(value) + '%'
export function dueState(row, today = localDate()) {
  if (isClosed(row) || !row.followUpDate || row.completed) return ''
  return row.followUpDate < today ? 'overdue' : row.followUpDate === today ? 'today' : 'upcoming'
}
export function annualSummary(rows, targets, year) {
  return PRODUCTS.map((product) => {
    const realization = rows
      .filter(
        (row) =>
          row.outcome === 'Won' &&
          row.product === product &&
          Number(row.closedDate?.slice(0, 4)) === Number(year),
      )
      .reduce((sum, row) => sum + row.realization, 0)
    const target = targets?.[product] ?? 0
    return {
      product,
      target,
      realization,
      percentage: target > 0 ? (realization / target) * 100 : null,
      remaining: Math.max(0, target - realization),
    }
  })
}
export function pipelineFieldErrors(
  row,
  { legacy = false, people = PEOPLE, products = PRODUCTS } = {},
) {
  const errors = {}
  if (!row.customer?.trim()) errors.customer = 'Nama nasabah wajib diisi.'
  if (!validDate(row.date) || row.date > localDate())
    errors.date = 'Tanggal pencatatan harus valid dan tidak melebihi hari ini.'
  for (const [key, valid] of Object.entries({
    pic: people.includes(row.pic),
    product: products.includes(row.product),
    status: STATUSES.includes(row.status),
    segment: SEGMENTS.includes(row.segment) || (legacy && row.segment === 'Small'),
  }))
    if (!valid) errors[key] = 'Lengkapi PIC, produk, status, dan segmentasi Mid/Large.'
  if (!Number.isSafeInteger(row.nominal) || row.nominal <= 0)
    errors.nominal = 'Nominal harus berupa rupiah bulat lebih dari nol.'
  if (row.followUpDate && (!validDate(row.followUpDate) || row.followUpDate < row.date))
    errors.followUpDate = 'Tanggal follow-up tidak boleh sebelum tanggal pencatatan.'
  if (!OUTCOMES.includes(row.outcome)) errors.outcome = 'Hasil opportunity tidak valid.'
  if (isClosed(row)) {
    if (!validDate(row.closedDate) || row.closedDate < row.date || row.closedDate > localDate())
      errors.closedDate = 'Tanggal closing harus antara tanggal pencatatan dan hari ini.'
    if (row.outcome === 'Won' && (!Number.isSafeInteger(row.realization) || row.realization <= 0))
      errors.realization = 'Realisasi Won harus berupa rupiah bulat lebih dari nol.'
    if (row.outcome === 'Lost' && !row.lostReason?.trim())
      errors.lostReason = 'Tuliskan alasan opportunity Lost.'
  }
  if ((row.customer || '').length > 120) errors.customer = 'Nama nasabah maksimal 120 karakter.'
  if ((row.notes || '').length > 2000) errors.notes = 'Catatan maksimal 2000 karakter.'
  if ((row.lostReason || '').length > 1000)
    errors.lostReason = 'Alasan Lost maksimal 1000 karakter.'
  return errors
}
export function validatePipeline(row, options) {
  return Object.values(pipelineFieldErrors(row, options))[0] || ''
}
export function validateTargets(year, values) {
  if (!Number.isInteger(Number(year)) || Number(year) < 2000 || Number(year) > 2100)
    return 'Tahun harus antara 2000 dan 2100.'
  if (PRODUCTS.some((product) => !Number.isSafeInteger(values[product]) || values[product] < 0))
    return 'Target wajib rupiah bulat, minimal nol. Nol berarti target belum ditetapkan.'
  return ''
}
