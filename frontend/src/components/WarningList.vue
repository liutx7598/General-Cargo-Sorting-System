<template>
  <div v-if="warnings.length" class="warning-table-shell">
    <table class="data-table">
      <thead>
        <tr>
          <th>类型</th>
          <th>信息</th>
          <th>级别</th>
          <th>货物 ID</th>
          <th>货舱 ID</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="warning in warnings"
          :key="warning.id ?? `${warning.planId}-${warning.warningType}-${warning.warningMessage}`"
        >
          <td>{{ warning.warningType }}</td>
          <td>{{ warning.warningMessage }}</td>
          <td>
            <v-chip size="small" :color="warning.severity === 'ERROR' ? 'error' : 'warning'" variant="tonal">
              {{ formatSeverity(warning.severity) }}
            </v-chip>
          </td>
          <td>{{ warning.cargoId ?? '-' }}</td>
          <td>{{ warning.holdId ?? '-' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <v-alert v-else type="success" variant="tonal" text="当前没有告警记录。" />
</template>

<script setup lang="ts">
import type { WarningRecord } from '@/types';
import { formatSeverity } from '@/utils/formatters';

defineProps<{ warnings: WarningRecord[] }>();
</script>

<style scoped>
.warning-table-shell {
  overflow-x: auto;
}
</style>
