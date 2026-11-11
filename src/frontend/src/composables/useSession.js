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
const sessionNotice = ref('')
setUnauthorizedHandler((message) => {
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
    sessionNotice.value = ''
    saveToken(response.token, remember)
    user.value = normalizeUser(response.user)
    return user.value
  }
  async function logout() {
    try {
      if (getToken()) await api('/logout', { method: 'POST' })
    } catch {
      // Local logout always finishes, even when the server cannot be reached.
    } finally {
      clearToken()
      clearPendingWrites()
      user.value = null
    }
  }
  return { user, sessionNotice, login, logout, initialize }
}
