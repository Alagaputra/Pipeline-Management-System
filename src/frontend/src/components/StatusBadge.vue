<script setup>
defineProps({ status: String })
</script>
<template>
  <span class="status-badge" :class="status?.toLowerCase()"
    ><span class="status-dot"></span>{{ status }}</span
  >
</template>
