import { chromium } from '../../../frontend/node_modules/playwright/index.mjs'
import { readFile, writeFile, access } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import assert from 'node:assert/strict'

const root = new URL('../', import.meta.url)
const names = ['arsitektur-sistem', 'erd-pipeline', 'erd-target', 'erd-keamanan']
const browser = await chromium.launch({ channel: 'msedge', headless: true })
const checks = { diagrams: [], errors: [], offline: true }
try {
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1120 }, deviceScaleFactor: 2, reducedMotion: 'reduce',
  })
  await context.setOffline(true)
  const page = await context.newPage()
  page.on('pageerror', (error) => checks.errors.push(error.message))
  for (const name of names) {
    const svg = await readFile(new URL(`${name}.svg`, root), 'utf8')
    await page.setContent(`<html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;width:1600px;height:1120px}svg{display:block}</style></head><body>${svg}</body></html>`)
    await page.evaluate(() => document.fonts.ready)
    const clipped = await page.locator('svg').evaluate((svg) => [...svg.querySelectorAll('text')].flatMap((node) => {
      const bounds = node.getBBox()
      return bounds.x < 0 || bounds.y < 0 || bounds.x + bounds.width > 1601 || bounds.y + bounds.height > 1121 ? [node.textContent] : []
    }))
    assert.deepEqual(clipped, [], `Teks terpotong: ${name}`)
    await page.screenshot({ path: fileURLToPath(new URL(`${name}.png`, root)), fullPage: true, animations: 'disabled' })
    checks.diagrams.push({ name, width: 3200, height: 2240, clippedText: clipped.length })
  }
  await page.goto(new URL('index.html', root).href)
  await page.evaluate(() => document.fonts.ready)
  await page.pdf({ path: fileURLToPath(new URL('desain-database-dan-arsitektur.pdf', root)), printBackground: true, preferCSSPageSize: true })
  const pdf = await readFile(new URL('desain-database-dan-arsitektur.pdf', root))
  checks.pdfPages = [...pdf.toString('latin1').matchAll(/\/Type\s*\/Page\b/g)].length
  assert.equal(checks.pdfPages, 4, 'PDF harus berisi empat halaman diagram.')
  const hrefs = await page.locator('a').evaluateAll((links) => links.map((link) => link.getAttribute('href')))
  for (const href of hrefs.filter((href) => href && !href.startsWith('#'))) await access(new URL(href, root))
  checks.localLinksChecked = hrefs.length
  const zoom = page.getByLabel('Perbesaran Arsitektur sistem', { exact: true })
  await zoom.fill('140')
  assert.equal(await page.locator('#arsitektur-sistem .diagram-canvas').evaluate((node) => node.style.width), '140%')
  checks.zoomControl = 'passed'
  await zoom.fill('100')
  await page.setViewportSize({ width: 390, height: 844 })
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, 'Lebar halaman mobile melampaui viewport.')
  checks.mobileViewport = 'passed'
  await page.screenshot({ path: fileURLToPath(new URL('preview-mobile.png', root)), fullPage: true, animations: 'disabled' })
  assert.deepEqual(checks.errors, [])
  await writeFile(new URL('VERIFIKASI.json', root), JSON.stringify(checks, null, 2)+'\n')
  console.log(JSON.stringify(checks, null, 2))
} finally {
  await browser.close()
}
