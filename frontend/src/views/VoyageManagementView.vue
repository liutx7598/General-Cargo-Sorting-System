<template>
  <div class="page-shell">
    <v-card class="page-card">
      <v-card-text>
        <div class="toolbar-row">
          <div>
            <div class="section-title">航次管理</div>
            <div class="muted-text">维护航次编号、航线、港口和状态，为后续配载任务绑定船舶。</div>
          </div>
        </div>

        <div class="form-grid mt-4">
          <v-text-field v-model="voyageForm.voyageNo" label="航次号" />
          <v-select
            v-model="voyageForm.shipId"
            :items="shipOptions"
            item-title="title"
            item-value="value"
            label="船舶"
          />
          <v-text-field v-model="voyageForm.routeInfo" label="航线" />
          <v-text-field v-model="voyageForm.departurePort" label="起运港" />
          <v-text-field v-model="voyageForm.arrivalPort" label="到达港" />
          <v-select
            v-model="voyageForm.status"
            :items="statusOptions"
            item-title="title"
            item-value="value"
            label="状态"
          />
        </div>

        <div class="mt-4">
          <v-btn color="primary" @click="saveVoyage">保存航次</v-btn>
        </div>
      </v-card-text>
    </v-card>

    <v-card class="page-card">
      <v-card-text>
        <div class="section-title">航次列表</div>
        <div class="table-shell">
          <table class="data-table">
            <thead>
              <tr>
                <th>航次号</th>
                <th>船舶</th>
                <th>航线</th>
                <th>起运港</th>
                <th>到达港</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="voyage in store.voyages" :key="voyage.id">
                <td>{{ voyage.voyageNo }}</td>
                <td>{{ shipName(voyage.shipId) }}</td>
                <td>{{ voyage.routeInfo || '-' }}</td>
                <td>{{ voyage.departurePort || '-' }}</td>
                <td>{{ voyage.arrivalPort || '-' }}</td>
                <td>
                  <v-chip size="small" color="info" variant="tonal">{{ formatStatus(voyage.status) }}</v-chip>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue';

import { usePlanStore } from '@/store/plan';
import { useUiStore } from '@/store/ui';
import type { Voyage } from '@/types';
import { formatStatus } from '@/utils/formatters';

const store = usePlanStore();
const ui = useUiStore();

const statusOptions = [
  { title: '规划中', value: 'PLANNING' },
  { title: '草稿', value: 'DRAFT' },
  { title: '已生成', value: 'GENERATED' },
];

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

const shipOptions = computed(() =>
  store.ships.map((ship) => ({
    title: `${ship.shipCode} - ${ship.shipName}`,
    value: ship.id,
  })),
);

onMounted(async () => {
  await store.loadBaseData();
  if (!store.ships.find((ship) => ship.id === voyageForm.shipId) && store.ships[0]?.id) {
    voyageForm.shipId = store.ships[0].id;
  }
});

async function saveVoyage() {
  try {
    await store.saveVoyage(voyageForm);
    ui.success('航次已保存');
    Object.assign(voyageForm, createVoyageForm());
    if (!store.ships.find((ship) => ship.id === voyageForm.shipId) && store.ships[0]?.id) {
      voyageForm.shipId = store.ships[0].id;
    }
  } catch (error) {
    ui.error((error as Error).message);
  }
}

function shipName(shipId: number) {
  return store.ships.find((ship) => ship.id === shipId)?.shipName ?? '-';
}
</script>

<style scoped>
.table-shell {
  overflow-x: auto;
}
</style>
