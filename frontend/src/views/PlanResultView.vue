<template>
  <div v-if="detail" class="page-grid result-page">
    <div class="page-card result-hero">
      <div>
        <div class="section-title">配载结果</div>
        <div class="result-subtitle">本页展示核算指标与配载明细，下方可查看总配载图，也可进入专门的 3D 检查页。</div>
      </div>
      <div class="result-actions">
        <el-button type="primary" @click="openVisualization()">打开 3D 可视化</el-button>
        <el-button @click="openWarnings()">查看告警</el-button>
      </div>
    </div>

    <metric-cards :cards="cards" />

    <metric-charts :holds="detail.plan.holdSummaries ?? []" :warning-count="detail.warnings.length" :gm="detail.plan.gm" />

    <stowage-deck-plan
      v-if="holds.length"
      :holds="holds"
      :items="detail.items"
      :cargos="store.cargos"
      :warnings="detail.warnings"
      :selected-hold-id="selectedHoldId"
      :selected-item-id="selectedItemId ?? null"
      @select-hold="handleSelectHold"
      @select-item="handleSelectItem"
    />

    <div class="page-card">
      <div class="summary-head">
        <div class="section-title">结果摘要</div>
        <div class="summary-actions">
          <span v-if="selectedHold" class="summary-selected">已选货舱 {{ selectedHold.holdNo }}</span>
          <span v-if="selectedCargoLabel" class="summary-selected">已选货物 {{ selectedCargoLabel }}</span>
          <el-button v-if="selectedHoldId" type="success" plain @click="openVisualization(selectedHoldId)">查看选中货舱</el-button>
        </div>
      </div>
      <el-descriptions :column="4" border>
        <el-descriptions-item label="方案号">{{ detail.plan.planNo }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ formatStatus(detail.plan.status) }}</el-descriptions-item>
        <el-descriptions-item label="结论">
          <el-tag :type="detail.plan.complianceStatus === 'PASS' ? 'success' : 'danger'">
            {{ formatCompliance(detail.plan.complianceStatus) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="告警数">{{ detail.plan.warningCount }}</el-descriptions-item>
      </el-descriptions>
    </div>

    <div class="page-card">
      <div class="section-title">货舱指标</div>
      <el-table :data="detail.plan.holdSummaries ?? []" stripe>
        <el-table-column prop="holdNo" label="货舱" width="90" />
        <el-table-column prop="totalWeight" label="总重 Wn" width="110" />
        <el-table-column prop="centroidX" label="重心 Xn" width="110" />
        <el-table-column prop="centroidY" label="重心 Yn" width="110" />
        <el-table-column prop="centroidZ" label="重心 Zn" width="110" />
        <el-table-column prop="utilization" label="利用率 eta_n" width="130">
          <template #default="{ row }">{{ (row.utilization * 100).toFixed(2) }}%</template>
        </el-table-column>
        <el-table-column prop="unitWeightPerVolume" label="单位载重 lambda_n" width="150" />
      </el-table>
    </div>

    <div class="page-card">
      <div class="section-title">配载项</div>
      <el-table :data="detail.items" stripe>
        <el-table-column prop="cargoId" label="货物ID" width="100" />
        <el-table-column prop="holdId" label="货舱ID" width="100" />
        <el-table-column prop="orientation" label="朝向" width="120" />
        <el-table-column prop="layerNo" label="层号" width="80" />
        <el-table-column label="原点" min-width="180">
          <template #default="{ row }">({{ row.originX }}, {{ row.originY }}, {{ row.originZ }})</template>
        </el-table-column>
        <el-table-column label="重心" min-width="180">
          <template #default="{ row }">({{ row.centroidX }}, {{ row.centroidY }}, {{ row.centroidZ }})</template>
        </el-table-column>
      </el-table>
    </div>

    <div class="page-card">
      <div class="section-title">告警列表</div>
      <warning-list :warnings="detail.warnings" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import MetricCards from '@/components/MetricCards.vue';
import MetricCharts from '@/components/MetricCharts.vue';
import StowageDeckPlan from '@/components/StowageDeckPlan.vue';
import WarningList from '@/components/WarningList.vue';
import { usePlanStore } from '@/store/plan';

const route = useRoute();
const router = useRouter();
const store = usePlanStore();
const selectedHoldId = ref<number>();
const selectedItemId = ref<number>();

const detail = computed(() => store.selectedPlanDetail);
const cards = computed(() => [
  { label: '总排水量', value: detail.value?.plan.displacement },
  { label: 'KG', value: detail.value?.plan.kg },
  { label: 'LCG', value: detail.value?.plan.lcg },
  { label: 'TCG', value: detail.value?.plan.tcg },
  { label: 'GM', value: detail.value?.plan.gm },
  { label: '总货重', value: detail.value?.plan.totalCargoWeight },
]);
const shipId = computed(() => store.voyages.find((voyage) => voyage.id === detail.value?.plan.voyageId)?.shipId);
const holds = computed(() => (shipId.value ? store.holdsByShip[shipId.value] ?? [] : []));
const selectedHold = computed(() => holds.value.find((hold) => hold.id === selectedHoldId.value) ?? null);
const selectedCargoLabel = computed(() => {
  const item = detail.value?.items.find((entry) => entry.id === selectedItemId.value);
  const cargo = store.cargos.find((entry) => entry.id === item?.cargoId);
  return cargo ? `${cargo.cargoCode} - ${cargo.cargoName}` : '';
});

onMounted(async () => {
  await store.loadBaseData();
  await store.fetchPlan(Number(route.params.id));
  if (shipId.value) {
    await store.loadHolds(shipId.value);
  }
});

watch(
  holds,
  (entries) => {
    if (!entries.length) {
      selectedHoldId.value = undefined;
      return;
    }
    if (!entries.some((hold) => hold.id === selectedHoldId.value)) {
      selectedHoldId.value = entries[0].id;
    }
  },
  { immediate: true },
);

function handleSelectHold(holdId: number) {
  selectedHoldId.value = holdId;
}

function handleSelectItem(itemId: number) {
  selectedItemId.value = itemId;
  const item = detail.value?.items.find((entry) => entry.id === itemId);
  if (item) {
    selectedHoldId.value = item.holdId;
  }
}

function openVisualization(holdId?: number) {
  router.push({
    path: `/plans/${route.params.id}/visualization`,
    query: holdId ? { holdId: String(holdId) } : undefined,
  });
}

function openWarnings() {
  router.push(`/plans/${route.params.id}/warnings`);
}

function formatStatus(status?: string) {
  const statusMap: Record<string, string> = {
    DRAFT: '草稿',
    GENERATED: '已生成',
    PENDING: '待处理',
    PLANNING: '规划中',
  };
  return status ? (statusMap[status] ?? status) : '-';
}

function formatCompliance(status?: string) {
  const complianceMap: Record<string, string> = {
    PASS: '通过',
    FAIL: '不通过',
    PENDING: '待判定',
  };
  return status ? (complianceMap[status] ?? status) : '-';
}
</script>

<style scoped>
.result-page {
  gap: 18px;
}

.result-hero {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.result-subtitle {
  color: #5f7383;
  font-size: 14px;
}

.result-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.summary-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.summary-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.summary-selected {
  color: #124e66;
  font-size: 14px;
  font-weight: 600;
}

@media (max-width: 980px) {
  .result-hero,
  .summary-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
