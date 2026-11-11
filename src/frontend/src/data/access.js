// Akun contoh untuk prototipe lokal. Sesuaikan penempatan PIC di sini.
export const DIVISIONS = ['Konsumer', 'Komersil']
export const ACCOUNTS = [
  { id: 'suci', name: 'Suci', division: 'Komersil', role: 'pic' },
  { id: 'cacan', name: 'Cacan', division: 'Komersil', role: 'pic' },
  { id: 'dharma', name: 'Dharma', division: 'Komersil', role: 'pic' },
  { id: 'nisa', name: 'Nisa', division: 'Konsumer', role: 'pic' },
  { id: 'head', name: 'Head Funding', division: null, role: 'head' },
]
export const divisionProducts = (division) =>
  division === 'Konsumer' ? ['Tabungan', 'Deposito'] : ['Tabungan', 'Giro', 'Deposito']
export const UNIT_PRODUCTS = ['Bale Syariah', 'QRIS', 'CMS']
