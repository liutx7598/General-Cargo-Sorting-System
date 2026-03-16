<template>
  <div class="page-grid">
    <div class="page-card">
      <div class="section-title">航次管理</div>
      <el-form :model="voyageForm" inline>
        <el-form-item label="航次号"><el-input v-model="voyageForm.voyageNo" /></el-form-item>
        <el-form-item label="船舶">
          <el-select v-model="voyageForm.shipId" style="width: 220px;">
            <el-option v-for="ship in store.ships" :key="ship.id" :label="ship.shipName" :value="ship.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="航线"><el-input v-model="voyageForm.routeInfo" /></el-form-item>
        <el-form-item label="起运港"><el-input v-model="voyageForm.departurePort" /></el-form-item>
        <el-form-item label="到达港"><el-input v-model="voyageForm.arrivalPort" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="voyageForm.status" style="width: 180px;">
            <el-option label="规划中" value="PLANNING" />
            <el-option label="草稿" value="DRAFT" />
            <el-option label="已生成" value="GENERATED" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveVoyage">保存航次</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="page-card">
      <el-table :data="store.voyages" stripe>
        <el-table-column prop="voyageNo" label="航次号" width="180" />
        <el-table-column prop="routeInfo" label="航线" />
        <el-table-column prop="departurePort" label="起运港" width="120" />
        <el-table-column prop="arrivalPort" label="到达港" width="120" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">{{ formatStatus(row.status) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue';
import { ElMessage } from 'element-plus';

import { usePlanStore } from '@/store/plan';
import type { Voyage } from '@/types';

const store = usePlanStore();

function buildSuffix() {
  return `${Date.now().toString().slice(-6)}${Math.floor(Math.random() * 100)
    .toString()
    .padStart(2, '0')}`;
}

function createVoyageForm(): Voyage {
  const suffix = buildSuffix();
  return {
    voyageNo: `VY-${suffix}`,
    shipId: 1,
    routeInfo: '上海 -> 釜山',
    departurePort: '上海',
    arrivalPort: '釜山',
    status: 'PLANNING',
  };
}

const voyageForm = reactive<Voyage>(createVoyageForm());

onMounted(async () => {
  await store.loadBaseData();
  if (!store.ships.find((ship) => ship.id === voyageForm.shipId) && store.ships[0]?.id) {
    voyageForm.shipId = store.ships[0].id;
  }
});

async function saveVoyage() {
  try {
    await store.saveVoyage(voyageForm);
    ElMessage.success('航次已保存');
    Object.assign(voyageForm, createVoyageForm());
    if (!store.ships.find((ship) => ship.id === voyageForm.shipId) && store.ships[0]?.id) {
      voyageForm.shipId = store.ships[0].id;
    }
  } catch (error) {
    ElMessage.error((error as Error).message);
  }
}

function formatStatus(status: string) {
  const statusMap: Record<string, string> = {
    PLANNING: '规划中',
    DRAFT: '草稿',
    GENERATED: '已生成',
    PENDING: '待处理',
  };
  return statusMap[status] ?? status;
}
</script>
