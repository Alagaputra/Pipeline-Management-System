import { chromium } from '../../../frontend/node_modules/playwright/index.mjs'
import { readFile, writeFile, mkdir, access } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import assert from 'node:assert/strict'

const root = new URL('../', import.meta.url)
const meta = JSON.parse(await readFile(new URL('materi.metadata.json', root), 'utf8'))
await mkdir(new URL('previews/', root), { recursive: true })
const browser = await chromium.launch({ channel: 'msedge', headless: true })
const checks = { expectedPages: meta.pages, errors: [], compactPages: [], offline: true }
try {
  const context = await browser.newContext({ viewport: { width: 1700, height: 1200 }, deviceScaleFactor: 1 })
  await context.setOffline(true)
  const page = await context.newPage()
  page.on('pageerror', e => checks.errors.push(e.message))
  await page.goto(new URL('MATERI-BELAJAR-UJIAN-MAGANG.html', root).href)
  await page.evaluate(() => document.fonts.ready)
  await page.locator('img').evaluateAll(imgs => Promise.all(imgs.map(img => img.decode())))
  const overflow = () => page.locator('.paper').evaluateAll(pages => pages.flatMap(p => {
    const frame = p.querySelector('.content').getBoundingClientRect()
    const children = [...p.querySelector('.content').children]
    const low = Math.max(frame.top, ...children.map(el => el.getBoundingClientRect().bottom))
    return low > frame.bottom+1 ? [{ id:p.id, title:p.dataset.title, over:Math.round(low-frame.bottom) }] : []
  }))
  const first = await overflow()
  for (const issue of first) {
    if (issue.over > 155) continue
    await page.locator('#'+issue.id).evaluate(p => p.classList.add('compact'))
    checks.compactPages.push(issue.id)
  }
  checks.overflow = await overflow()
  await writeFile(new URL('materi.verifikasi.json', root), JSON.stringify(checks,null,2)+'\n')
  assert.deepEqual(checks.overflow, [], 'Halaman melampaui area isi; sunting materi/tata letak')
  const links = await page.locator('a').evaluateAll(links => links.map(a => a.getAttribute('href')))
  for (const href of links) {
    if (href.startsWith('#')) assert.equal(await page.locator(href).count(),1)
    else if (!href.startsWith('https:') && !href.endsWith('.pdf')) await access(new URL(href,root))
  }
  checks.linksChecked=links.length
  checks.schemaTables=await page.locator('.dictionary table.schema').count()
  checks.schemaColumns=await page.locator('.dictionary table.schema tbody tr').count()
  assert.equal(checks.schemaTables,22)
  assert.equal(checks.schemaColumns,162)
  for (let n=1;n<=meta.pages;n++) {
    await page.locator('#page-'+n).screenshot({ path:fileURLToPath(new URL('previews/page-'+String(n).padStart(3,'0')+'.png',root)) })
  }
  await page.emulateMedia({media:'print'})
  await page.pdf({path:fileURLToPath(new URL('MATERI-BELAJAR-UJIAN-MAGANG.pdf',root)),printBackground:true,preferCSSPageSize:true,tagged:true,outline:true})
  const pdf=await readFile(new URL('MATERI-BELAJAR-UJIAN-MAGANG.pdf',root))
  checks.pdfPages=[...pdf.toString('latin1').matchAll(/\/Type\s*\/Page\b/g)].length
  assert.equal(checks.pdfPages,meta.pages)
  checks.mediaBoxes=[...new Set([...pdf.toString('latin1').matchAll(/\/MediaBox\s*\[([^\]]+)\]/g)].map(m=>m[1]))]
  assert.equal(checks.mediaBoxes.length,2,'Buku harus memuat A4 dan lampiran A3')
  checks.pdfBytes=pdf.length
  assert.deepEqual(checks.errors,[])
  // Persist the final typography choices so offline HTML matches the PDF.
  await page.emulateMedia({media:'screen'})
  const html='<!doctype html>\n'+await page.locator('html').evaluate(el=>el.outerHTML)
  await writeFile(new URL('MATERI-BELAJAR-UJIAN-MAGANG.html',root),html)
  await writeFile(new URL('materi.verifikasi.json',root),JSON.stringify(checks,null,2)+'\n')
  const review=await context.newPage()
  checks.contactSheets=[]
  for (let start=1;start<=meta.pages;start+=20) {
    const number=checks.contactSheets.length+1
    const items=[]
    for(let i=start;i<Math.min(start+20,meta.pages+1);i++) items.push(`<figure><img src="page-${String(i).padStart(3,'0')}.png"><figcaption>${i}. ${meta.pageIndex[i-1].title}</figcaption></figure>`)
    const contact=`<!doctype html><meta charset="utf-8"><style>body{margin:0;padding:20px;background:#e7edf0;font:12px Arial}.grid{display:grid;grid-template-columns:repeat(5,270px);gap:18px;width:1422px}figure{margin:0}img{width:270px;display:block;border:1px solid #a9bbc5}figcaption{padding:5px 0;line-height:1.3;height:36px}</style><div class="grid">${items.join('')}</div>`
    const name=`contact-${String(number).padStart(2,'0')}`
    await writeFile(new URL(`previews/${name}.html`,root),contact)
    await review.setViewportSize({width:1462,height:1000})
    await review.goto(new URL(`previews/${name}.html`,root).href)
    await review.locator('img').evaluateAll(imgs=>Promise.all(imgs.map(img=>img.decode())))
    await review.screenshot({path:fileURLToPath(new URL(`previews/${name}.png`,root)),fullPage:true})
    checks.contactSheets.push(name+'.png')
  }
  await writeFile(new URL('materi.verifikasi.json',root),JSON.stringify(checks,null,2)+'\n')
  console.log(JSON.stringify(checks,null,2))
} finally { await browser.close() }
