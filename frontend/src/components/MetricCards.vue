<template>
  <div class="page-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
    <div v-for="card in cards" :key="card.label" class="page-card">
      <div style="color: #64748b;">{{ card.label }}</div>
      <div class="metric-value">{{ format(card.value) }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  cards: Array<{ label: string; value: number | string | undefined }>;
}>();

function format(value: number | string | undefined) {
  if (value === undefined || value === null) {
    return '-';
  }
  if (typeof value === 'number') {
    return value.toFixed(2);
  }
  return value;
}
</script>

