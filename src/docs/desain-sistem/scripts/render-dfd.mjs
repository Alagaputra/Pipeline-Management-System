import { chromium } from '../../../frontend/node_modules/playwright/index.mjs'
import { access, readFile, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import assert from 'node:assert/strict'

const root = new URL('../', import.meta.url)
const metadata = JSON.parse(await readFile(new URL('DFD.metadata.json', root), 'utf8'))
const names = ['dfd-konteks', 'dfd-level-1', 'dfd-level-2-pipeline', 'dfd-level-3-closing']
const browser = await chromium.launch({ channel: 'msedge', headless: true })
const checks = { diagrams: [], pageErrors: [], offline: true }
try {
  const context = await browser.newContext({
    viewport: { width: metadata.width, height: metadata.height }, deviceScaleFactor: 1.5,
  })
  await context.setOffline(true)
  const page = await context.newPage()
  page.on('pageerror', error => checks.pageErrors.push(error.message))
  for (const name of names) {
    const svg = await readFile(new URL(`${name}.svg`, root), 'utf8')
    await page.setContent(`<html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0}svg{display:block}</style></head><body>${svg}</body></html>`)
    await page.evaluate(() => document.fonts.ready)
    const issues = await page.locator('svg').evaluate(svg => {
      const { width, height } = svg.viewBox.baseVal
      const allText = [...svg.querySelectorAll('text')]
      const clipped = allText.filter(node => {
        const b = node.getBBox()
        return b.x < 0 || b.y < 0 || b.x+b.width > width || b.y+b.height > height
      }).map(node => node.textContent)
      const overlaps = [...svg.querySelectorAll('.flow text')].flatMap(label => {
        const a = label.getBBox()
        return [...svg.querySelectorAll('.process,.store,.entity')].filter(node => {
          const b = node.getBBox()
          return a.x < b.x+b.width && a.x+a.width > b.x && a.y < b.y+b.height && a.y+a.height > b.y
        }).map(() => label.textContent)
      })
      const labelOverlaps = allText.flatMap((label, i) => {
        const a = label.getBBox()
        return allText.slice(i+1).filter(other => {
          const b = other.getBBox()
          return a.x < b.x+b.width && a.x+a.width > b.x && a.y < b.y+b.height && a.y+a.height > b.y
        }).map(other => `${label.textContent} / ${other.textContent}`)
      })
      return { clipped, overlaps, labelOverlaps }
    })
    assert.deepEqual(issues, { clipped: [], overlaps: [], labelOverlaps: [] }, `${name}: layout`)
    const graph = await page.locator('svg').evaluate(svg => {
      const nodes = [...svg.querySelectorAll('.process,.entity,.store')].map(node => node.getBBox())
      const onBoundary = point => nodes.some(b => {
        const withinX = point.x >= b.x-3 && point.x <= b.x+b.width+3
        const withinY = point.y >= b.y-3 && point.y <= b.y+b.height+3
        const atX = Math.abs(point.x-b.x) <= 3 || Math.abs(point.x-b.x-b.width) <= 3
        const atY = Math.abs(point.y-b.y) <= 3 || Math.abs(point.y-b.y-b.height) <= 3
        return withinX && withinY && (atX || atY)
      })
      const detached = [...svg.querySelectorAll('.flow path')].flatMap(path => {
        const a = path.getPointAtLength(0)
        const b = path.getPointAtLength(path.getTotalLength())
        return onBoundary(a) && onBoundary(b) ? [] : [path.getAttribute('d')]
      })
      return {
        processCount: svg.querySelectorAll('.process').length,
        entityIds: [...new Set([...svg.querySelectorAll('.entity')].map(node => node.dataset.entity))].sort(),
        flowCount: svg.querySelectorAll('.flow').length,
        detached,
      }
    })
    assert.deepEqual(graph.detached, [], `${name}: panah harus menyambung ke simbol`)
    assert.deepEqual(graph.entityIds, ['E1', 'E2'])
    assert.equal(graph.processCount, name === 'dfd-konteks' ? 1 : 5)
    await page.screenshot({ path: fileURLToPath(new URL(`${name}.png`, root)), fullPage: true })
    checks.diagrams.push({ name, pngWidth: metadata.width*1.5, pngHeight: metadata.height*1.5, ...issues, ...graph })
  }
  await page.goto(new URL('DFD.html', root).href)
  await page.evaluate(() => document.fonts.ready)
  await page.emulateMedia({ media: 'print' })
  checks.printOverflow = await page.locator('.sheet').evaluateAll(sheets => sheets.flatMap(sheet => {
    const frame = sheet.getBoundingClientRect()
    const image = sheet.querySelector('svg').getBoundingClientRect()
    return image.left < frame.left-1 || image.right > frame.right+1 || image.height > frame.height+1 ? [sheet.id] : []
  }))
  assert.deepEqual(checks.printOverflow, [])
  await page.pdf({ path: fileURLToPath(new URL('DFD.pdf', root)), printBackground: true, preferCSSPageSize: true })
  const pdf = await readFile(new URL('DFD.pdf', root))
  checks.pdfPages = [...pdf.toString('latin1').matchAll(/\/Type\s*\/Page\b/g)].length
  assert.equal(checks.pdfPages, 4)
  const links = await page.locator('a').evaluateAll(nodes => nodes.map(node => node.getAttribute('href')))
  for (const href of links) await access(new URL(href, root))
  checks.localLinksChecked = links.length
  await page.emulateMedia({ media: 'screen' })
  await page.getByLabel('Perbesaran DFD Level 1', { exact: true }).fill('160')
  assert.equal(await page.locator('#dfd-level-1 .canvas').evaluate(node => node.style.width), '160%')
  checks.zoom = 'passed'
  await page.getByLabel('Perbesaran DFD Level 1', { exact: true }).fill('100')
  await page.getByLabel('Perbesaran DFD Level 3 — Closing', { exact: true }).fill('160')
  assert.equal(await page.locator('#dfd-level-3-closing .canvas').evaluate(node => node.style.width), '160%')
  checks.level3Zoom = 'passed'
  await page.getByLabel('Perbesaran DFD Level 3 — Closing', { exact: true }).fill('100')
  await page.setViewportSize({ width: 390, height: 844 })
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true)
  checks.mobileWidth = 'passed'
  assert.deepEqual(checks.pageErrors, [])
  await writeFile(new URL('DFD.verifikasi.json', root), JSON.stringify(checks, null, 2)+'\n')
  console.log(JSON.stringify(checks, null, 2))
} finally {
  await browser.close()
}
