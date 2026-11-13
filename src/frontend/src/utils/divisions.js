import { DIVISIONS, divisionProducts } from '../data/access.js'
import { PRODUCTS, validateTargets } from './pipeline.js'
import { validateStoredData } from './storage.js'

export function migrateDivisions(data) {
  // Kompatibilitas data lokal lama: seluruh peluang awal ditempatkan pada Komersil.
  validateStoredData(data)
  return {
    version: 3,
    rows: data.rows.map((row) => ({ ...row, division: 'Komersil' })),
    targets: { Komersil: structuredClone(data.annualTargets), Konsumer: {} },
    unitTargets: { Komersil: {}, Konsumer: {}, shared: {} },
  }
}
export function validateDivisionData(data) {
  if (data?.version !== 3 || !Array.isArray(data.rows) || !data.targets || !data.unitTargets)
    throw new Error('Format data divisi tidak valid.')
  validateStoredData({ version: 2, rows: data.rows, annualTargets: {} })
  for (const row of data.rows)
    if (!DIVISIONS.includes(row.division) || !divisionProducts(row.division).includes(row.product))
      throw new Error('Produk atau divisi opportunity tidak valid.')
  for (const division of DIVISIONS) {
    if (!data.targets[division]) throw new Error('Target divisi tidak tersedia.')
    for (const [year, target] of Object.entries(data.targets[division])) {
      const error = validateDivisionTargets(year, target, division)
      if (error) throw new Error(error)
    }
  }
  for (const scope of [...DIVISIONS, 'shared']) {
    if (!data.unitTargets[scope]) throw new Error('Target unit tidak tersedia.')
    for (const [year, products] of Object.entries(data.unitTargets[scope])) {
      if (!validYear(year)) throw new Error('Tahun target unit tidak valid.')
      for (const [product, entry] of Object.entries(products)) {
        if (!(scope === 'shared' ? ['CMS'] : ['Bale Syariah', 'QRIS']).includes(product))
          throw new Error('Produk target unit tidak valid.')
        validateUnitEntry(entry)
      }
    }
  }
  return data
}
const validYear = (year) => Number.isInteger(Number(year)) && year >= 2000 && year <= 2100
const count = (value) => Number.isSafeInteger(value) && value >= 0
export function validateUnitEntry(entry) {
  // Produk layanan memakai hitungan unit, bukan rupiah; tiap bulan harus bulat nonnegatif.
  if (!entry || !count(entry.target) || !entry.monthly)
    throw new Error('Target unit harus bilangan bulat, minimal nol.')
  let total = 0
  for (const [month, value] of Object.entries(entry.monthly)) {
    if (!/^(?:[1-9]|1[0-2])$/.test(month) || !count(value.target) || !count(value.realization))
      throw new Error('Target dan realisasi bulanan harus unit bulat, minimal nol.')
    total += value.realization
  }
  if (!Number.isSafeInteger(total)) throw new Error('Jumlah realisasi unit terlalu besar.')
}
export function validateDivisionTargets(year, values, division) {
  const error = validateTargets(year, values)
  if (error) return error
  if (values.bekasi !== undefined && !count(values.bekasi)) return 'Target cabang tidak valid.'
  if (division === 'Konsumer' && values.Giro !== 0) return 'Konsumer tidak memiliki Giro.'
  for (const [month, entry] of Object.entries(values.monthly || {})) {
    if (!/^(?:[1-9]|1[0-2])$/.test(month) || PRODUCTS.some((p) => !count(entry[p] ?? 0)))
      return 'Target bulanan tidak valid.'
    if (division === 'Konsumer' && entry.Giro) return 'Konsumer tidak memiliki Giro.'
  }
  return ''
}
export function aggregateTargets(targets) {
  // Jumlahkan target kedua divisi per tahun/bulan untuk kebutuhan tampilan gabungan.
  const result = {}
  for (const division of DIVISIONS)
    for (const [year, values] of Object.entries(targets[division])) {
      const target = (result[year] ||= {
        Tabungan: 0,
        Giro: 0,
        Deposito: 0,
        bekasi: 0,
        monthly: {},
      })
      for (const product of [...PRODUCTS, 'bekasi']) target[product] += Number(values[product]) || 0
      for (const [month, products] of Object.entries(values.monthly || {})) {
        const entry = (target.monthly[month] ||= { Tabungan: 0, Giro: 0, Deposito: 0 })
        for (const product of PRODUCTS) entry[product] += Number(products[product]) || 0
      }
    }
  return result
}
