import { chromium } from '../../../frontend/node_modules/playwright/index.mjs'
import { readFile, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import assert from 'node:assert/strict'

const root = new URL('../', import.meta.url)
const metadata = JSON.parse(await readFile(new URL('ERD-LENGKAP.metadata.json', root), 'utf8'))
const svg = await readFile(new URL('ERD-LENGKAP.svg', root), 'utf8')
const browser = await chromium.launch({ channel: 'msedge', headless: true })
try {
  const context = await browser.newContext({ viewport: { width: metadata.width, height: metadata.height }, deviceScaleFactor: 2 })
  await context.setOffline(true)
  const page = await context.newPage()
  await page.setContent(`<html><head><style>html,body{margin:0;padding:0}svg{display:block}</style></head><body>${svg}</body></html>`)
  await page.evaluate(() => document.fonts.ready)
  assert.equal(await page.locator('.entity').count(), metadata.tables)
  assert.equal(await page.locator('.column-name').count(), metadata.columns)
  assert.equal(await page.locator('.relation').count(), metadata.sql_foreign_keys + metadata.logical_relations)
  const clipped = await page.locator('.entity').evaluateAll((tables) => tables.flatMap((table) => {
    const box = table.querySelector('rect').getBBox()
    return [...table.querySelectorAll('text')].flatMap((text) => {
      if (!text.textContent.trim()) return []
      const bounds = text.getBBox()
      return bounds.x < box.x || bounds.x + bounds.width > box.x + box.width || bounds.y + bounds.height > box.y + box.height ? [table.dataset.table + ': ' + text.textContent] : []
    })
  }))
  assert.deepEqual(clipped, [])
  await page.screenshot({ path: fileURLToPath(new URL('ERD-LENGKAP.png', root)), fullPage: true })
  await page.goto(new URL('ERD-LENGKAP.html', root).href)
  await page.evaluate(() => document.fonts.ready)
  await page.pdf({ path: fileURLToPath(new URL('ERD-LENGKAP.pdf', root)), printBackground: true, preferCSSPageSize: true })
  const pdf = await readFile(new URL('ERD-LENGKAP.pdf', root))
  const pdfPages = [...pdf.toString('latin1').matchAll(/\/Type\s*\/Page\b/g)].length
  assert.equal(pdfPages, 1)
  await page.locator('[data-table="opportunities"]').click()
  assert.ok(await page.locator('.relation.selected').count() > 0)
  await page.locator('[data-table="opportunities"]').click()
  assert.equal(await page.locator('svg.active').count(), 0)
  await page.getByLabel('Perbesar', { exact: true }).fill('200')
  assert.equal(await page.locator('#canvas').evaluate((element) => element.style.width), '200%')
  await writeFile(new URL('ERD-LENGKAP.verifikasi.json', root), JSON.stringify({ ...metadata, pngWidth: metadata.width*2, pngHeight: metadata.height*2, pdfPages, clippedText: clipped, highlight: 'passed', zoom: 'passed' }, null, 2)+'\n')
  console.log(`ERD PNG ${metadata.width*2}x${metadata.height*2}; PDF ${pdfPages} halaman; ${metadata.tables} tabel dan ${metadata.columns} kolom terverifikasi.`)
} finally {
  await browser.close()
}
