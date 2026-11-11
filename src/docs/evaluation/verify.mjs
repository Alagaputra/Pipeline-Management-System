import { chromium, expect } from '@playwright/test'
import { readFileSync, existsSync, writeFileSync } from 'node:fs'
import assert from 'node:assert/strict'
import { fileURLToPath } from 'node:url'
const root = new URL('./', import.meta.url)
const html = readFileSync(new URL('index.html', root), 'utf8')
for (const match of html.matchAll(/href="([^"]+)"/g)) {
  if (!match[1].startsWith('#')) assert.ok(existsSync(new URL(match[1], root)), match[1])
}
for (const file of ['README.md', 'DATA-MODEL.md', 'FLOWS.md', 'API-AND-TESTS.md']) {
  const content = readFileSync(new URL(file, root), 'utf8')
  for (const match of content.matchAll(/\]\(([^)]+)\)/g)) assert.ok(existsSync(new URL(match[1], root)), file + ': ' + match[1])
}
const source = readFileSync(new URL('erd.mmd', root), 'utf8')
const entities = new Set([...source.matchAll(/^    (\w+) \{/gm)].map((m) => m[1]))
assert.equal(entities.size, 12)
assert.equal((source.match(/\{/g) || []).length - (source.match(/--o\{/g) || []).length, (source.match(/\}/g) || []).length)
for (const relation of source.matchAll(/^    (\w+) [|o{}-]+ (\w+) :/gm)) {
  assert.ok(entities.has(relation[1]), relation[1]); assert.ok(entities.has(relation[2]), relation[2])
}
const browser = await chromium.launch({ channel: 'msedge' })
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1080 } })
  const errors = []
  page.on('pageerror', (e) => errors.push(e.message))
  await page.goto(new URL('index.html', root).href)
  await expect(page.getByRole('heading', { name: 'Evaluasi sistem dan rancangan data' })).toBeVisible()
  await expect(page.locator('svg')).toHaveCount(3)
  await page.locator('#overview').screenshot({ path: fileURLToPath(new URL('review-overview.png', root)) })
  await page.locator('.diagram').first().screenshot({ path: fileURLToPath(new URL('review-erd.png', root)) })
  const slider = page.getByLabel('Perbesar ERD seluruh sistem')
  await slider.fill('150')
  await expect(page.locator('.diagram-canvas').first()).toHaveAttribute('style', 'width: 150%;')
  await slider.fill('100')
  await page.setViewportSize({ width: 390, height: 844 })
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth))
  await page.setViewportSize({ width: 1440, height: 1080 })
  await page.pdf({ path: fileURLToPath(new URL('evaluasi-pipeline.pdf', root)), format: 'A4', landscape: true, printBackground: true, margin: { top: '12mm', bottom: '12mm', left: '12mm', right: '12mm' } })
  assert.deepEqual(errors, [])
  console.log('PASS: 12 entitas in one ERD, tautan lokal, 3 SVG, HTML offline, zoom, mobile, PDF. Tidak ada pageerror.')
} finally { await browser.close() }
