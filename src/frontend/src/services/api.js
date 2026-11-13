import { ref } from 'vue'
const API_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')
const TOKEN_KEY = 'pipeline-api-token'
// Simpan payload asli selama hasil tulis belum pasti; retry dengan key yang sama
// harus mengirim method/path/body yang sama ke middleware IdempotentWrite Laravel.
const pendingWrites = new Map()
let unauthorizedHandler = () => {}
export const connectionProblem = ref('')
export const getToken = () => localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY)
export const setUnauthorizedHandler = (handler) => {
  unauthorizedHandler = handler
}
export function clearPendingWrites() {
  pendingWrites.clear()
}
export function saveToken(token, remember = true) {
  // Ingat saya memakai localStorage; sesi biasa hanya bertahan di sessionStorage.
  clearToken()
  ;(remember ? localStorage : sessionStorage).setItem(TOKEN_KEY, token)
}
export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(TOKEN_KEY)
}
export async function api(path, options = {}) {
  // Alur bersama: siapkan token/key -> fetch dengan timeout -> normalisasi hasil/error.
  const { requestKey, timeoutMs = 15000, ...supplied } = options
  if (requestKey) {
    if (!pendingWrites.has(requestKey)) pendingWrites.set(requestKey, { path, options: supplied })
    const pending = pendingWrites.get(requestKey)
    path = pending.path
    supplied.method = pending.options.method
    supplied.body = pending.options.body
  }
  const headers = { Accept: 'application/json', ...(supplied.headers || {}) }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  if (requestKey) headers['Idempotency-Key'] = requestKey
  if (supplied.body && !(supplied.body instanceof FormData))
    headers['Content-Type'] = 'application/json'
  const controller = new AbortController()
  // Timeout membatalkan penantian browser; server mungkin sudah menyimpan perubahan.
  const timeout = setTimeout(() => controller.abort(), timeoutMs)
  const signal = supplied.signal
    ? AbortSignal.any([supplied.signal, controller.signal])
    : controller.signal
  try {
    const response = await fetch(`${API_URL}${path}`, { ...supplied, signal, headers })
    const payload =
      response.status === 204
        ? null
        : await response.json().catch((error) => {
            if (controller.signal.aborted) throw error
            return {}
          })
    if (!response.ok) {
      const validation = payload?.errors ? Object.values(payload.errors).flat()[0] : ''
      const message =
        response.status >= 500
          ? 'Layanan sedang bermasalah. Coba lagi.'
          : response.status === 429
            ? 'Terlalu banyak percobaan. Tunggu sebentar lalu coba lagi.'
            : response.status === 401
              ? 'Sesi telah berakhir. Silakan masuk kembali.'
              : response.status === 409
                ? payload.message || 'Data telah berubah. Muat data terbaru.'
                : validation || payload?.message || 'Permintaan tidak dapat diproses.'
      const error = new Error(message)
      error.status = response.status
      error.fields = payload?.errors || {}
      error.uncertain = Boolean(requestKey && response.status >= 500)
      // Pertahankan payload pada kegagalan server/jaringan karena hasil tulis belum pasti.
      // Validasi atau konflik yang sudah jelas mengakhiri percobaan tersebut.
      if (!error.uncertain && requestKey) pendingWrites.delete(requestKey)
      if (response.status === 401 && path !== '/login') {
        // Sesi kedaluwarsa: hapus token, buang retry akun lama, dan beri tahu useSession.
        clearToken()
        clearPendingWrites()
        unauthorizedHandler(message)
      }
      if (response.status >= 500) connectionProblem.value = message
      throw error
    }
    connectionProblem.value = ''
    if (requestKey) pendingWrites.delete(requestKey)
    return payload
  } catch (error) {
    if (error.status) throw error
    const message = controller.signal.aborted
      ? 'Permintaan terlalu lama. Coba lagi untuk memastikan penyimpanan.'
      : 'Koneksi terputus. Periksa jaringan lalu coba lagi.'
    connectionProblem.value = message
    const networkError = new Error(message)
    networkError.uncertain = Boolean(requestKey)
    throw networkError
  } finally {
    clearTimeout(timeout)
  }
}
