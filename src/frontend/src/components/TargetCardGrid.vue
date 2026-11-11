<template>
  <div class="target-cards-grid"><slot /></div>
</template>
<style scoped>
.target-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr));
  gap: 16px;
}
</style>
