import { validatePipeline, validateTargets } from './pipeline.js'
// Data v1 tetap disimpan sebagai cadangan; migrasi tidak mengubah nominal atau PIC.
export function migrateLegacy(data, year) {
  if (!Array.isArray(data?.rows) || validateTargets(year, data.targets || {}))
    throw new Error('Format data lama tidak valid.')
  const rows = data.rows.map((row) => ({
    ...row,
    outcome: 'Active',
    realization: 0,
    closedDate: '',
    lostReason: '',
    updatedAt: row.date + 'T00:00:00',
    handledBy: [row.pic],
  }))
  return validateStoredData({ version: 2, rows, annualTargets: { [year]: { ...data.targets } } })
}
export function validateStoredData(data) {
  if (
    data?.version !== 2 ||
    !Array.isArray(data.rows) ||
    !data.annualTargets ||
    typeof data.annualTargets !== 'object'
  )
    throw new Error('Format penyimpanan tidak valid.')
  const ids = new Set()
  for (const row of data.rows) {
    if (
      !row.id ||
      ids.has(row.id) ||
      validatePipeline(row, { legacy: true }) ||
      !Array.isArray(row.handledBy) ||
      !Number.isFinite(new Date(row.updatedAt).getTime())
    )
      throw new Error('Data opportunity tidak valid.')
    ids.add(row.id)
  }
  for (const [year, values] of Object.entries(data.annualTargets))
    if (validateTargets(year, values)) throw new Error('Data target tidak valid.')
  return data
}
