<script setup>
import { PRODUCT_COLORS } from '../utils/productColors'
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import { compactMoney, money, percent } from '../utils/pipeline'

const props = defineProps({ items: Array, label: String })
const colors = PRODUCT_COLORS
const total = computed(() => props.items.reduce((sum, item) => sum + item.value, 0))
const portions = computed(() =>
  props.items.map((item) => ({
    ...item,
    percentage: total.value ? (item.value / total.value) * 100 : 0,
  })),
)
const background = computed(() => {
  if (!total.value) return '#eeebf4'
  let start = 0
  const stops = portions.value.map((item) => {
    const end = start + item.percentage
    const stop = `${colors[item.product]} ${start}% ${end}%`
    start = end
    return stop
  })
  return `conic-gradient(${stops.join(', ')})`
})
const description = computed(
  () =>
    `${props.label}: ${money(total.value)}. ` +
    portions.value
      .map((item) => `${item.product} ${money(item.value)}, ${percent(item.percentage)}`)
      .join('; '),
)
</script>
<template>
  <div class="product-distribution">
    <div class="distribution-donut" :style="{ background }" role="img" :aria-label="description">
      <div class="distribution-center">
        <AppIcon name="wallet" :size="21" /><strong>{{ compactMoney(total) }}</strong
        ><small>{{ label }}</small>
      </div>
    </div>
    <div class="distribution-legend">
      <div v-for="item in portions" :key="item.product" class="distribution-item">
        <div class="distribution-title">
          <span><i :style="{ backgroundColor: colors[item.product] }"></i>{{ item.product }}</span
          ><strong>{{ percent(item.percentage) }}</strong>
        </div>
        <div class="distribution-track">
          <span
            :style="{ width: item.percentage + '%', backgroundColor: colors[item.product] }"
          ></span>
        </div>
        <small :title="money(item.value)">{{ compactMoney(item.value) }}</small>
      </div>
      <p v-if="!total" class="distribution-empty">Belum ada nominal untuk ditampilkan.</p>
    </div>
  </div>
</template>
