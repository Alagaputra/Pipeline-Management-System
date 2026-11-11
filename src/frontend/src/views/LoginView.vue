<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSession } from '../composables/useSession'
import AppIcon from '../components/AppIcon.vue'
const name = ref(''),
  password = ref(''),
  visible = ref(false),
  remember = ref(true),
  error = ref('')
const busy = ref(false)
const { sessionNotice } = useSession()
const router = useRouter()
async function submit() {
  if (busy.value) return
  error.value = ''
  busy.value = true
  try {
    await useSession().login(name.value, remember.value, password.value)
    await router.push('/')
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}
</script>
<template>
  <div class="login-page">
    <div class="login-decoration circle-one"></div>
    <div class="login-decoration circle-two"></div>
    <div class="login-brand">
      <span class="brand-symbol">p<span></span></span>pipeline
    </div>
    <div class="login-content">
      <span class="login-kicker">SETIAP PELUANG, SATU LANGKAH LEBIH DEKAT.</span>
      <h1>Pipeline Management System<span>.</span></h1>
      <p class="login-subtitle">Kelola peluang. Jaga hubungan.<br />Capai target bersama tim.</p>
      <div class="login-card">
        <h2>Selamat datang kembali</h2>
        <p v-if="sessionNotice" class="notice closing-note" role="status">{{ sessionNotice }}</p>
        <form @submit.prevent="submit">
          <label for="username">Username</label>
          <div class="input-icon">
            <AppIcon name="team" :size="18" /><input
              id="username"
              v-model="name"
              required
              maxlength="40"
              autocomplete="username"
              placeholder="Masukkan username"
            />
          </div>
          <label for="password">Password</label>
          <div class="input-icon">
            <AppIcon name="bank" :size="18" /><input
              id="password"
              v-model="password"
              :type="visible ? 'text' : 'password'"
              required
              autocomplete="current-password"
              placeholder="Masukkan password"
            /><button
              type="button"
              class="icon-button"
              :aria-label="visible ? 'Sembunyikan password' : 'Tampilkan password'"
              @click="visible = !visible"
            >
              <AppIcon :name="visible ? 'eyeOff' : 'eye'" :size="18" />
            </button>
          </div>
          <label class="checkbox-row"
            ><input v-model="remember" type="checkbox" /> Ingat saya</label
          >
          <p v-if="error" class="notice error" role="alert">{{ error }}</p>
          <button class="button primary login-submit" :disabled="busy">
            {{ busy ? 'Menghubungkan...' : 'Masuk' }} <AppIcon name="arrow" :size="18" />
          </button>
        </form>
      </div>
    </div>
    <footer class="login-footer">Pipeline Funding Management System</footer>
  </div>
</template>
