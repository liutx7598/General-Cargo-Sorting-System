<template>
  <div class="metric-grid">
    <v-card v-for="card in cards" :key="card.label" class="metric-card">
      <v-card-text>
        <div class="metric-label">{{ card.label }}</div>
        <div class="metric-value">{{ format(card.value) }}</div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
defineProps<{
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

<style scoped>
.metric-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.metric-card {
  background: rgba(255, 255, 255, 0.96);
}

.metric-label {
  color: #6b7b8c;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
}
</style>
