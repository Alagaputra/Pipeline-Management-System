import test from 'node:test'
import assert from 'node:assert/strict'
import {
  annualSummary,
  dueState,
  validatePipeline,
  validateTargets,
  localDate,
  validDate,
} from '../src/utils/pipeline.js'
import { migrateLegacy, validateStoredData } from '../src/utils/storage.js'
const today = localDate()
const year = Number(today.slice(0, 4))
const row = {
  id: 'a',
  customer: 'Nasabah',
  date: year + '-01-01',
  pic: 'Suci',
  product: 'Giro',
  status: 'Hot',
  segment: 'Mid',
  nominal: 1000,
  outcome: 'Active',
  notes: '',
  followUpDate: '',
  completed: false,
}
test('target menghitung realisasi Won menurut tahun closing, bukan nominal dan tanggal pencatatan', () => {
  const result = annualSummary(
    [
      { ...row, outcome: 'Won', closedDate: today, realization: 500 },
      { ...row, outcome: 'Lost', closedDate: today, realization: 0 },
      { ...row, outcome: 'Won', closedDate: year - 1 + '-12-31', realization: 900 },
      row,
    ],
    { Giro: 400 },
    year,
  )
  const giro = result.find((item) => item.product === 'Giro')
  assert.equal(giro.realization, 500)
  assert.equal(giro.percentage, 125)
  assert.equal(giro.remaining, 0)
  assert.equal(result[0].percentage, null)
})
test('follow-up selesai dan closed tidak dianggap pekerjaan terlambat', () => {
  assert.equal(dueState({ ...row, followUpDate: '2020-01-01' }), 'overdue')
  assert.equal(dueState({ ...row, followUpDate: today }), 'today')
  assert.equal(dueState({ ...row, followUpDate: today, completed: true }), '')
  assert.equal(dueState({ ...row, outcome: 'Lost', followUpDate: '2020-01-01' }), '')
})
test('validasi closing menerima realisasi di bawah, sama dengan, dan melebihi nominal potensi', () => {
  for (const realization of [700000000, 1000000000, 1200000000]) {
    const opportunity = {
      ...row,
      nominal: 1000000000,
      outcome: 'Won',
      closedDate: today,
      realization,
    }
    assert.equal(validatePipeline(opportunity), '')
    assert.equal(opportunity.nominal, 1000000000)
    const giro = annualSummary([opportunity], { Giro: 1000000000 }, year).find(
      (item) => item.product === 'Giro',
    )
    assert.equal(giro.realization, realization)
  }
})

test('validasi closing menolak realisasi tidak valid, alasan kosong, dan tanggal tidak valid', () => {
  assert.equal(validatePipeline(row), '')
  assert.equal(
    validatePipeline({ ...row, outcome: 'Won', closedDate: today, realization: 700 }),
    '',
  )
  for (const realization of [0, -1, Infinity, NaN, 0.5, Number.MAX_SAFE_INTEGER + 1])
    assert.ok(validatePipeline({ ...row, outcome: 'Won', closedDate: today, realization }))
  assert.ok(validatePipeline({ ...row, outcome: 'Lost', closedDate: today, lostReason: ' ' }))
  assert.ok(validatePipeline({ ...row, outcome: 'Won', closedDate: '2099-01-01', realization: 1 }))
  assert.equal(validDate('2026-02-31'), false)
})
test('target menerima nol sebagai belum ditetapkan dan memvalidasi tahun serta rupiah', () => {
  assert.equal(validateTargets(year, { Tabungan: 0, Giro: 100, Deposito: 0 }), '')
  assert.ok(validateTargets(1999, { Tabungan: 1, Giro: 1, Deposito: 1 }))
  assert.ok(validateTargets(year, { Tabungan: -1, Giro: 1, Deposito: 1 }))
})
test('migrasi menjaga nominal, PIC, catatan, follow-up selesai, dan segmentasi lama', () => {
  const legacy = {
    rows: [{ ...row, segment: 'Small', completed: true, notes: 'Catatan lama' }],
    targets: { Tabungan: 100, Giro: 200, Deposito: 300 },
  }
  const original = JSON.stringify(legacy)
  const data = migrateLegacy(legacy, year)
  assert.equal(JSON.stringify(legacy), original)
  assert.equal(data.rows[0].nominal, 1000)
  assert.equal(data.rows[0].segment, 'Small')
  assert.equal(data.rows[0].notes, 'Catatan lama')
  assert.equal(data.rows[0].completed, true)
  assert.equal(data.rows[0].outcome, 'Active')
  assert.deepEqual(data.annualTargets[year], legacy.targets)
  assert.deepEqual(data.rows[0].handledBy, ['Suci'])
  assert.equal(validateStoredData(data), data)
})
test('data rusak ditolak tanpa digantikan oleh data contoh', () => {
  assert.throws(() => migrateLegacy({ rows: [], targets: {} }, year))
  assert.throws(() => validateStoredData({ version: 2, rows: [row], annualTargets: {} }))
})
