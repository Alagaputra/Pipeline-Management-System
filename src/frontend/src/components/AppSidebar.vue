<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useSession } from '../composables/useSession'
import AppIcon from './AppIcon.vue'
const props = defineProps({ open: Boolean })
const sidebar = ref(null)
const mobileQuery = window.matchMedia('(max-width: 760px)')
const mobile = ref(mobileQuery.matches)
let previousOverflow = ''
const updateMobile = () => {
  mobile.value = mobileQuery.matches
  if (!mobile.value) emit('close')
}
mobileQuery.addEventListener('change', updateMobile)
const emit = defineEmits(['close'])
const { user, logout } = useSession()
const router = useRouter()
const nav = [
  { to: '/', icon: 'dashboard', label: 'Dashboard' },
  { to: '/pipeline', icon: 'pipeline', label: 'Pipeline' },
  { to: '/target', icon: 'target', label: 'Target' },
  { to: '/history', icon: 'history', label: 'Riwayat' },
  { to: '/tim', icon: 'team', label: 'Tim' },
]
async function signOut() {
  await logout()
  await router.push('/login')
}
watch(
  () => props.open,
  async (open) => {
    if (open) {
      previousOverflow = document.body.style.overflow
      document.body.style.overflow = 'hidden'
      await nextTick()
      sidebar.value?.querySelector('a')?.focus()
    } else document.body.style.overflow = previousOverflow
  },
)
function keydown(event) {
  if (!props.open) return
  if (event.key === 'Escape') {
    event.preventDefault()
    emit('close')
    return
  }
  if (event.key !== 'Tab') return
  const elements = [...sidebar.value.querySelectorAll('a,button')].filter(
    (element) => !element.disabled && element.getClientRects().length,
  )
  const first = elements[0],
    last = elements.at(-1)
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last?.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first?.focus()
  }
}
document.addEventListener('keydown', keydown)
onBeforeUnmount(() => {
  mobileQuery.removeEventListener('change', updateMobile)
  document.removeEventListener('keydown', keydown)
  if (props.open) document.body.style.overflow = previousOverflow
})
</script>
<template>
  <button
    v-if="open"
    class="sidebar-backdrop"
    aria-label="Tutup navigasi"
    @click="emit('close')"
  ></button>
  <aside
    ref="sidebar"
    id="app-sidebar"
    class="sidebar"
    :class="{ open }"
    :inert="mobile && !open"
    :aria-hidden="mobile && !open"
  >
    <RouterLink to="/" class="brand" @click="emit('close')"
      ><span class="brand-symbol">p<span></span></span
      ><span>pipeline<small>FUNDING MANAGEMENT</small></span></RouterLink
    >
    <div class="nav-label">RUANG KERJA</div>
    <nav aria-label="Navigasi utama">
      <RouterLink
        v-for="item in nav"
        :key="item.to"
        :to="item.to"
        :class="{
          active: item.to === '/' ? $route.path === '/' : $route.path.startsWith(item.to),
        }"
        @click="emit('close')"
        ><AppIcon :name="item.icon" /><span>{{ item.label }}</span
        ><AppIcon name="right" :size="15"
      /></RouterLink>
    </nav>
    <div class="sidebar-bottom">
      <div class="sidebar-tip">
        <span class="tip-icon"><AppIcon name="growth" /></span
        ><strong>Langkah kecil,<br />peluang besar.</strong>
        <p>Follow-up tepat waktu untuk hasil yang lebih baik.</p>
      </div>
      <div class="user-profile">
        <span class="avatar">{{ user?.name?.slice(0, 2).toUpperCase() }}</span
        ><span
          ><strong>{{ user?.name }}</strong
          ><small>{{ user?.role === 'head' ? 'Head Funding' : user?.division }}</small></span
        ><button class="icon-button" aria-label="Keluar" title="Keluar" @click="signOut">
          <AppIcon name="logout" :size="18" />
        </button>
      </div>
    </div>
  </aside>
</template>
