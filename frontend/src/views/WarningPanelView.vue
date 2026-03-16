<template>
  <div v-if="detail" class="page-shell">
    <v-card class="page-card">
      <v-card-text>
        <div class="toolbar-row">
          <div>
            <div class="section-title">告警面板</div>
            <div class="muted-text">集中查看当前配载方案产生的所有告警记录。</div>
          </div>
          <v-chip color="warning" variant="tonal">告警总数 {{ detail.warnings.length }}</v-chip>
        </div>
        <div class="mt-4">
          <warning-list :warnings="detail.warnings" />
        </div>
      </v-card-text>
    </v-card>
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
