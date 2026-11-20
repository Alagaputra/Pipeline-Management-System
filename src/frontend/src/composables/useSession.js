import { ref } from 'vue'
import { answerConfirmation } from './useConfirm'
import {
  api,
  clearToken,
  getToken,
  saveToken,
  setUnauthorizedHandler,
  clearPendingWrites,
  getSessionVersion,
} from '../services/api'

const user = ref(null)
// Satu state sesi digunakan oleh router, shell aplikasi, dan seluruh composable.
const sessionNotice = ref('')
setUnauthorizedHandler((message) => {
  // API 401 menutup konfirmasi yang tertunda dan memicu router kembali ke login.
  answerConfirmation(false)
  clearToken()
  user.value = null
  sessionNotice.value = message
})
let initialization

const normalizeUser = (value) => ({
  id: value.username,
  backendId: value.id,
  name: value.name,
  division: value.division?.name || null,
  divisionId: value.division_id,
  role: value.role,
})

async function initialize() {
  // Pulihkan akun dari token saat aplikasi dibuka. Bagikan promise yang sama agar
  // beberapa pemanggil tidak mengirim /me secara bersamaan.
  if (user.value || !getToken()) return user.value
  const token = getToken(),
    version = getSessionVersion()
  const current = () => token === getToken() && version === getSessionVersion()
  if (!initialization || initialization.token !== token || initialization.version !== version) {
    const entry = { token, version }
    entry.promise = api('/me')
      .then((value) => {
        if (current()) user.value = normalizeUser(value)
        return user.value
      })
      .catch((error) => {
        if (!current() || error.staleSession) return user.value
        if (error.status === 401) clearToken()
        sessionNotice.value = error.message
        user.value = null
      })
      .finally(() => {
        if (initialization === entry) initialization = null
      })
    initialization = entry
  }
  return initialization.promise
}

export function useSession() {
  async function login(name, remember, password) {
    const response = await api('/login', {
      validateResponse: (value) =>
        typeof value.token === 'string' &&
        value.token.length > 0 &&
        value.user?.id &&
        value.user.username,
      method: 'POST',
      body: JSON.stringify({ username: name.trim().toLowerCase(), password }),
    })
    clearPendingWrites()
    // Retry dari sesi sebelumnya tidak boleh terbawa ke akun yang baru masuk.
    sessionNotice.value = ''
    saveToken(response.token, remember)
    user.value = normalizeUser(response.user)
    return user.value
  }
  async function logout() {
    const token = getToken(),
      version = getSessionVersion()
    try {
      if (getToken()) await api('/logout', { method: 'POST' })
    } catch {
      // Keluar di perangkat tetap diselesaikan meskipun server tidak dapat dijangkau.
    } finally {
      if (token === getToken() && version === getSessionVersion()) {
        clearToken()
        clearPendingWrites()
        user.value = null
      }
    }
  }
  return { user, sessionNotice, login, logout, initialize }
}
