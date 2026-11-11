import { chromium, expect } from '@playwright/test'
import assert from 'node:assert/strict'
const browser = await chromium.launch({ channel: 'msedge' })
const page = await browser.newPage({
  viewport: { width: 1440, height: 1080 },
  reducedMotion: 'reduce',
})
const errors = []
page.setDefaultTimeout(10000)
page.on('pageerror', (e) => errors.push(e.message))
const year = new Date().getFullYear()
async function login(name) {
  console.log('Login', name)
  await page.goto('http://127.0.0.1:5173/#/login')
  await page.getByLabel('Username', { exact: true }).fill(name)
  await page.getByLabel('Password', { exact: true }).fill('demo123')
  await page.getByRole('button', { name: 'Masuk', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Progress target tahunan' })).toBeVisible()
}
async function target() {
  await page.getByRole('link', { name: 'Target', exact: true }).click()
}
async function setUnit(product, target, actual) {
  console.log('Unit', product, target)
  await page.getByRole('button', { name: 'Atur ' + product, exact: true }).click()
  await page
    .getByLabel('Target tahunan ' + product + ' (unit)', { exact: true })
    .fill(String(target))
  await page.getByLabel('Target ' + product + ' Januari (unit)', { exact: true }).fill('10')
  await page
    .getByLabel('Realisasi ' + product + ' Januari (unit)', { exact: true })
    .fill(String(actual))
  await page.getByRole('button', { name: 'Simpan target unit', exact: true }).click()
}
try {
  await login('suci')
  await expect(page.getByRole('article', { name: 'Target unit Bale Syariah' })).toHaveCount(0)
  await expect(page.getByRole('article', { name: 'Target unit QRIS' })).toHaveCount(0)
  await target()
  await expect(page.getByRole('article', { name: 'Pencapaian Giro', exact: true })).toBeVisible()
  await expect(page.getByRole('article', { name: 'Target unit Bale Syariah' })).toHaveCount(0)
  await expect(page.getByRole('article', { name: 'Target unit QRIS' })).toHaveCount(0)
  await setUnit('CMS', 60, 4)
  const komersilTargets = await page.evaluate(
    (y) => JSON.parse(localStorage.getItem('funding-pipeline-v3')).targets.Komersil[y],
    year,
  )
  await login('nisa')
  await target()
  await expect(page.getByRole('article', { name: 'Pencapaian Giro', exact: true })).toHaveCount(0)
  await expect(page.getByRole('article', { name: 'Target unit Bale Syariah' })).not.toContainText(
    '100 unit',
  )
  await page.getByRole('button', { name: 'Atur target', exact: true }).click()
  await expect(page.getByLabel('Target Giro (rupiah)', { exact: true })).toHaveCount(0)
  await page.getByLabel('Target Tabungan (rupiah)', { exact: true }).fill('1000000000')
  await page.getByLabel('Target Tabungan Januari (rupiah)', { exact: true }).fill('1000000')
  await page.getByRole('button', { name: 'Simpan target', exact: true }).click()
  await expect(page.locator('.month-detail-main')).toContainText('Rp 0,001 M')
  await setUnit('Bale Syariah', 200, 8)
  await setUnit('QRIS', 50, 5)
  await expect(page.getByRole('article', { name: 'Target unit CMS' })).toContainText('60 unit')
  await setUnit('CMS', 70, 6)
  await page.getByRole('link', { name: 'Dashboard', exact: true }).click()
  await expect(page.getByRole('article', { name: 'Target unit Bale Syariah' })).toContainText(
    '200 unit',
  )
  await expect(page.getByRole('article', { name: 'Target unit QRIS' })).toContainText('50 unit')
  await expect(page.getByRole('article', { name: 'Target unit CMS' })).toContainText('70 unit')
  await expect(page.getByRole('button', { name: 'Atur CMS', exact: true })).toHaveCount(0)
  await page.getByLabel('Bulan target unit').selectOption('1')
  await expect(page.getByRole('article', { name: 'Target unit CMS' })).toContainText('60%')
  await page.getByLabel('Tahun laporan').selectOption(String(year + 1))
  await expect(page.getByRole('article', { name: 'Target unit QRIS' })).not.toContainText('50 unit')
  await page.getByLabel('Tahun laporan').selectOption(String(year))
  await page.locator('.unit-target-panel').screenshot({ path: 'test-results/dashboard-units.png' })
  await page.getByRole('link', { name: 'Pipeline', exact: true }).click()
  await expect(page.getByText('PT Metland', { exact: true })).toHaveCount(0)
  await page.getByRole('button', { name: 'Catat opportunity', exact: true }).click()
  await expect(
    page.getByRole('dialog').getByRole('option', { name: 'Giro', exact: true }),
  ).toHaveCount(0)
  await page.getByLabel('Nama nasabah').fill('Nasabah Konsumer Test')
  await page.getByLabel('Nominal peluang (rupiah)', { exact: true }).fill('10000000')
  await page.getByRole('button', { name: 'Simpan opportunity', exact: true }).click()
  await page.getByRole('button', { name: 'Nasabah Konsumer Test', exact: true }).click()
  await page.getByRole('button', { name: 'Closing Won', exact: true }).click()
  await page.getByRole('button', { name: 'Simpan closing Won', exact: true }).click()
  await page.getByRole('link', { name: 'History', exact: true }).click()
  await expect(
    page.getByRole('button', { name: 'Nasabah Konsumer Test', exact: true }),
  ).toBeVisible()
  await page.getByRole('link', { name: 'Team', exact: true }).click()
  await expect(page.locator('.pic-analytics-card')).toHaveCount(1)
  await expect(page.locator('.pic-analytics-card')).not.toContainText('Giro')
  await login('suci')
  await expect(page.getByRole('article', { name: 'Target unit CMS' })).toContainText('70 unit')
  await page.getByRole('link', { name: 'History', exact: true }).click()
  await expect(
    page.getByRole('button', { name: 'Nasabah Konsumer Test', exact: true }),
  ).toHaveCount(0)
  assert.deepEqual(
    await page.evaluate(
      (y) => JSON.parse(localStorage.getItem('funding-pipeline-v3')).targets.Komersil[y],
      year,
    ),
    komersilTargets,
  )
  // Mutation guard is checked independently of hidden UI controls.
  const denied = await page.evaluate(async () => {
    const { usePipeline } = await import('/src/composables/usePipeline.js')
    const store = usePipeline()
    const raw = JSON.parse(localStorage.getItem('funding-pipeline-v3'))
    try {
      store.save(raw.rows.find((r) => r.division === 'Konsumer'))
      return false
    } catch {
      return true
    }
  })
  assert.equal(denied, true)
  await login('head')
  await expect(page.getByRole('article', { name: 'Target unit Bale Syariah' })).toContainText(
    '200 unit',
  )
  await expect(page.getByRole('article', { name: 'Target unit CMS' })).toContainText('70 unit')
  await target()
  await expect(page.getByRole('button', { name: 'Atur target', exact: true })).toHaveCount(0)
  await expect(page.getByRole('article', { name: 'Target unit Bale Syariah' })).toContainText(
    '200 unit',
  )
  await setUnit('CMS', 80, 9)
  await expect(page.getByRole('article', { name: 'Target unit CMS' })).toContainText('80 unit')
  await page.getByLabel('Pilih divisi').selectOption('Konsumer')
  await expect(page.getByRole('article', { name: 'Pencapaian Giro', exact: true })).toHaveCount(0)
  await expect(page.getByRole('article', { name: 'Target unit Bale Syariah' })).toContainText(
    '200 unit',
  )
  await expect(page.getByRole('article', { name: 'Target unit CMS' })).toContainText('80 unit')
  await page.getByLabel('Pilih divisi').selectOption('Komersil')
  await expect(page.getByRole('article', { name: 'Pencapaian Giro', exact: true })).toBeVisible()
  await expect(page.getByRole('article', { name: 'Target unit CMS' })).toContainText('80 unit')
  await page.getByLabel('Pilih divisi').selectOption('all')
  await page.screenshot({ path: 'test-results/divisions-target.png', fullPage: true })
  await login('nisa')
  await target()
  await expect(page.getByRole('article', { name: 'Target unit CMS' })).toContainText('80 unit')
  await page.reload()
  await expect(page.getByRole('article', { name: 'Target unit CMS' })).toContainText('80 unit')
  await page.getByLabel('Tahun laporan').selectOption(String(year + 1))
  await expect(page.getByRole('article', { name: 'Target unit CMS' })).not.toContainText('80 unit')
  await page.getByLabel('Tahun laporan').selectOption(String(year))
  await page.setViewportSize({ width: 390, height: 844 })
  await page.locator('#main').focus()
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true)
  await page.locator('.unit-target-panel').screenshot({ path: 'test-results/divisions-mobile.png' })
  assert.deepEqual(errors, [])
  console.log(
    'PASS: login pribadi, isolasi divisi, Giro, target bulanan, target unit, CMS bersama, closing, Team, reload, tahun, mobile.',
  )
} catch (e) {
  console.log('Page:', await page.locator('body').innerText())
  console.log('Errors:', errors)
  throw e
} finally {
  await browser.close()
}
