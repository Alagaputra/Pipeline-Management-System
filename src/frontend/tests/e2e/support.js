import { expect } from '@playwright/test'

const tokens = new Map()
export async function ready(page) {
  await expect(page.getByText('Terhubung ke server', { exact: true })).toBeVisible({
    timeout: 15000,
  })
}
export async function login(page, username = 'suci') {
  if (tokens.has(username)) {
    await page.addInitScript(
      (token) => localStorage.setItem('pipeline-api-token', token),
      tokens.get(username),
    )
    await page.goto('/')
    await ready(page)
    return
  }
  await page.goto('/')
  await page.getByLabel('Username').fill(username)
  await page.getByLabel('Password', { exact: true }).fill('demo123')
  await page.getByRole('button', { name: 'Masuk', exact: true }).click()
  await ready(page)
  tokens.set(
    username,
    await page.evaluate(
      () =>
        localStorage.getItem('pipeline-api-token') || sessionStorage.getItem('pipeline-api-token'),
    ),
  )
}
export async function request(page, path, options = {}) {
  return page.evaluate(
    async ({ path, options }) => {
      const token =
        localStorage.getItem('pipeline-api-token') || sessionStorage.getItem('pipeline-api-token')
      const response = await fetch('/api' + path, {
        ...options,
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          ...options.headers,
        },
        body: options.body ? JSON.stringify(options.body) : undefined,
      })
      return { status: response.status, body: await response.json() }
    },
    { path, options },
  )
}
