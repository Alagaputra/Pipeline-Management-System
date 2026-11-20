import test from 'node:test'
import assert from 'node:assert/strict'
import { createServer } from 'vite'
import { nextTick } from 'vue'
import { localDate } from '../src/utils/pipeline.js'

test('draft mempertahankan versi awal saat state diperbarui sebelum edit atau closing disimpan', async (t) => {
  const server = await createServer({
    configFile: false,
    optimizeDeps: { noDiscovery: true, include: [] },
    server: { middlewareMode: true, hmr: false, ws: false },
  })
  t.after(() => server.close())
  for (const name of ['localStorage', 'sessionStorage']) {
    const descriptor = Object.getOwnPropertyDescriptor(globalThis, name)
    Object.defineProperty(globalThis, name, { configurable: true, value: { getItem: () => null } })
    t.after(() =>
      descriptor ? Object.defineProperty(globalThis, name, descriptor) : delete globalThis[name],
    )
  }

  const division = { id: 1, name: 'Komersil', code: 'komersil' }
  const pic = { id: 1, name: 'Suci' }
  const product = {
    id: 1,
    name: 'Tabungan',
    code: 'tabungan',
    measure: 'IDR',
    divisions: [division],
  }
  let record
  let targets = []
  const writes = []
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    const path = new URL(url, 'http://localhost').pathname.replace('/api', '')
    let body
    if (options.method === 'PATCH' || options.method === 'POST') {
      const payload = JSON.parse(options.body)
      writes.push({ path, payload })
      if (path === '/targets/batch') {
        for (const entry of payload.targets) {
          const stored = targets.find(
            (item) => item.scope_code === payload.scope && item.product.code === entry.product,
          )
          if (
            entry.version !== (stored?.version || 0) ||
            (entry.monthly || []).some(
              (month) =>
                month.version !==
                (stored?.unit_realizations?.find((item) => item.month === month.month)?.version ||
                  0),
            )
          )
            return Response.json({ message: 'Target telah berubah.' }, { status: 409 })
        }
        return Response.json(targets)
      }
      if (payload.version !== record.version)
        return Response.json({ message: 'Data telah berubah. Muat data terbaru.' }, { status: 409 })
      record = { ...record, notes: payload.notes, version: record.version + 1 }
      body = record
    } else if (path === '/divisions') body = [division]
    else if (path === '/products') body = [product]
    else if (path === '/pics') body = [pic]
    else if (path === '/opportunities') body = { data: [record], last_page: 1 }
    else if (path === '/targets') body = targets
    else if (path === '/branch-targets') body = []
    else if (path === '/dashboard') body = { follow_ups: [] }
    else throw new Error(`Unexpected request: ${url}`)
    return Response.json(body)
  })

  const { useSession } = await server.ssrLoadModule('/src/composables/useSession.js')
  const { usePipeline } = await server.ssrLoadModule('/src/composables/usePipeline.js')
  const session = useSession()
  const pipeline = usePipeline()
  t.after(() => {
    session.user.value = null
  })

  for (const outcome of ['Active', 'Won', 'Lost']) {
    await t.test(outcome, async () => {
      record = {
        id: 1,
        version: 1,
        division,
        pic,
        product,
        customer_name: 'Nasabah',
        recorded_date: localDate(),
        segment: 'Mid',
        nominal: 1000,
        interest_status: 'Hot',
        outcome: 'Active',
        notes: 'Catatan lama',
      }
      session.user.value = {
        backendId: 1,
        name: 'Suci',
        division: 'Komersil',
        divisionId: 1,
        role: 'pic',
      }
      await nextTick()
      await pipeline.refresh()
      assert.equal(pipeline.storageError.value, '')
      const draft = {
        ...pipeline.rows.value[0],
        outcome,
        closedDate: localDate(),
        realization: 1000,
        lostReason: 'Batal',
      }

      record = { ...record, version: 2, notes: 'Catatan pengguna lain' }
      await pipeline.refresh()
      assert.equal(pipeline.rows.value[0].version, 2)
      await assert.rejects(pipeline.save(draft), (error) => error.status === 409)
      assert.equal(writes.at(-1).payload.version, 1)
      assert.equal(writes.at(-1).payload.notes, 'Catatan lama')
      assert.equal(
        writes.at(-1).path,
        outcome === 'Active' ? '/opportunities/1' : '/opportunities/1/closing',
      )
      assert.equal(record.notes, 'Catatan pengguna lain')
      assert.equal(record.version, 2)
    })
  }

  await t.test('form yang dimuat ulang dapat disimpan', async () => {
    const refreshedDraft = { ...pipeline.rows.value[0], notes: 'Perubahan setelah muat ulang' }
    const saved = await pipeline.save(refreshedDraft)
    assert.equal(writes.at(-1).payload.version, 2)
    assert.equal(saved.version, 3)
    assert.equal(saved.notes, refreshedDraft.notes)
  })

  await t.test('draft target rupiah memakai versi saat form dibuka', async () => {
    const year = pipeline.selectedYear.value
    targets = [
      {
        id: 1,
        scope_code: 'komersil',
        year,
        product,
        product_id: product.id,
        version: 1,
        target_value: '100',
      },
    ]
    await pipeline.refresh()
    const draft = pipeline.captureTargetDraft()
    targets = [{ ...targets[0], version: 2, target_value: '200' }]
    await pipeline.refresh()
    await assert.rejects(
      pipeline.saveTargets(year, { Tabungan: 101, Giro: 0, Deposito: 0 }, { draft }),
      (error) => error.status === 409,
    )
    assert.equal(writes.at(-1).payload.targets[0].version, 1)
    assert.equal(targets[0].target_value, '200')
    await pipeline.saveTargets(
      year,
      { Tabungan: 201, Giro: 0, Deposito: 0 },
      { draft: pipeline.captureTargetDraft() },
    )
    assert.equal(writes.at(-1).payload.targets[0].version, 2)
  })

  await t.test('draft unit memakai versi target dan realisasi bulanan awal', async () => {
    const year = pipeline.selectedYear.value
    const cms = { id: 2, code: 'cms', name: 'CMS', measure: 'UNIT', divisions: [division] }
    // Daftar produk master juga diperlukan untuk jalur simpan unit.
    const originalFetch = globalThis.fetch
    t.mock.method(globalThis, 'fetch', async (url, options) => {
      if (new URL(url, 'http://localhost').pathname.endsWith('/products'))
        return Response.json([product, cms])
      return originalFetch(url, options)
    })
    session.user.value = { ...session.user.value }
    await nextTick()
    targets = [
      {
        id: 2,
        scope_code: 'shared',
        year,
        product: cms,
        product_id: 2,
        version: 1,
        target_value: '100',
        unit_realizations: [{ month: 1, units: 10, version: 1 }],
      },
    ]
    await pipeline.refresh()
    const draft = pipeline.captureTargetDraft()
    const entry = { target: 100, monthly: { 1: { target: 10, realization: 11 } } }
    targets = [
      { ...targets[0], version: 2, unit_realizations: [{ month: 1, units: 20, version: 2 }] },
    ]
    await pipeline.refresh()
    await assert.rejects(
      pipeline.saveUnitTarget('CMS', year, entry, { draft }),
      (error) => error.status === 409,
    )
    assert.equal(writes.at(-1).payload.targets[0].version, 1)
    assert.equal(writes.at(-1).payload.targets[0].monthly[0].version, 1)
    const refreshed = pipeline.captureTargetDraft()
    targets[0].unit_realizations[0].version = 3
    await pipeline.refresh()
    await assert.rejects(
      pipeline.saveUnitTarget('CMS', year, entry, { draft: refreshed }),
      (error) => error.status === 409,
    )
    assert.equal(writes.at(-1).payload.targets[0].monthly[0].version, 2)
    await pipeline.saveUnitTarget('CMS', year, entry, { draft: pipeline.captureTargetDraft() })
  })

  await t.test(
    'perubahan tahun atau divisi menolak draft lama sebelum mengirim request',
    async () => {
      const draft = pipeline.captureTargetDraft()
      const count = writes.length
      await assert.rejects(
        pipeline.saveTargets(
          draft.context.year + 1,
          { Tabungan: 100, Giro: 0, Deposito: 0 },
          { draft },
        ),
        (error) => error.status === 409,
      )
      session.user.value = { ...session.user.value, division: 'Konsumer', divisionId: 2 }
      await nextTick()
      await pipeline.refresh()
      await assert.rejects(
        pipeline.saveTargets(
          draft.context.year,
          { Tabungan: 100, Giro: 0, Deposito: 0 },
          { draft },
        ),
        (error) => error.status === 409,
      )
      assert.equal(writes.length, count)
    },
  )
})
