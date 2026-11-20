import test from 'node:test'
import assert from 'node:assert/strict'
import { createServer } from 'vite'
import { nextTick } from 'vue'
import { localDate } from '../src/utils/pipeline.js'

test('draft mempertahankan versi awal saat state diperbarui sebelum edit atau closing disimpan', async (t) => {
  const server = await createServer({
    configFile: false,
    optimizeDeps: { noDiscovery: true, include: [] },
    server: { middlewareMode: true, hmr: false },
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
  const writes = []
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    const path = new URL(url, 'http://localhost').pathname.replace('/api', '')
    let body
    if (options.method === 'PATCH' || options.method === 'POST') {
      const payload = JSON.parse(options.body)
      writes.push({ path, payload })
      if (payload.version !== record.version)
        return Response.json({ message: 'Data telah berubah. Muat data terbaru.' }, { status: 409 })
      record = { ...record, notes: payload.notes, version: record.version + 1 }
      body = record
    } else if (path === '/divisions') body = [division]
    else if (path === '/products') body = [product]
    else if (path === '/pics') body = [pic]
    else if (path === '/opportunities') body = { data: [record], last_page: 1 }
    else if (path === '/targets' || path === '/branch-targets') body = []
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
})
