import { test, expect } from '@playwright/test'
import { login, ready } from './support.js'

const pages = [
  ['Dashboard', 'Selamat bekerja,'],
  ['Pipeline', 'Pipeline aktif'],
  ['Target', 'Target tahunan'],
  ['Riwayat', 'Riwayat closing'],
  ['Tim', 'Tim / PIC'],
]

for (const [username, scope, funds, units] of [
  ['suci', 'komersil', 3, 1],
  ['nisa', 'konsumer', 2, 3],
  ['head', 'head', 3, 3],
]) {
  test(`lima halaman ${scope} rapi pada 1440, 390, dan 320 piksel`, async ({ page }) => {
    test.setTimeout(150000)
    const errors = []
    page.on('pageerror', (error) => errors.push(error.message))
    await login(page, username)
    for (const width of [1440, 390, 320]) {
      await page.setViewportSize({ width, height: width === 1440 ? 1080 : 844 })
      for (const [name, title] of pages) {
        if (width < 760)
          await page.getByRole('button', { name: 'Buka navigasi', exact: true }).click()
        await page.getByRole('link', { name, exact: true }).click()
        await expect(page.getByRole('heading', { level: 1 })).toContainText(title)
        await ready(page)
        await expect
          .poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth))
          .toBe(true)
        if (name === 'Dashboard' || name === 'Target') {
          await expect(page.locator('.unit-cards > article')).toHaveCount(units)
          await expect(page.locator('.unit-cards')).toContainText('CMS')
          if (units === 3) {
            await expect(page.locator('.unit-cards')).toContainText('Bale Syariah')
            await expect(page.locator('.unit-cards')).toContainText('QRIS')
          }
          if (name === 'Dashboard') {
            await expect(page.locator('.dashboard-target-card')).toHaveCount(funds)
            await expect(page.locator('.interest-track')).toHaveCount(3)
          }
        }
        await page.screenshot({
          path: `test-results/layout-${scope}-${name.toLowerCase()}-${width}.png`,
          fullPage: true,
          animations: 'disabled',
        })
      }
    }
    expect(errors).toEqual([])
  })
}
