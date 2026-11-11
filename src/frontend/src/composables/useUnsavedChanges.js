import { onBeforeUnmount } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { confirmAction } from './useConfirm'
import { useSession } from './useSession'
export function useUnsavedChanges(dirty, saving) {
  const { user } = useSession()
  onBeforeRouteLeave(async () => {
    if (!user.value) return true
    if (saving?.value) return false
    return !dirty.value || (await confirmAction())
  })
  const beforeUnload = (event) => {
    if (user.value && (dirty.value || saving?.value)) {
      event.preventDefault()
      event.returnValue = ''
    }
  }
  window.addEventListener('beforeunload', beforeUnload)
  onBeforeUnmount(() => window.removeEventListener('beforeunload', beforeUnload))
}
