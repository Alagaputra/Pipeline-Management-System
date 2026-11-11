<script setup>
import { ref, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import ConfirmDialog from './components/ConfirmDialog.vue'
import { connectionProblem } from './services/api'
import AppSidebar from './components/AppSidebar.vue'
import AppIcon from './components/AppIcon.vue'
import { DIVISIONS } from './data/access'
import { usePipeline } from './composables/usePipeline'
const route = useRoute()
const menuOpen = ref(false)
const {
  storageError,
  storageNotice,
  loading,
  refresh,
  division,
  divisionLabel,
  headDivision,
  isHead,
} = usePipeline()
async function closeNavigation() {
  menuOpen.value = false
  await nextTick()
  document.getElementById('navigation-toggle')?.focus()
}
function focusContent() {
  document.getElementById('main')?.focus()
}
watch(
  () => route.path,
  () => {
    menuOpen.value = false
  },
)
</script>
<template>
  <RouterView v-if="route.path === '/login'" />
  <div v-else class="app-shell">
    <a class="skip-link" href="#main" @click.prevent="focusContent">Langsung ke konten</a>
    <AppSidebar :open="menuOpen" @close="closeNavigation" />
    <div class="workspace" :inert="menuOpen">
      <header class="topbar">
        <div class="breadcrumb">
          <button
            id="navigation-toggle"
            class="icon-button mobile-menu"
            aria-controls="app-sidebar"
            aria-label="Buka navigasi"
            :aria-expanded="menuOpen"
            @click="menuOpen = !menuOpen"
          >
            <AppIcon name="menu" /></button
          ><span>Ruang kerja</span><AppIcon name="right" :size="14" /><strong>{{
            route.meta.title
          }}</strong>
        </div>
        <span class="workspace-label"
          ><span class="live-dot"></span>
          {{
            storageError || connectionProblem
              ? 'Koneksi bermasalah'
              : loading
                ? 'Memuat data...'
                : 'Terhubung ke server'
          }}
        </span>
      </header>
      <main id="main" tabindex="-1">
        <div class="division-toolbar">
          <div>
            <strong>{{ divisionLabel }}</strong>
          </div>
          <label v-if="isHead"
            >Tampilan divisi
            <select v-model="headDivision" aria-label="Pilih divisi">
              <option value="all">Semua Divisi</option>
              <option v-for="item in DIVISIONS" :key="item">{{ item }}</option>
            </select>
          </label>
        </div>
        <p v-if="storageError" class="notice error" role="alert">
          {{ storageError }}
          <button type="button" class="text-button" :disabled="loading" @click="refresh">
            Coba lagi
          </button>
        </p>
        <p v-else-if="loading" class="notice closing-note" role="status">
          Mengambil data terbaru dari server...
        </p>
        <p v-if="storageNotice" class="notice success" role="status">
          {{ storageNotice }}
          <button type="button" class="text-button" :disabled="loading" @click="refresh">
            Perbarui ringkasan</button
          ><button class="icon-button" aria-label="Tutup pemberitahuan" @click="storageNotice = ''">
            <AppIcon name="close" :size="16" />
          </button>
        </p>
        <RouterView :key="route.path + division" />
      </main>
      <footer class="app-footer">
        <span>Pipeline Funding Management</span>
      </footer>
    </div>
  </div>
  <ConfirmDialog />
</template>
