<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import AppIcon from './AppIcon.vue'
defineProps({ title: String, subtitle: String })
const emit = defineEmits(['close'])
const dialog = ref(null)
let previousFocus
let overflow
onMounted(() => {
  previousFocus = document.activeElement
  overflow = document.body.style.overflow
  document.body.style.overflow = 'hidden'
  dialog.value.showModal()
})
onBeforeUnmount(() => {
  document.body.style.overflow = overflow
  previousFocus?.focus()
})
</script>
<template>
  <dialog
    ref="dialog"
    class="app-drawer"
    aria-labelledby="drawer-title"
    @cancel.prevent="emit('close')"
    @click="
      (event) => {
        if (event.target === dialog) emit('close')
      }
    "
  >
    <div class="drawer-surface">
      <header class="drawer-header">
        <div>
          <span v-if="subtitle" class="eyebrow">{{ subtitle }}</span>
          <h2 id="drawer-title">{{ title }}</h2>
        </div>
        <button type="button" class="icon-button" aria-label="Tutup panel" @click="emit('close')">
          <AppIcon name="close" />
        </button>
      </header>
      <div class="drawer-body"><slot /></div>
    </div>
  </dialog>
</template>
