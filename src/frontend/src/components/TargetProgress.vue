<script setup>
import TargetCard from './TargetCard.vue'
import { moneyInMillions } from '../utils/pipeline'
defineProps({ item: Object, monthLabel: String, monthlyTarget: [String, Number] })
</script>
<template>
  <TargetCard :item="item" :label="'Pencapaian ' + item.product">
    <p v-if="monthLabel">Target {{ monthLabel }} &middot; {{ moneyInMillions(monthlyTarget) }}</p>
  </TargetCard>
</template>
