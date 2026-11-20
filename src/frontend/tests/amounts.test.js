import test from 'node:test'
import assert from 'node:assert/strict'
import { sumAmounts, remainingAmount, compareAmounts, formatInteger } from '../src/utils/amounts.js'
import { money, compactMoney, annualSummary } from '../src/utils/pipeline.js'
import { aggregateTargets, validateUnitEntry } from '../src/utils/divisions.js'

test('agregasi divisi dan realisasi unit besar mempertahankan batas per field', () => {
  const result = aggregateTargets({
    Komersil: { 2026: { Tabungan: 9007199254740991 } },
    Konsumer: { 2026: { Tabungan: 2 } },
  })
  assert.equal(result[2026].Tabungan, '9007199254740993')
  assert.doesNotThrow(() =>
    validateUnitEntry({
      target: 100,
      monthly: {
        1: { target: 0, realization: 9007199254740991 },
        2: { target: 0, realization: 2 },
      },
    }),
  )
})

test('total melampaui integer aman dan int64 tetap eksak dan dapat diformat', () => {
  assert.equal(sumAmounts([9007199254740991, 2]), '9007199254740993')
  assert.equal(sumAmounts(['9223372036854775807', 2]), '9223372036854775809')
  assert.equal(sumAmounts([1, 2]), 3)
  assert.equal(remainingAmount('9007199254740993', 2), 9007199254740991)
  assert.equal(remainingAmount(2, '9007199254740993'), 0)
  assert.equal(compareAmounts('9007199254740993', '9007199254740992'), 1)
  assert.equal(formatInteger('9007199254740993'), '9.007.199.254.740.993')
  assert.match(money('9007199254740993'), /9\.007\.199\.254\.740\.993/)
  assert.equal(compactMoney('9007199254740993'), money('9007199254740993'))
  const rows = [9007199254740991, 2].map((realization) => ({
    outcome: 'Won',
    product: 'Giro',
    closedDate: '2026-01-01',
    realization,
  }))
  assert.equal(annualSummary(rows, { Giro: 1 }, 2026)[1].realization, '9007199254740993')
})
