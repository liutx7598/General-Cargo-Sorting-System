<template>
  <div v-if="detail" class="page-shell result-page">
    <v-card class="page-card hero-card">
      <v-card-text class="hero-content">
        <div>
          <div class="section-title">配载结果</div>
          <div class="muted-text">本页展示整船指标、货舱指标、配载明细和二维总配载图。</div>
        </div>
        <div class="hero-actions">
          <v-btn color="primary" @click="openVisualization()">打开 3D 可视化</v-btn>
          <v-btn color="secondary" variant="tonal" @click="openWarnings()">查看告警</v-btn>
        </div>
      </v-card-text>
    </v-card>

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

    <v-card class="page-card">
      <v-card-text>
        <div class="toolbar-row">
          <div class="section-title">结果摘要</div>
          <div class="summary-actions">
            <span v-if="selectedHold" class="chip-inline">已选货舱 {{ selectedHold.holdNo }}</span>
            <span v-if="selectedCargoLabel" class="chip-inline">已选货物 {{ selectedCargoLabel }}</span>
            <v-btn v-if="selectedHoldId" color="success" variant="tonal" @click="openVisualization(selectedHoldId)">
              查看选中货舱
            </v-btn>
          </div>
        </div>

        <div class="summary-grid">
          <div class="summary-item">
            <span class="summary-label">方案号</span>
            <span class="summary-value">{{ detail.plan.planNo }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">状态</span>
            <span class="summary-value">{{ formatStatus(detail.plan.status) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">结论</span>
            <v-chip
              size="small"
              :color="detail.plan.complianceStatus === 'PASS' ? 'success' : 'error'"
              variant="tonal"
            >
              {{ formatCompliance(detail.plan.complianceStatus) }}
            </v-chip>
          </div>
          <div class="summary-item">
            <span class="summary-label">告警数</span>
            <span class="summary-value">{{ detail.plan.warningCount }}</span>
          </div>
        </div>
      </v-card-text>
    </v-card>

    <v-card class="page-card">
      <v-card-text>
        <div class="section-title">货舱指标</div>
        <div class="table-shell">
          <table class="data-table">
            <thead>
              <tr>
                <th>货舱</th>
                <th>总重 Wn</th>
                <th>重心 Xn</th>
                <th>重心 Yn</th>
                <th>重心 Zn</th>
                <th>利用率 eta_n</th>
                <th>单位载重 lambda_n</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="summary in detail.plan.holdSummaries ?? []" :key="summary.holdId">
                <td>{{ summary.holdNo }}</td>
                <td>{{ formatNumber(summary.totalWeight) }}</td>
                <td>{{ formatNumber(summary.centroidX) }}</td>
                <td>{{ formatNumber(summary.centroidY) }}</td>
                <td>{{ formatNumber(summary.centroidZ) }}</td>
                <td>{{ formatPercent(summary.utilization, 2) }}</td>
                <td>{{ formatNumber(summary.unitWeightPerVolume, 4) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </v-card-text>
    </v-card>

    <v-card class="page-card">
      <v-card-text>
        <div class="section-title">配载项</div>
        <div class="table-shell">
          <table class="data-table">
            <thead>
              <tr>
                <th>货物 ID</th>
                <th>货舱 ID</th>
                <th>朝向</th>
                <th>层号</th>
                <th>原点</th>
                <th>重心</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in detail.items" :key="item.id ?? `${item.cargoId}-${item.holdId}-${item.layerNo}`">
                <td>{{ item.cargoId }}</td>
                <td>{{ item.holdId }}</td>
                <td>{{ item.orientation }}</td>
                <td>{{ item.layerNo }}</td>
                <td>({{ item.originX }}, {{ item.originY }}, {{ item.originZ }})</td>
                <td>({{ item.centroidX }}, {{ item.centroidY }}, {{ item.centroidZ }})</td>
              </tr>
            </tbody>
          </table>
        </div>
      </v-card-text>
    </v-card>

    <v-card class="page-card">
      <v-card-text>
        <div class="section-title">告警列表</div>
        <warning-list :warnings="detail.warnings" />
      </v-card-text>
    </v-card>
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
import { formatCompliance, formatNumber, formatPercent, formatStatus } from '@/utils/formatters';

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
</script>

<style scoped>
.result-page {
  gap: 18px;
}

.hero-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(235, 244, 248, 0.96));
}

.hero-content {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.hero-actions,
.summary-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.summary-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.summary-item {
  display: grid;
  gap: 8px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(15, 92, 115, 0.08);
}

.summary-label {
  color: #6b7b8c;
  font-size: 13px;
  font-weight: 600;
}

.summary-value {
  color: #17324d;
  font-size: 16px;
  font-weight: 700;
}

.table-shell {
  overflow-x: auto;
}

@media (max-width: 980px) {
  .hero-content {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
