import { localDate } from '../utils/pipeline'
const relativeDate = (offset) => {
  const d = new Date()
  d.setDate(d.getDate() + offset)
  return localDate(d)
}
export function createSeed() {
  return [
    ['Dharma', 'Giro', 'Mid', 'PT Nusantara Prima', 100, 'Cold', -2],
    ['Suci', 'Tabungan', 'Large', 'PT Metland', 300, 'Warm', 0],
    ['Cacan', 'Deposito', 'Mid', 'PT Nusantara Prima', 400, 'Hot', 0],
    ['Dharma', 'Giro', 'Large', 'PT Sinar Harapan', 500, 'Cold', 2],
    ['Suci', 'Tabungan', 'Mid', 'PT Metland', 250, 'Hot', 1],
    ['Cacan', 'Deposito', 'Mid', 'PT Bumi Sentosa', 500, 'Warm', 3],
    ['Dharma', 'Giro', 'Large', 'PT Nusantara Prima', 450, 'Cold', -1],
    ['Suci', 'Tabungan', 'Mid', 'PT Artha Sejahtera', 300, 'Hot', 4],
    ['Cacan', 'Deposito', 'Large', 'PT Cipta Karya', 150, 'Warm', 5],
    ['Suci', 'Tabungan', 'Mid', 'CV Mitra Usaha', 155, 'Cold', 7],
  ].map(([pic, product, segment, customer, nominal, status, due], i) => ({
    id: `PL-${String(i + 1).padStart(4, '0')}`,
    pic,
    product,
    segment,
    customer,
    nominal: nominal * 1e9,
    status,
    date: relativeDate(-i - 3),
    followUpDate: relativeDate(due),
    notes: [
      'Hubungi nasabah untuk konfirmasi kebutuhan pendanaan.',
      'Jadwalkan pertemuan lanjutan dan siapkan penawaran.',
      'Konfirmasi dokumen dan rencana penempatan dana.',
    ][i % 3],
    completed: false,
  }))
}
export const defaultTargets = { Tabungan: 1e12, Giro: 2e12, Deposito: 1.05e12 }
