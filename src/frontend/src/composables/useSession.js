import { ref } from 'vue'
import { answerConfirmation } from './useConfirm'
import {
  api,
  clearToken,
  getToken,
  saveToken,
  setUnauthorizedHandler,
  clearPendingWrites,
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
  if (!initialization)
    initialization = api('/me')
      .then((value) => (user.value = normalizeUser(value)))
      .catch((error) => {
        if (error.status === 401) clearToken()
        sessionNotice.value = error.message
        user.value = null
      })
      .finally(() => (initialization = null))
  return initialization
}

export function useSession() {
  async function login(name, remember, password) {
    const response = await api('/login', {
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
    try {
      if (getToken()) await api('/logout', { method: 'POST' })
    } catch {
      // Keluar di perangkat tetap diselesaikan meskipun server tidak dapat dijangkau.
    } finally {
      clearToken()
      clearPendingWrites()
      user.value = null
    }
  }
  return { user, sessionNotice, login, logout, initialize }
}
