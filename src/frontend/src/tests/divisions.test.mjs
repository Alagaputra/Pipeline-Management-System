import test from 'node:test'
import assert from 'node:assert/strict'
import {
  migrateDivisions,
  aggregateTargets,
  validateDivisionData,
  validateDivisionTargets,
  validateUnitEntry,
} from '../utils/divisions.js'
import { migrateLegacy } from '../utils/storage.js'

test('migrasi menyimpan seluruh target lama di Komersil tanpa mengubah cadangan', () => {
  const old = migrateLegacy(
    { rows: [], targets: { Tabungan: 100, Giro: 200, Deposito: 300 } },
    2026,
  )
  old.annualTargets[2026].monthly = { 1: { Tabungan: 1, Giro: 2, Deposito: 3 } }
  old.annualTargets[2026].bekasi = 40
  const original = JSON.stringify(old)
  const data = migrateDivisions(old)
  assert.equal(JSON.stringify(old), original)
  assert.deepEqual(data.targets.Komersil, old.annualTargets)
  assert.deepEqual(data.targets.Konsumer, {})
  assert.equal(validateDivisionData(data), data)
})
test('target tahunan dan bulanan digabung menurut tahun, Giro ditolak untuk Konsumer', () => {
  const consumer = {
    Tabungan: 100,
    Giro: 0,
    Deposito: 20,
    monthly: { 1: { Tabungan: 10, Giro: 0, Deposito: 5 } },
  }
  assert.equal(validateDivisionTargets(2026, consumer, 'Konsumer'), '')
  assert.ok(validateDivisionTargets(2026, { ...consumer, Giro: 1 }, 'Konsumer'))
  assert.ok(validateDivisionTargets(2026, { ...consumer, monthly: { 1: { Giro: 1 } } }, 'Konsumer'))
  const result = aggregateTargets({
    Konsumer: { 2026: consumer },
    Komersil: {
      2026: {
        Tabungan: 50,
        Giro: 80,
        Deposito: 10,
        monthly: { 1: { Tabungan: 3, Giro: 4, Deposito: 5 } },
      },
      2027: consumer,
    },
  })
  assert.equal(result[2026].Tabungan, 150)
  assert.deepEqual(result[2026].monthly[1], { Tabungan: 13, Giro: 4, Deposito: 10 })
  assert.equal(result[2027].Tabungan, 100)
})
test('unit menolak pecahan, negatif, bulan invalid, serta CMS yang disimpan per divisi', () => {
  assert.doesNotThrow(() =>
    validateUnitEntry({ target: 10, monthly: { 1: { target: 2, realization: 3 } } }),
  )
  for (const target of [-1, 1.5, Infinity])
    assert.throws(() => validateUnitEntry({ target, monthly: {} }))
  assert.throws(() =>
    validateUnitEntry({ target: 10, monthly: { 13: { target: 1, realization: 0 } } }),
  )
  const data = migrateDivisions(
    migrateLegacy({ rows: [], targets: { Tabungan: 0, Giro: 0, Deposito: 0 } }, 2026),
  )
  data.unitTargets.Konsumer[2026] = { CMS: { target: 5, monthly: {} } }
  assert.throws(() => validateDivisionData(data))
})
