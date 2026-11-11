import { test, expect } from '@playwright/test'
import { login, ready, request } from './support.js'

const unique = (label) => `QA ${label} ${Date.now()}`
async function createForm(page, name) {
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  await page.getByRole('button', { name: 'Catat peluang', exact: true }).click()
  const dialog = page.getByRole('dialog', { name: 'Catat peluang', exact: true })
  await dialog.getByLabel('Nama nasabah').fill(name)
  await dialog.getByLabel('Nominal peluang (rupiah)').fill('1000000000')
  return dialog
}
async function find(page, name) {
  const response = await request(
    page,
    `/opportunities?search=${encodeURIComponent(name)}&per_page=100`,
  )
  expect(response.status).toBe(200)
  return response.body.data.filter((row) => row.customer_name === name)
}
function deferred() {
  let resolve
  return { promise: new Promise((r) => (resolve = r)), resolve: (...args) => resolve(...args) }
}

test('refresh gagal sesudah simpan tetap menutup formulir dan tidak membuat duplikasi', async ({
  page,
}) => {
  await login(page)
  const name = unique('refresh'),
    dialog = await createForm(page, name)
  let saved = false
  await page.route('**/api/opportunities*', async (route) => {
    if (route.request().method() === 'POST') {
      const response = await route.fetch()
      saved = true
      return route.fulfill({ response })
    }
    if (saved) return route.fulfill({ status: 503, json: { message: 'Simulasi gangguan' } })
    return route.continue()
  })
  await dialog.getByRole('button', { name: 'Simpan peluang', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  await expect(
    page.getByText('Perubahan tersimpan. Ringkasan belum diperbarui.', { exact: false }),
  ).toBeVisible()
  await expect(page.getByRole('button', { name, exact: true })).toBeVisible()
  await page.unroute('**/api/opportunities*')
  expect(await find(page, name)).toHaveLength(1)
  await page.getByRole('button', { name: 'Perbarui ringkasan', exact: true }).click()
  await ready(page)
  await expect(page.getByRole('button', { name: 'Perbarui ringkasan', exact: true })).toHaveCount(0)
})

test('respons simpan yang terputus dapat dicoba ulang dengan satu record dan satu audit', async ({
  page,
}) => {
  await login(page)
  const name = unique('retry'),
    dialog = await createForm(page, name)
  let first = true,
    calls = 0
  const keys = []
  await page.route('**/api/opportunities', async (route) => {
    if (route.request().method() !== 'POST') return route.continue()
    keys.push(route.request().headers()['idempotency-key'])
    calls++
    if (first) {
      first = false
      const response = await route.fetch()
      expect(response.status()).toBe(201)
      return route.abort('failed')
    }
    return route.continue()
  })
  await dialog.getByRole('button', { name: 'Simpan peluang', exact: true }).click()
  await expect(dialog.getByRole('alert')).toContainText('Koneksi terputus')
  await expect(dialog.getByLabel('Nama nasabah')).toBeDisabled()
  await dialog.getByRole('button', { name: 'Coba lagi', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  expect(calls).toBe(2)
  expect(keys[0]).toBeTruthy()
  expect(keys[0]).toBe(keys[1])
  const records = await find(page, name)
  expect(records).toHaveLength(1)
  const detail = await request(page, `/opportunities/${records[0].id}`)
  expect(detail.body.timeline).toHaveLength(1)
})

test('closing mengirim satu operasi dan retry respons terputus tidak mengulang closing', async ({
  page,
}) => {
  await login(page)
  const name = unique('closing'),
    dialog = await createForm(page, name)
  await dialog.getByRole('button', { name: 'Simpan peluang', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  await page.getByRole('button', { name, exact: true }).click()
  await page.getByRole('button', { name: 'Closing Won', exact: true }).click()
  await page.getByLabel('Realisasi dana (rupiah)').fill('700000000')
  await page.getByLabel('Catatan tindak lanjut').fill('Dana masuk dengan konfirmasi final.')
  const writes = []
  let first = true
  await page.route('**/api/opportunities/**', async (route) => {
    if (route.request().method() === 'GET') return route.continue()
    writes.push({ method: route.request().method(), url: new URL(route.request().url()).pathname })
    if (first) {
      first = false
      const response = await route.fetch()
      expect(response.status()).toBe(200)
      return route.abort('failed')
    }
    return route.continue()
  })
  await page.getByRole('button', { name: 'Simpan closing Won', exact: true }).click()
  await page.getByRole('button', { name: 'Konfirmasi closing Won', exact: true }).click()
  await expect(page.getByRole('dialog').getByRole('alert')).toContainText('Koneksi terputus')
  await page.getByRole('dialog').getByRole('button', { name: 'Coba lagi', exact: true }).click()
  await expect(page.getByRole('dialog')).not.toBeVisible()
  expect(writes).toHaveLength(2)
  expect(writes.every((write) => write.method === 'POST' && write.url.endsWith('/closing'))).toBe(
    true,
  )
  const [record] = await find(page, name)
  expect(record.outcome).toBe('Won')
  expect(record.version).toBe(2)
  expect(record.notes).toBe('Dana masuk dengan konfirmasi final.')
  const detail = await request(page, `/opportunities/${record.id}`)
  expect(detail.body.timeline).toHaveLength(2)
})

test('simpan target dana dan layanan masing-masing menggunakan satu permintaan tulis', async ({
  page,
}) => {
  await login(page, 'nisa')
  await page.getByRole('link', { name: 'Target', exact: true }).click()
  const writes = []
  page.on('request', (request) => {
    if (request.url().includes('/api/') && ['POST', 'PUT', 'PATCH'].includes(request.method()))
      writes.push(new URL(request.url()).pathname)
  })
  await page.getByRole('button', { name: 'Atur target', exact: true }).click()
  await page.getByLabel('Target Tabungan (rupiah)').fill('2000000000')
  await page.getByRole('button', { name: 'Simpan target', exact: true }).click()
  await expect(page.getByRole('dialog')).not.toBeVisible()
  expect(writes).toEqual(['/api/targets/batch'])
  await page.getByRole('button', { name: 'Atur Bale Syariah', exact: true }).click()
  await page.getByLabel('Target tahunan Bale Syariah (unit)', { exact: true }).fill('240')
  await page.getByLabel('Target Bale Syariah Januari (unit)', { exact: true }).fill('20')
  await page.getByLabel('Realisasi Bale Syariah Januari (unit)', { exact: true }).fill('9')
  await page.getByRole('button', { name: 'Simpan target unit', exact: true }).click()
  await expect(page.getByRole('dialog')).not.toBeVisible()
  expect(writes).toEqual(['/api/targets/batch', '/api/targets/batch'])
  await page.reload()
  await ready(page)
  await expect(
    page
      .getByRole('article', { name: 'Target unit Bale Syariah', exact: true })
      .locator('[data-metric=target]'),
  ).toHaveText('240 unit')
})

test('PostgreSQL membatalkan seluruh perubahan formulir saat produk atau bulan berkonflik', async ({
  page,
}) => {
  await login(page)
  const year = new Date().getFullYear()
  const before = (await request(page, `/targets?year=${year}&scope=komersil`)).body
  const products = ['deposito', 'giro', 'tabungan']
  const targets = products.map((product) => {
    const record = before.find((item) => item.product.code === product)
    return {
      product,
      target_value: Number(record?.target_value || 0) + 123,
      version: Number(record?.version || 0) + (product === 'tabungan' ? 1000 : 0),
    }
  })
  const failed = await request(page, '/targets/batch', {
    method: 'POST',
    body: { year, scope: 'komersil', targets },
  })
  expect(failed.status).toBe(409)
  expect((await request(page, `/targets?year=${year}&scope=komersil`)).body).toEqual(before)

  const shared = (await request(page, `/targets?year=${year}&scope=shared`)).body
  const cms = shared.find((item) => item.product.code === 'cms')
  const monthly = Array.from({ length: 12 }, (_, index) => {
    const month = index + 1,
      actual = cms?.unit_realizations.find((item) => item.month === month)
    return {
      month,
      target_value: 12,
      units: Number(actual?.units || 0) + 1,
      version: Number(actual?.version || 0) + (month === 12 ? 1000 : 0),
    }
  })
  const unitFailure = await request(page, '/targets/batch', {
    method: 'POST',
    body: {
      year,
      scope: 'shared',
      targets: [{ product: 'cms', target_value: 999, version: Number(cms?.version || 0), monthly }],
    },
  })
  expect(unitFailure.status).toBe(409)
  expect((await request(page, `/targets?year=${year}&scope=shared`)).body).toEqual(shared)
})

test('target layanan yang konflik dapat memuat data terbaru tanpa kehilangan panel', async ({
  page,
}) => {
  await login(page, 'nisa')
  await page.getByRole('link', { name: 'Target', exact: true }).click()
  await page.getByRole('button', { name: 'Atur CMS', exact: true }).click()
  const dialog = page.getByRole('dialog', { name: 'Atur CMS', exact: true })
  await page.getByLabel('Target tahunan CMS (unit)', { exact: true }).fill('321')
  const before = await request(page, `/targets?year=${new Date().getFullYear()}&scope=shared`)
  const cms = before.body.find((record) => record.product.code === 'cms')
  const update = await request(page, `/targets/shared/cms/${new Date().getFullYear()}`, {
    method: 'PUT',
    body: { target_value: 333, version: cms?.version || 0 },
  })
  expect(update.status).toBe(200)
  await page.getByRole('button', { name: 'Simpan target unit', exact: true }).click()
  await expect(dialog.getByRole('alert')).toContainText('berubah')
  await dialog.getByRole('button', { name: 'Muat data terbaru', exact: true }).click()
  const confirmation = page.getByRole('dialog', { name: 'Muat data terbaru?', exact: true })
  await confirmation.getByRole('button', { name: 'Muat data terbaru', exact: true }).click()
  await expect(dialog).toBeVisible()
  await expect(dialog.getByLabel('Target tahunan CMS (unit)', { exact: true })).toHaveValue('333')
  await expect(dialog.getByRole('alert')).toHaveCount(0)
})

test('retry target layanan setelah respons terputus mempertahankan seluruh bulan dan versinya', async ({
  page,
}) => {
  await login(page, 'nisa')
  await page.getByRole('link', { name: 'Target', exact: true }).click()
  await page.getByRole('button', { name: 'Atur QRIS', exact: true }).click()
  const dialog = page.getByRole('dialog', { name: 'Atur QRIS', exact: true })
  await dialog.getByLabel('Target tahunan QRIS (unit)', { exact: true }).fill('120')
  await dialog.getByLabel('Target QRIS Januari (unit)', { exact: true }).fill('10')
  await dialog.getByLabel('Realisasi QRIS Januari (unit)', { exact: true }).fill('7')
  let first = true,
    version
  await page.route('**/api/targets/batch', async (route) => {
    const response = await route.fetch()
    if (first) {
      first = false
      version = (await response.json())[0].version
      return route.abort('failed')
    }
    expect(response.headers()['idempotency-replayed']).toBe('true')
    return route.fulfill({ response })
  })
  await dialog.getByRole('button', { name: 'Simpan target unit', exact: true }).click()
  await expect(dialog.getByRole('alert')).toContainText('Koneksi terputus')
  await expect(dialog.getByLabel('Target tahunan QRIS (unit)', { exact: true })).toBeDisabled()
  await dialog.getByRole('button', { name: 'Coba lagi', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  const records = (await request(page, `/targets?year=${new Date().getFullYear()}&scope=konsumer`))
    .body
  const qris = records.find((item) => item.product.code === 'qris')
  expect(qris.version).toBe(version)
  expect(qris.monthly_targets).toHaveLength(12)
  expect(Number(qris.unit_realizations.find((month) => month.month === 1).units)).toBe(7)
})

test('formulir target dana dan layanan meminta konfirmasi pembatalan', async ({ page }) => {
  await login(page, 'nisa')
  await page.getByRole('link', { name: 'Target', exact: true }).click()
  for (const [button, field, value] of [
    ['Atur target', 'Target Tabungan (rupiah)', '987654321'],
    ['Atur Bale Syariah', 'Target tahunan Bale Syariah (unit)', '987'],
  ]) {
    await page.getByRole('button', { name: button, exact: true }).click()
    const dialog = page.getByRole('dialog')
    await dialog.getByLabel(field, { exact: true }).fill(value)
    await dialog.getByRole('button', { name: 'Batal', exact: true }).click()
    const confirmation = page.getByRole('dialog', { name: 'Batalkan perubahan?', exact: true })
    await confirmation.getByRole('button', { name: 'Lanjut mengisi', exact: true }).click()
    await expect(dialog.getByLabel(field, { exact: true })).not.toHaveValue('0')
    await dialog.getByRole('button', { name: 'Batal', exact: true }).click()
    await confirmation.getByRole('button', { name: 'Buang perubahan', exact: true }).click()
    await expect(page.getByRole('dialog')).not.toBeVisible()
  }
})

test('closing Lost memvalidasi alasan dan tersimpan di riwayat tanpa realisasi dana', async ({
  page,
}) => {
  await login(page)
  const name = unique('Lost'),
    dialog = await createForm(page, name)
  await dialog.getByRole('button', { name: 'Simpan peluang', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  await page.getByRole('button', { name, exact: true }).click()
  await page.getByRole('button', { name: 'Closing Lost', exact: true }).click()
  await page.getByRole('button', { name: 'Simpan closing Lost', exact: true }).click()
  await expect(page.locator('#error-lostReason')).toBeVisible()
  await page.getByLabel('Alasan Lost').fill('Nasabah menunda rencana penempatan dana.')
  await page.getByRole('button', { name: 'Simpan closing Lost', exact: true }).click()
  await page.getByRole('button', { name: 'Kembali ke formulir', exact: true }).click()
  await expect(page.getByLabel('Alasan Lost')).toHaveValue(
    'Nasabah menunda rencana penempatan dana.',
  )
  await page.getByRole('button', { name: 'Simpan closing Lost', exact: true }).click()
  await page.getByRole('button', { name: 'Konfirmasi closing Lost', exact: true }).click()
  await expect(page.getByRole('dialog')).not.toBeVisible()
  const [record] = await find(page, name)
  expect(record.outcome).toBe('Lost')
  expect(Number(record.realization)).toBe(0)
  await page.getByRole('link', { name: 'Riwayat', exact: true }).click()
  await page.getByLabel('Cari peluang').fill(name)
  await page.getByRole('button', { name, exact: true }).click()
  await expect(page.getByRole('dialog')).toContainText('Nasabah menunda rencana penempatan dana.')
  await expect(page.getByRole('button', { name: 'Ubah peluang', exact: true })).toHaveCount(0)
})

test('respons lama divisi tidak menimpa pilihan Head terbaru', async ({ page }) => {
  await login(page, 'head')
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  const divisions = (await request(page, '/divisions')).body
  const commercial = divisions.find((division) => division.name === 'Komersil')
  const held = deferred(),
    release = deferred()
  await page.route('**/api/opportunities?**', async (route) => {
    const url = new URL(route.request().url())
    if (url.searchParams.get('division_id') !== String(commercial.id)) return route.continue()
    const response = await route.fetch()
    held.resolve()
    await release.promise
    return route.fulfill({ response })
  })
  await page.getByLabel('Pilih divisi').selectOption('Komersil')
  await held.promise
  await page.getByLabel('Pilih divisi').selectOption('Konsumer')
  await ready(page)
  const expected = await page.locator('.opportunity-desktop .customer-link').allTextContents()
  release.resolve()
  await page.waitForLoadState('networkidle')
  await expect(page.getByLabel('Pilih divisi')).toHaveValue('Konsumer')
  expect(await page.locator('.opportunity-desktop .customer-link').allTextContents()).toEqual(
    expected,
  )
  await expect(
    page.locator('.opportunity-desktop .cell-subtitle').filter({ hasText: 'Komersil' }),
  ).toHaveCount(0)
})

test('respons target tahun lama tidak mengganti angka tahun terbaru', async ({ page }) => {
  await login(page, 'head')
  await page.getByRole('link', { name: 'Target', exact: true }).click()
  const year = new Date().getFullYear(),
    next = year + 1
  for (const [period, target] of [
    [year, 60],
    [next, 121],
  ]) {
    const records = (await request(page, `/targets?year=${period}&scope=shared`)).body
    const cms = records.find((record) => record.product.code === 'cms')
    expect(
      (
        await request(page, `/targets/shared/cms/${period}`, {
          method: 'PUT',
          body: { target_value: target, version: cms?.version || 0 },
        })
      ).status,
    ).toBe(200)
  }
  await page.getByLabel('Tahun laporan').selectOption(String(next))
  await ready(page)
  const held = deferred(),
    release = deferred()
  await page.route('**/api/targets?**', async (route) => {
    if (new URL(route.request().url()).searchParams.get('year') !== String(year))
      return route.continue()
    const response = await route.fetch()
    held.resolve()
    await release.promise
    return route.fulfill({ response })
  })
  await page.getByLabel('Tahun laporan').selectOption(String(year))
  await held.promise
  await page.getByLabel('Tahun laporan').selectOption(String(next))
  await ready(page)
  release.resolve()
  await page.waitForLoadState('networkidle')
  await expect(
    page
      .getByRole('article', { name: 'Target unit CMS', exact: true })
      .locator('[data-metric=target]'),
  ).toHaveText('121 unit')
})

test('sesi habis mengarah ke login dengan pesan yang jelas', async ({ page }) => {
  await login(page)
  const dialog = await createForm(page, unique('sesi'))
  await page.route('**/api/opportunities', (route) =>
    route.fulfill({ status: 401, json: { message: 'Unauthenticated.' } }),
  )
  await dialog.getByRole('button', { name: 'Simpan peluang', exact: true }).click()
  await expect(page).toHaveURL(/#\/login/)
  await expect(
    page.getByText('Sesi telah berakhir. Silakan masuk kembali.', { exact: true }),
  ).toBeVisible()
  expect(
    await page.evaluate(
      () =>
        localStorage.getItem('pipeline-api-token') || sessionStorage.getItem('pipeline-api-token'),
    ),
  ).toBeNull()
})

test('logout tetap selesai saat koneksi gagal tanpa error JavaScript', async ({ page }) => {
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  await login(page, 'cacan')
  await page.route('**/api/logout', (route) => route.abort('failed'))
  await page.getByRole('button', { name: 'Keluar', exact: true }).click()
  await expect(page).toHaveURL(/#\/login/)
  await expect(page.getByRole('button', { name: 'Masuk', exact: true })).toBeVisible()
  expect(
    await page.evaluate(
      () =>
        localStorage.getItem('pipeline-api-token') || sessionStorage.getItem('pipeline-api-token'),
    ),
  ).toBeNull()
  expect(errors).toEqual([])
})

test('Back browser melindungi isian dengan konfirmasi yang seragam', async ({ page }) => {
  await login(page)
  const name = unique('draft'),
    dialog = await createForm(page, name)
  await page.goBack()
  const confirmation = page.getByRole('dialog', { name: 'Batalkan perubahan?', exact: true })
  await expect(confirmation).toBeVisible()
  await confirmation.getByRole('button', { name: 'Lanjut mengisi', exact: true }).click()
  await expect(dialog.getByLabel('Nama nasabah')).toHaveValue(name)
  await expect(page).toHaveURL(/#\/pipeline/)
  await page.goBack()
  await confirmation.getByRole('button', { name: 'Buang perubahan', exact: true }).click()
  await expect(
    page.getByRole('heading', { name: 'Selamat bekerja, Suci', exact: true }),
  ).toBeVisible()
  await expect(dialog).not.toBeVisible()
})

test('skip link mempertahankan rute dan menu ponsel mendukung Escape serta fokus', async ({
  page,
}) => {
  await login(page)
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  await page.getByRole('link', { name: 'Langsung ke konten', exact: true }).focus()
  await page.keyboard.press('Enter')
  await expect(page).toHaveURL(/#\/pipeline/)
  await expect(page.locator('#main')).toBeFocused()
  await page.setViewportSize({ width: 390, height: 844 })
  const toggle = page.getByRole('button', { name: 'Buka navigasi', exact: true })
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-expanded', 'true')
  await page.keyboard.press('Escape')
  await expect(toggle).toHaveAttribute('aria-expanded', 'false')
  await expect(toggle).toBeFocused()
  await toggle.click()
  await page.getByRole('button', { name: 'Tutup navigasi', exact: true }).click()
  await expect(toggle).toHaveAttribute('aria-expanded', 'false')
})

test('Head melihat status aktif yang benar dan login tidak memajang akun demo', async ({
  page,
}) => {
  await login(page, 'head')
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  const rows = page.locator('.opportunity-desktop .customer-link')
  await expect(rows.first()).toBeVisible()
  await rows.first().click()
  const dialog = page.getByRole('dialog', { name: 'Detail peluang', exact: true })
  await expect(dialog).toContainText('Pilih divisi')
  await expect(dialog).not.toContainText('Hasil closing tersimpan')
  await expect(dialog.getByRole('button', { name: 'Closing Won', exact: true })).toHaveCount(0)
  await dialog.getByRole('button', { name: 'Tutup panel', exact: true }).click()
  await page.getByRole('button', { name: 'Keluar', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Masuk', exact: true })).toBeVisible()
  await expect(page.getByText('demo123', { exact: false })).toHaveCount(0)
  await expect(page.locator('.demo-accounts')).toHaveCount(0)
})
