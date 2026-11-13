import { reactive } from 'vue'
export const confirmation = reactive({
  open: false,
  title: '',
  message: '',
  confirmLabel: '',
  danger: false,
})
let resolveConfirmation, pending
// Pemanggil menunggu Promise; ConfirmDialog meneruskannya melalui answerConfirmation.
// Jika dialog masih terbuka, gunakan Promise yang sama agar konfirmasi tidak bertumpuk.
export function confirmAction({
  title = 'Batalkan perubahan?',
  message = 'Perubahan yang belum disimpan akan hilang.',
  confirmLabel = 'Buang perubahan',
  danger = true,
} = {}) {
  if (confirmation.open) return pending
  Object.assign(confirmation, { open: true, title, message, confirmLabel, danger })
  pending = new Promise((resolve) => {
    resolveConfirmation = resolve
  })
  return pending
}
export function answerConfirmation(value) {
  confirmation.open = false
  resolveConfirmation?.(value)
  resolveConfirmation = null
}
