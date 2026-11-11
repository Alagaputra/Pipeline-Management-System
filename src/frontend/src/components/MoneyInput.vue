<script setup>
import { computed, nextTick } from 'vue'
const props = defineProps({ modelValue: [String, Number] })
const emit = defineEmits(['update:modelValue'])
const display = computed(() => {
  const raw = String(props.modelValue ?? '')
  return /^\d+$/.test(raw) ? raw.replace(/\B(?=(\d{3})+(?!\d))/g, '.') : raw
})
async function input(event) {
  const element = event.target
  const before = element.value.slice(0, element.selectionStart).replace(/\./g, '').length
  const raw = element.value.replace(/\./g, '')
  emit('update:modelValue', raw)
  await nextTick()
  element.value = display.value
  let position = 0,
    digits = 0
  while (position < element.value.length && digits < before) {
    if (element.value[position] !== '.') digits++
    position++
  }
  element.setSelectionRange(position, position)
}
</script>
<template>
  <input type="text" inputmode="numeric" :value="display" @input="input" />
</template>
