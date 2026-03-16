<template>
  <div v-if="detail" class="page-grid">
    <div class="page-card">
      <div class="section-title">告警面板</div>
      <warning-list :warnings="detail.warnings" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';

import WarningList from '@/components/WarningList.vue';
import { usePlanStore } from '@/store/plan';

const route = useRoute();
const store = usePlanStore();
const detail = computed(() => store.selectedPlanDetail);

onMounted(() => {
  store.fetchPlan(Number(route.params.id));
});
</script>
