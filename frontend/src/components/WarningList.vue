<template>
  <el-table :data="warnings" stripe>
    <el-table-column prop="warningType" label="类型" width="140" />
    <el-table-column prop="warningMessage" label="信息" min-width="280" />
    <el-table-column label="级别" width="120">
      <template #default="{ row }">
        <el-tag :type="row.severity === 'ERROR' ? 'danger' : 'warning'">{{ formatSeverity(row.severity) }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="cargoId" label="货物ID" width="110" />
    <el-table-column prop="holdId" label="货舱ID" width="110" />
  </el-table>
</template>

<script setup lang="ts">
import type { WarningRecord } from '@/types';

defineProps<{ warnings: WarningRecord[] }>();

function formatSeverity(severity: string) {
  const severityMap: Record<string, string> = {
    ERROR: '严重',
    WARNING: '警告',
  };
  return severityMap[severity] ?? severity;
}
</script>
