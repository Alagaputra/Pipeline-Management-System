<script setup>
import TargetCard from './TargetCard.vue'
defineProps({ item: Object })
</script>
<template>
  <TargetCard :item="item" :label="'Pencapaian ' + item.product" />
</template>
