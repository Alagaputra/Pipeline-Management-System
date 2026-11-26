import { test, expect } from '@playwright/test'
import { login, ready } from './support.js'

const pages = [
  ['Dashboard', 'Dashboard'],
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
          const unitCards = page.locator(
            name === 'Dashboard'
              ? '.product-progress[data-measure=unit]'
              : '.unit-cards > .service-target-card',
          )
          await expect(unitCards).toHaveCount(units)
          await expect(
            page.getByRole('article', { name: 'Target unit CMS', exact: true }),
          ).toBeVisible()
          if (units === 3) {
            await expect(
              page.getByRole('article', { name: 'Target unit Bale Syariah', exact: true }),
            ).toBeVisible()
            await expect(
              page.getByRole('article', { name: 'Target unit QRIS', exact: true }),
            ).toBeVisible()
          }
          if (name === 'Dashboard') {
            await expect(page.locator('.product-progress[data-measure=idr]')).toHaveCount(funds)
            await expect(page.locator('main details')).toHaveCount(0)
            await expect(page.getByLabel('Bulan target unit')).toBeHidden()
            await page.getByRole('button', { name: 'Bulanan', exact: true }).click()
            await expect(page.getByLabel('Bulan target unit')).toBeVisible()
            await page.getByRole('button', { name: 'Tahunan', exact: true }).click()
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
