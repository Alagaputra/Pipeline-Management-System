import { test, expect } from '@playwright/test'
import { localDate } from '../../src/utils/pipeline.js'
import { login, request } from './support.js'

const today = localDate()
const customer = `PT Integrasi ${Date.now()}`

test('PIC menyimpan opportunity dan closing Won ke PostgreSQL melalui Laravel', async ({
  page,
}) => {
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  await login(page)
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  await page.getByRole('button', { name: 'Catat peluang', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await dialog.getByLabel('Nama nasabah').fill(customer)
  await dialog.getByLabel('Nominal peluang (rupiah)').fill('1000000000')
  await dialog.getByLabel('Jadwal tindak lanjut').fill(today)
  await dialog.getByLabel('Catatan tindak lanjut').fill('Disimpan melalui REST API Laravel.')
  await dialog.getByRole('button', { name: 'Simpan peluang', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  await expect(page.getByRole('button', { name: customer, exact: true })).toBeVisible()

  await page.getByRole('button', { name: customer, exact: true }).click()
  await page.getByRole('button', { name: 'Closing Won', exact: true }).click()
  await page.getByLabel('Realisasi dana (rupiah)').fill('700000000')
  await page.getByRole('button', { name: 'Simpan closing Won', exact: true }).click()
  await expect(page.getByRole('region', { name: 'Konfirmasi closing' })).toContainText(
    '700.000.000',
  )
  await page.setViewportSize({ width: 320, height: 844 })
  for (const name of ['Kembali ke formulir', 'Konfirmasi closing Won']) {
    const bounds = await page.getByRole('button', { name, exact: true }).boundingBox()
    expect(bounds.x).toBeGreaterThanOrEqual(0)
    expect(bounds.x + bounds.width).toBeLessThanOrEqual(320)
  }
  await page.screenshot({ path: 'test-results/closing-review-320.png' })
  await page.setViewportSize({ width: 1440, height: 1080 })
  await page.getByRole('button', { name: 'Konfirmasi closing Won', exact: true }).click()
  await expect(page.getByRole('status')).toContainText('Riwayat')

  await page.getByRole('link', { name: 'Riwayat', exact: true }).click()
  await expect(page.getByRole('button', { name: customer, exact: true })).toBeVisible()
  await page.reload()
  await expect(page.getByRole('button', { name: customer, exact: true })).toBeVisible()
  await page.getByRole('button', { name: customer, exact: true }).click()
  const timeline = page.getByRole('region', { name: 'Riwayat perkembangan' })
  await expect(timeline.getByText('Peluang dicatat', { exact: true })).toBeVisible()
  await expect(timeline.getByText('Closing Won', { exact: true })).toBeVisible()
  const closingEvent = timeline
    .locator('li')
    .filter({ has: page.getByText('Closing Won', { exact: true }) })
  await expect(closingEvent.locator('details')).not.toHaveAttribute('open', '')
  await closingEvent.locator('summary').click()
  await expect(closingEvent.locator('dl')).toContainText('700.000.000')
  expect(errors).toEqual([])
})

test('closing Won boleh melebihi potensi tanpa mengubah nominal peluang', async ({ page }) => {
  const customer = `PT Realisasi Lebih ${Date.now()}`
  await login(page)
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  await page.getByRole('button', { name: 'Catat peluang', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await dialog.getByLabel('Nama nasabah').fill(customer)
  await dialog.getByLabel('Nominal peluang (rupiah)').fill('1000000000')
  await dialog.getByRole('button', { name: 'Simpan peluang', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  await page.getByRole('button', { name: customer, exact: true }).click()
  await dialog.getByRole('button', { name: 'Closing Won', exact: true }).click()
  await dialog.getByLabel('Realisasi dana (rupiah)').fill('1200000000')
  await dialog.getByRole('button', { name: 'Simpan closing Won', exact: true }).click()
  const review = page.getByRole('region', { name: 'Konfirmasi closing' })
  await expect(review).toContainText('1.000.000.000')
  await expect(review).toContainText('1.200.000.000')
  const closingResponse = page.waitForResponse(
    (response) => response.url().endsWith('/closing') && response.request().method() === 'POST',
  )
  await dialog.getByRole('button', { name: 'Konfirmasi closing Won', exact: true }).click()
  expect((await closingResponse).status()).toBe(200)
  await expect(dialog).not.toBeVisible()
  await page.getByRole('link', { name: 'Riwayat', exact: true }).click()
  await page.getByRole('textbox', { name: 'Cari peluang' }).fill(customer)
  await expect(page.getByRole('button', { name: customer, exact: true })).toBeVisible()
  await page.reload()
  await page.getByRole('button', { name: customer, exact: true }).click()
  await expect(dialog.getByTitle(/^Rp\s1\.000\.000\.000$/)).toContainText('Rp 1 M')
  await expect(dialog.getByTitle(/^Rp\s1\.200\.000\.000$/)).toContainText('Rp 1,2 M')
  const saved = await request(page, `/opportunities?search=${encodeURIComponent(customer)}`)
  expect(saved.status).toBe(200)
  expect(saved.body.data).toHaveLength(1)
  expect(saved.body.data[0]).toMatchObject({
    nominal: '1000000000',
    realization: '1200000000',
    outcome: 'Won',
  })
})

test('target dana tersimpan di API dan tetap ada setelah reload', async ({ page }) => {
  await login(page)
  await page.getByRole('link', { name: 'Target', exact: true }).click()
  await expect(page.getByRole('article', { name: 'Target unit CMS', exact: true })).toBeVisible()
  await expect(
    page.getByRole('article', { name: 'Target unit Bale Syariah', exact: true }),
  ).toHaveCount(0)
  await expect(page.getByRole('article', { name: 'Target unit QRIS', exact: true })).toHaveCount(0)
  await page.getByRole('button', { name: 'Atur target', exact: true }).click()
  await page.getByLabel('Target Tabungan (rupiah)').fill('1000000000')
  await page.getByRole('button', { name: 'Simpan target', exact: true }).click()
  await expect(page.getByRole('status')).toContainText('berhasil disimpan')
  await page.reload()
  const targetCard = page.getByRole('article', { name: 'Pencapaian Tabungan', exact: true })
  await expect(targetCard.locator('dd').first()).toContainText('Rp 1 M')
  await expect(page.getByText('Target bulanan', { exact: true })).toHaveCount(0)
  await expect(page.getByText('Target KCP Bekasi', { exact: true })).toHaveCount(0)
  await page.screenshot({ path: 'test-results/target-desktop.png', fullPage: true })
  await page.setViewportSize({ width: 390, height: 844 })
  await page.reload()
  await expect(targetCard.locator('dd').first()).toContainText('Rp 1 M')
  await expect
    .poll(() => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth))
    .toBe(true)
  await page.screenshot({ path: 'test-results/target-mobile.png', fullPage: true })
  await page.getByRole('button', { name: 'Atur target', exact: true }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.screenshot({ path: 'test-results/target-form-mobile.png', fullPage: true })
})

test('dashboard memakai ringkasan API dan menampilkan grafik Chart.js pada desktop dan mobile', async ({
  page,
}) => {
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  await login(page)
  await expect(page.getByRole('heading', { name: 'Target dan realisasi tahunan' })).toBeVisible()
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  await page.getByRole('button', { name: 'Catat peluang', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await dialog.getByLabel('Nama nasabah').fill(`PT Grafik ${Date.now()}`)
  await dialog.getByLabel('Nominal peluang (rupiah)').fill('1000000000')
  await dialog.getByRole('button', { name: 'Simpan peluang', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  await page.getByRole('link', { name: 'Dashboard', exact: true }).click()
  await expect(
    page.getByRole('img', { name: 'Distribusi peluang aktif Cold, Warm, dan Hot' }),
  ).toBeVisible()
  await expect(page.locator('.dashboard-target-card')).toHaveCount(3)
  await expect(page.getByRole('article', { name: 'Target Tabungan', exact: true })).toContainText(
    'Realisasi Won',
  )
  await expect(
    page.getByRole('img', { name: 'Perbandingan target tahunan dan realisasi Won per produk' }),
  ).toHaveCount(0)
  await page.getByText('Lihat perbandingan grafik', { exact: true }).click()
  await expect(
    page.getByRole('img', { name: 'Perbandingan target tahunan dan realisasi Won per produk' }),
  ).toBeVisible()
  await page.getByText('Lihat perbandingan grafik', { exact: true }).click()
  await expect(
    page.getByRole('img', { name: 'Nilai peluang yang dicatat dan realisasi Won setiap bulan' }),
  ).toBeVisible()
  await page.getByText('Lihat rincian bulanan', { exact: true }).click()
  await expect(page.locator('.trend-panel tbody tr')).toHaveCount(12)
  await page.screenshot({ path: 'test-results/proposal-dashboard-desktop.png', fullPage: true })
  await page.setViewportSize({ width: 390, height: 844 })
  await page.reload()
  await expect(page.getByRole('article', { name: 'Target Tabungan', exact: true })).toBeVisible()
  await expect
    .poll(() => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth))
    .toBe(true)
  await page.screenshot({ path: 'test-results/proposal-dashboard-mobile.png', fullPage: true })
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  )
  expect(errors).toEqual([])
})

test('akun Konsumer menampilkan dan menyimpan Bale, QRIS, CMS tanpa pilihan Giro', async ({
  page,
}) => {
  await login(page, 'nisa')
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  await page.getByRole('button', { name: 'Catat peluang', exact: true }).click()
  const product = page.getByRole('dialog').getByLabel('Produk')
  await expect(product.locator('option')).toHaveCount(2)
  await expect(product.locator('option', { hasText: 'Giro' })).toHaveCount(0)
  await page.getByRole('button', { name: 'Batal', exact: true }).click()
  await page.getByRole('link', { name: 'Target', exact: true }).click()
  const services = page.getByRole('region', { name: 'Target layanan dalam unit' })
  for (const [name, target] of [
    ['Bale Syariah', 200],
    ['QRIS', 100],
    ['CMS', 60],
  ]) {
    await expect(
      page.getByRole('article', { name: 'Target unit ' + name, exact: true }),
    ).toBeVisible()
    await page.getByRole('button', { name: 'Atur ' + name, exact: true }).click()
    const dialog = page.getByRole('dialog')
    await dialog
      .getByLabel('Target tahunan ' + name + ' (unit)', { exact: true })
      .fill(String(target))
    await dialog.getByLabel('Target ' + name + ' Januari (unit)', { exact: true }).fill('20')
    await dialog.getByLabel('Realisasi ' + name + ' Januari (unit)', { exact: true }).fill('8')
    await dialog.getByRole('button', { name: 'Simpan target unit', exact: true }).click()
    await expect(dialog).not.toBeVisible()
    await expect(services.getByRole('status')).toContainText(name + ' tahun')
  }
  await page.reload()
  await page.getByLabel('Bulan target unit').selectOption('1')
  for (const [name, target] of [
    ['Bale Syariah', 200],
    ['QRIS', 100],
    ['CMS', 60],
  ]) {
    const card = page.getByRole('article', { name: 'Target unit ' + name, exact: true })
    await expect(card.locator('[data-metric=target]')).toHaveText(target + ' unit')
    await expect(card.locator('.unit-month-values dd').first()).toHaveText('20 unit')
    await expect(card.locator('.unit-month-values dd').last()).toHaveText('8 unit')
  }
  await page.getByRole('link', { name: 'Dashboard', exact: true }).click()
  await expect(
    page.getByRole('article', { name: 'Target unit Bale Syariah', exact: true }),
  ).toContainText('200 unit')
  await expect(page.getByRole('article', { name: 'Target unit QRIS', exact: true })).toContainText(
    '100 unit',
  )
  await expect(page.getByRole('article', { name: 'Target unit CMS', exact: true })).toContainText(
    '60 unit',
  )
  await expect(page.getByRole('button', { name: 'Atur CMS', exact: true })).toHaveCount(0)
  await page.setViewportSize({ width: 320, height: 844 })
  await expect
    .poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth))
    .toBe(true)
  await services.screenshot({ path: 'test-results/konsumer-unit-targets-320.png' })
})

test('peluang baru tetap aktif dan tindak lanjut dapat dicatat langsung dari Dashboard', async ({
  page,
}) => {
  const name = `PT Tindak Lanjut ${Date.now()}`
  await login(page)
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  await page.getByRole('button', { name: 'Catat peluang', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog.getByLabel('Hasil peluang', { exact: true })).toHaveCount(0)
  await dialog.getByLabel('Nama nasabah').fill(name)
  await dialog.getByLabel('Nominal peluang (rupiah)').fill('250000000')
  await dialog.getByLabel('Jadwal tindak lanjut').fill(today)
  await dialog.getByRole('button', { name: 'Simpan peluang', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  await page.getByRole('link', { name: 'Dashboard', exact: true }).click()
  const queue = page.getByRole('region', { name: 'Tindak lanjut hari ini' })
  const quickAction = queue.getByRole('button', { name: 'Tindak lanjut ' + name, exact: true })
  if (await quickAction.count()) await quickAction.click()
  else {
    await queue.getByRole('link', { name: 'Lihat semua', exact: true }).click()
    await page.getByLabel('Cari peluang').fill(name)
    await page.getByRole('button', { name, exact: true }).click()
    await dialog.getByRole('button', { name: 'Catat tindak lanjut', exact: true }).click()
  }
  await expect(dialog.getByLabel('Nama nasabah')).toHaveCount(0)
  await expect(dialog.getByLabel('Hasil peluang', { exact: true })).toHaveCount(0)
  await dialog.getByLabel('Catatan tindak lanjut').fill('Nasabah meminta dihubungi kembali besok.')
  await dialog.getByRole('button', { name: 'Simpan tindak lanjut', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  await page.getByRole('button', { name: name, exact: true }).click()
  await expect(dialog).toContainText('Nasabah meminta dihubungi kembali besok.')
  await expect(dialog.getByRole('button', { name: 'Closing Won', exact: true })).toBeVisible()
})

test('kartu mobile dan filter lanjutan menjaga data peluang serta dapat direset', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await login(page)
  await page.goto('/#/pipeline')
  await expect(page.getByRole('heading', { name: 'Pipeline aktif', exact: true })).toBeVisible()
  await expect(page.locator('.opportunity-desktop')).toBeHidden()
  await expect(page.locator('.opportunity-mobile')).toBeVisible()
  await expect(page.getByLabel('Filter PIC')).toHaveCount(0)
  await page.getByRole('button', { name: 'Filter', exact: true }).click()
  await page.getByLabel('Filter PIC').selectOption('Dharma')
  await expect(page.getByRole('button', { name: 'Filter 1', exact: true })).toHaveAttribute(
    'aria-expanded',
    'true',
  )
  await expect(page.locator('.mobile-opportunity')).toHaveCount(0)
  await page.getByRole('button', { name: 'Hapus filter', exact: true }).click()
  await expect(page.locator('.mobile-opportunity').first()).toBeVisible()
  await page.getByRole('button', { name: 'Filter', exact: true }).click()
  await expect(page.getByLabel('Filter PIC')).toHaveCount(0)
  await expect
    .poll(() => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth))
    .toBe(true)
  await page.screenshot({ path: 'test-results/ux-pipeline-mobile.png', fullPage: true })
  await page.locator('.opportunity-mobile .customer-link').first().click()
  await expect(page.getByRole('dialog', { name: 'Detail peluang' })).toBeVisible()
})

test('ringkasan Tim tetap bisa membuka komposisi produk dan peluang PIC', async ({ page }) => {
  await login(page)
  await page.getByRole('link', { name: 'Tim', exact: true }).click()
  await expect(page.locator('.team-summary-row')).toHaveCount(3)
  await expect(page.locator('.team-summary .distribution-donut')).toHaveCount(0)
  await page.getByRole('button', { name: 'Detail PIC Suci', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog.getByRole('heading', { name: 'Peluang pernah ditangani' })).toBeVisible()
  await expect(dialog.locator('.distribution-donut')).toBeVisible()
  await dialog.getByRole('button', { name: 'Realisasi Won', exact: true }).click()
  await expect(dialog).toContainText('Realisasi Won tahun')
  await dialog.getByRole('button', { name: 'Tutup panel', exact: true }).click()
  await page.getByLabel('Cari PIC').fill('Cacan')
  await expect(page.locator('.team-summary-row')).toHaveCount(1)
})

test('validasi per kolom, format rupiah, dan simpan sekali saat permintaan berjalan', async ({
  page,
}) => {
  await login(page)
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  await page.getByRole('button', { name: 'Catat peluang', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await dialog.getByRole('button', { name: 'Simpan peluang', exact: true }).click()
  await expect(dialog.locator('#error-customer')).toBeVisible()
  await expect(dialog.locator('[name="customer"]')).toBeFocused()
  await expect(dialog.locator('#error-nominal')).toBeVisible()
  const name = `PT Guard ${Date.now()}`
  await dialog.getByLabel('Nama nasabah').fill(name)
  await dialog.getByLabel('Nominal peluang (rupiah)').fill('1250000000')
  await expect(dialog.getByLabel('Nominal peluang (rupiah)')).toHaveValue('1.250.000.000')
  let calls = 0
  let release
  const gate = new Promise((resolve) => {
    release = resolve
  })
  await page.route('**/api/opportunities', async (route) => {
    if (route.request().method() !== 'POST') return route.continue()
    calls++
    await gate
    await route.continue()
  })
  await dialog.getByRole('button', { name: 'Simpan peluang', exact: true }).click()
  await expect(dialog.locator('button[type="submit"], .form-actions .primary')).toBeDisabled()
  await dialog
    .locator('form')
    .evaluate((form) =>
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })),
    )
  await expect.poll(() => calls).toBe(1)
  release()
  await expect(dialog).not.toBeVisible()
  await expect(page.getByRole('button', { name, exact: true })).toBeVisible()
})

test('pencarian dan filter URL pulih setelah reload dan navigasi kembali', async ({ page }) => {
  await login(page)
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  await page.getByLabel('Cari peluang').fill('PT')
  await page.getByRole('button', { name: 'Filter', exact: true }).click()
  await page.getByLabel('Filter produk').selectOption('Tabungan')
  await page.getByLabel('Urutkan peluang').selectOption('nominal')
  await expect(page).toHaveURL(/q=PT/)
  await expect(page).toHaveURL(/product=Tabungan/)
  await expect(page).toHaveURL(/sort=nominal/)
  await page.reload()
  await expect(page.getByLabel('Cari peluang')).toHaveValue('PT')
  await expect(page.getByLabel('Filter produk')).toHaveValue('Tabungan')
  await expect(page.getByLabel('Urutkan peluang')).toHaveValue('nominal')
  await page.getByRole('link', { name: 'Dashboard', exact: true }).click()
  await expect(
    page.getByRole('heading', { name: 'Selamat bekerja, Suci', exact: true }),
  ).toBeVisible()
  await page.goBack()
  await expect(page.getByLabel('Cari peluang')).toHaveValue('PT')
  await page.getByRole('button', { name: 'Hapus filter', exact: true }).click()
  await expect(page).not.toHaveURL(/q=|product=|sort=/)
})

test('target kosong di dashboard membuka formulir produk dengan fokus dan validasi', async ({
  page,
}) => {
  await login(page)
  await page.getByLabel('Tahun laporan').selectOption(String(new Date().getFullYear() + 1))
  await page.getByRole('link', { name: 'Tetapkan target Tabungan', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await expect(dialog.getByLabel('Target Tabungan (rupiah)')).toBeFocused()
  await expect(dialog.getByLabel('Tahun', { exact: true })).toHaveValue(
    String(new Date().getFullYear() + 1),
  )
  await dialog.getByLabel('Target Tabungan (rupiah)').fill('-1')
  await dialog.getByRole('button', { name: 'Simpan target', exact: true }).click()
  await expect(dialog.locator('#target-error-Tabungan')).toBeVisible()
  await expect(dialog.getByLabel('Target Tabungan (rupiah)')).toBeFocused()
})
