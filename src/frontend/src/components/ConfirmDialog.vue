<script setup>
import { ref, watch, nextTick } from 'vue'
import { confirmation, answerConfirmation } from '../composables/useConfirm'
const dialog = ref(null)
let previousFocus
watch(
  () => confirmation.open,
  async (open) => {
    await nextTick()
    if (open) {
      previousFocus = document.activeElement
      dialog.value?.showModal()
    } else {
      dialog.value?.close()
      previousFocus?.focus()
    }
  },
)
</script>
<template>
  <dialog
    ref="dialog"
    class="confirm-dialog"
    aria-labelledby="confirmation-title"
    aria-describedby="confirmation-description"
    @cancel.prevent="answerConfirmation(false)"
  >
    <h2 id="confirmation-title">{{ confirmation.title }}</h2>
    <p id="confirmation-description">{{ confirmation.message }}</p>
    <div class="confirm-actions">
      <button autofocus type="button" class="button secondary" @click="answerConfirmation(false)">
        Lanjut mengisi
      </button>
      <button
        type="button"
        class="button"
        :class="confirmation.danger ? 'confirm-danger' : 'primary'"
        @click="answerConfirmation(true)"
      >
        {{ confirmation.confirmLabel }}
      </button>
    </div>
  </dialog>
</template>
<style scoped>
.confirm-dialog {
  margin: auto;
  padding: 28px;
  width: min(440px, calc(100vw - 32px));
  border: 1px solid #e8e2f0;
  border-radius: 18px;
  color: #332b44;
  background: #fff;
  box-shadow: 0 20px 80px #21152b33;
}
.confirm-dialog::backdrop {
  background: #251c3a66;
}
h2 {
  font-size: 20px;
}
p {
  margin: 14px 0 24px;
  color: #716b80;
  font-size: 14px;
  line-height: 1.6;
}
.confirm-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}
.confirm-danger {
  background: #b83252;
  color: #fff;
}
@media (max-width: 420px) {
  .confirm-dialog {
    padding: 22px;
  }
  .confirm-actions {
    flex-direction: column;
  }
}
</style>
