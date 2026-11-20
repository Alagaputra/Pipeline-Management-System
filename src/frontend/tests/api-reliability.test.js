import test from 'node:test'
import assert from 'node:assert/strict'
import { createServer } from 'vite'
import { nextTick } from 'vue'
import { fileURLToPath } from 'node:url'

test('respons rusak, pergantian sesi, dan retry closing ditangani tanpa kehilangan draft', async (t) => {
  const server = await createServer({
    root: fileURLToPath(new URL('..', import.meta.url)),
    configFile: false,
    optimizeDeps: { noDiscovery: true, include: [] },
    server: { middlewareMode: true, hmr: false, ws: false },
  })
  t.after(() => server.close())
  for (const name of ['localStorage', 'sessionStorage']) {
    const map = new Map()
    Object.defineProperty(globalThis, name, {
      configurable: true,
      value: {
        getItem: (key) => map.get(key) || null,
        setItem: (key, value) => map.set(key, value),
        removeItem: (key) => map.delete(key),
      },
    })
  }
  const client = await server.ssrLoadModule('/src/services/api.js')
  await t.test(
    'payload sukses yang tidak sesuai skema tetap dapat diretry dengan body asli',
    async () => {
      const key = crypto.randomUUID()
      const writes = []
      let response = () => Response.json({})
      t.mock.method(globalThis, 'fetch', async (url, options) => {
        writes.push(options.body)
        return response()
      })
      const options = {
        method: 'POST',
        body: '{"notes":"awal"}',
        requestKey: key,
        validateResponse: (value) => value?.id === 1,
      }
      for (const invalid of [
        () => Response.json({}),
        () => Response.json(null),
        () => new Response(null, { status: 204 }),
      ]) {
        response = invalid
        await assert.rejects(
          client.api('/opportunities', options),
          (error) => error.uncertain === true,
        )
        assert.ok(client.getPendingWrite(key))
      }
      response = () => Response.json({ id: 1 })
      await client.api('/opportunities', { ...options, body: '{"notes":"berubah"}' })
      assert.ok(writes.every((body) => body === options.body))
      assert.equal(client.getPendingWrite(key), undefined)
    },
  )
  await t.test(
    'HTTP 200 dengan JSON tidak valid tetap uncertain dan mempertahankan payload',
    async () => {
      t.mock.method(
        globalThis,
        'fetch',
        async () =>
          new Response('<html>gateway response</html>', {
            status: 200,
            headers: { 'Content-Type': 'text/html' },
          }),
      )
      const key = crypto.randomUUID()
      await assert.rejects(
        client.api('/targets/batch', { method: 'POST', body: '{}', requestKey: key }),
        (error) => error.uncertain === true,
      )
      assert.equal(client.getPendingWrite(key).options.body, '{}')
    },
  )
  await t.test('respons 401 sesi lama tidak menghapus sesi baru', async () => {
    let release
    const pending = new Promise((resolve) => {
      release = resolve
    })
    t.mock.method(globalThis, 'fetch', () => pending)
    let unauthorized = false
    client.setUnauthorizedHandler(() => {
      unauthorized = true
    })
    client.saveToken('old-session')
    const request = client.api('/me')
    client.saveToken('new-session')
    release(Response.json({ message: 'Unauthenticated.' }, { status: 401 }))
    await assert.rejects(request, (error) => error.staleSession === true)
    assert.equal(client.getToken(), 'new-session')
    assert.equal(unauthorized, false)
  })
  const division = { id: 1, name: 'Komersil', code: 'komersil' }
  const pic = { id: 1, name: 'Suci' }
  const product = {
    id: 1,
    name: 'Tabungan',
    code: 'tabungan',
    measure: 'IDR',
    divisions: [division],
  }
  const date = new Date().toLocaleDateString('en-CA')
  let record = {
    id: 1,
    version: 1,
    division,
    pic,
    product,
    customer_name: 'Audit customer',
    recorded_date: date,
    segment: 'Mid',
    nominal: '1000',
    interest_status: 'Hot',
    outcome: 'Active',
    notes: 'Notes',
  }
  let closingCalls = 0
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    const path = new URL(url, 'http://localhost').pathname.replace('/api', '')
    if (path.endsWith('/closing')) {
      closingCalls++
      if (closingCalls > 1) return Response.json(record)
      record = { ...record, outcome: 'Won', version: 2, realization: '1000', closed_date: date }
      throw new TypeError('response lost after commit')
    }
    const responses = {
      '/divisions': [division],
      '/products': [product],
      '/pics': [pic],
      '/opportunities': { data: [record], last_page: 1 },
      '/targets': [],
      '/branch-targets': [],
      '/dashboard': { follow_ups: [] },
    }
    assert.ok(path in responses, path)
    return Response.json(responses[path])
  })
  const { useSession } = await server.ssrLoadModule('/src/composables/useSession.js')
  const { usePipeline } = await server.ssrLoadModule('/src/composables/usePipeline.js')
  const session = useSession(),
    pipeline = usePipeline()
  session.user.value = {
    backendId: 1,
    name: 'Suci',
    division: 'Komersil',
    divisionId: 1,
    role: 'pic',
  }
  await nextTick()
  await pipeline.refresh()
  await t.test('simpan peluang dengan respons HTML 200 ditolak tanpa mengubah state', async () => {
    const normalFetch = globalThis.fetch
    const mocked = t.mock.method(globalThis, 'fetch', async (url, options) => {
      if (options.method === 'POST' && url.endsWith('/opportunities'))
        return new Response('<html>gateway</html>', { status: 200 })
      return normalFetch(url, options)
    })
    try {
      const draft = { ...pipeline.rows.value[0], id: undefined, customer: 'Never saved' }
      await assert.rejects(pipeline.save(draft), (error) => error.uncertain === true)
      assert.equal(record.customer_name, 'Audit customer')
      assert.equal(
        pipeline.rows.value.some((row) => row.customer === 'Never saved'),
        false,
      )
    } finally {
      mocked.mock.restore()
    }
  })
  await t.test(
    'retry closing mencapai receipt walaupun refresh menemukan closing tersimpan',
    async () => {
      assert.equal(pipeline.storageError.value, '')
      const draft = {
        ...pipeline.rows.value[0],
        outcome: 'Won',
        closedDate: date,
        realization: 1000,
      }
      const options = { requestKey: crypto.randomUUID() }
      await assert.rejects(pipeline.save(draft, options), (error) => error.uncertain === true)
      await pipeline.refresh()
      assert.equal(pipeline.rows.value[0].outcome, 'Won')
      const saved = await pipeline.save(draft, options)
      assert.equal(saved.outcome, 'Won')
      assert.equal(saved.version, 2)
      assert.equal(closingCalls, 2)
      assert.equal(client.getPendingWrite(options.requestKey), undefined)
    },
  )
  await t.test('pemulihan profil sesi lama tidak menimpa akun yang baru login', async () => {
    session.user.value = null
    await nextTick()
    client.saveToken('old-initialization')
    let release
    const deferred = new Promise((resolve) => {
      release = resolve
    })
    const normalFetch = globalThis.fetch
    t.mock.method(globalThis, 'fetch', (url, options) => {
      if (url.endsWith('/me')) return deferred
      if (url.endsWith('/login'))
        return Promise.resolve(
          Response.json({
            token: 'new-login',
            user: {
              id: 2,
              username: 'new-user',
              name: 'New User',
              role: 'pic',
              division,
              division_id: 1,
            },
          }),
        )
      return normalFetch(url, options)
    })
    const initializing = session.initialize()
    await session.login('new-user', true, 'test-password')
    release(Response.json({ message: 'Unauthenticated.' }, { status: 401 }))
    await initializing
    assert.equal(session.user.value.id, 'new-user')
    assert.equal(client.getToken(), 'new-login')
    await pipeline.refresh()
  })
  session.user.value = null
})
