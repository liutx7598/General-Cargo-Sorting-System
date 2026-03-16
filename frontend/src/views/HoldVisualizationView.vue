<template>
  <div v-if="detail" class="page-shell visualization-page">
    <v-card class="page-card hero-card">
      <v-card-text class="hero-content">
        <div>
          <div class="section-title">配载可视化</div>
          <div class="muted-text">主视图为二维总配载图，三维视图用于检查单舱摆位细节。</div>
        </div>
        <div class="hero-meta">
          <v-chip color="primary" variant="tonal">方案 {{ detail.plan.planNo }}</v-chip>
          <v-chip color="info" variant="tonal">状态 {{ formatStatus(detail.plan.status) }}</v-chip>
          <v-chip
            :color="detail.plan.complianceStatus === 'PASS' ? 'success' : 'error'"
            variant="tonal"
          >
            {{ formatCompliance(detail.plan.complianceStatus) }}
          </v-chip>
          <v-chip color="warning" variant="tonal">告警 {{ detail.warnings.length }}</v-chip>
        </div>
      </v-card-text>
    </v-card>

    <v-card class="page-card">
      <v-card-text>
        <div class="control-grid">
          <v-select
            v-model="selectedHoldId"
            :items="holdOptions"
            item-title="title"
            item-value="value"
            clearable
            label="聚焦货舱"
          />
          <v-select
            v-model="selectedLayer"
            :items="layerSelectOptions"
            item-title="title"
            item-value="value"
            label="层号"
          />
          <div class="selected-info">
            <span class="selected-label">当前货物</span>
            <span class="selected-value">{{ selectedCargoLabel }}</span>
          </div>
        </div>
      </v-card-text>
    </v-card>

    <stowage-deck-plan
      :holds="holds"
      :items="visibleItems"
      :cargos="store.cargos"
      :warnings="detail.warnings"
      :selected-hold-id="selectedHoldId"
      :selected-item-id="selectedItem?.id ?? null"
      @select-hold="selectedHoldId = $event"
      @select-item="handleSelectItem"
    />

    <div class="detail-grid">
      <div class="page-shell">
        <v-card class="page-card">
          <v-card-text>
            <div class="section-title">当前货舱摘要</div>
            <div class="summary-stack">
              <div class="summary-row"><span>货舱</span><strong>{{ focusedHold?.holdNo ?? '-' }}</strong></div>
              <div class="summary-row"><span>货物数量</span><strong>{{ focusedHoldItems.length }}</strong></div>
              <div class="summary-row"><span>重量</span><strong>{{ formatNumber(focusedSummary?.totalWeight) }} T</strong></div>
              <div class="summary-row"><span>利用率</span><strong>{{ formatPercent(focusedSummary?.utilization) }}</strong></div>
              <div class="summary-row">
                <span>重心</span>
                <strong>
                  ({{ formatNumber(focusedSummary?.centroidX) }}, {{ formatNumber(focusedSummary?.centroidY) }},
                  {{ formatNumber(focusedSummary?.centroidZ) }})
                </strong>
              </div>
            </div>
          </v-card-text>
        </v-card>

        <v-card class="page-card">
          <v-card-text>
            <div class="section-title">当前货物详情</div>
            <div v-if="selectedCargo" class="summary-stack">
              <div class="summary-row"><span>编码</span><strong>{{ selectedCargo.cargoCode }}</strong></div>
              <div class="summary-row"><span>名称</span><strong>{{ selectedCargo.cargoName }}</strong></div>
              <div class="summary-row"><span>类别</span><strong>{{ formatCargoCategory(selectedCargo.cargoCategory) }}</strong></div>
              <div class="summary-row"><span>重量</span><strong>{{ formatNumber(selectedCargo.weight) }} T</strong></div>
              <div class="summary-row"><span>危险等级</span><strong>{{ selectedCargo.dangerousClass ?? '-' }}</strong></div>
              <div class="summary-row">
                <span>摆放尺寸</span>
                <strong>{{ selectedItem?.placedLength }} × {{ selectedItem?.placedWidth }} × {{ selectedItem?.placedHeight }}</strong>
              </div>
              <div class="summary-row">
                <span>原点</span>
                <strong>({{ selectedItem?.originX }}, {{ selectedItem?.originY }}, {{ selectedItem?.originZ }})</strong>
              </div>
              <div class="summary-row"><span>层号</span><strong>{{ selectedItem?.layerNo }}</strong></div>
            </div>
            <v-alert v-else type="info" variant="tonal" text="点击二维配载图中的货物块查看详情。" />
          </v-card-text>
        </v-card>

        <v-card class="page-card">
          <v-card-text>
            <div class="section-title">货舱货物表</div>
            <div class="table-shell">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>编码</th>
                    <th>名称</th>
                    <th>重量</th>
                    <th>层号</th>
                    <th>原点</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in focusedHoldRows" :key="`${row.cargoCode}-${row.layerNo}-${row.originX}`">
                    <td>{{ row.cargoCode }}</td>
                    <td>{{ row.cargoName }}</td>
                    <td>{{ row.weight }}</td>
                    <td>{{ row.layerNo }}</td>
                    <td>({{ row.originX }}, {{ row.originY }}, {{ row.originZ }})</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </v-card-text>
        </v-card>
      </div>

      <hold-viewer
        :hold="focusedHold"
        :items="focusedHoldItems"
        :cargos="store.cargos"
        :warnings="focusedWarnings"
      />
    </div>
  </div>

  <v-alert v-else type="info" variant="tonal" text="正在加载配载可视化..." />
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import HoldViewer from '@/components/HoldViewer.vue';
import StowageDeckPlan from '@/components/StowageDeckPlan.vue';
import { usePlanStore } from '@/store/plan';
import { formatCargoCategory, formatCompliance, formatNumber, formatPercent, formatStatus } from '@/utils/formatters';

const route = useRoute();
const store = usePlanStore();
const selectedHoldId = ref<number>();
const selectedLayer = ref<number | 'ALL'>('ALL');
const selectedItemId = ref<number>();

const detail = computed(() => store.selectedPlanDetail);
const shipId = computed(() => store.voyages.find((voyage) => voyage.id === detail.value?.plan.voyageId)?.shipId);
const holds = computed(() => (shipId.value ? store.holdsByShip[shipId.value] ?? [] : []));
const layerOptions = computed(() =>
  [...new Set((detail.value?.items ?? []).map((item) => item.layerNo))].sort((left, right) => left - right),
);

const holdOptions = computed(() =>
  holds.value.map((hold) => ({
    title: hold.holdNo,
    value: hold.id,
  })),
);

const layerSelectOptions = computed(() => [
  { title: '全部层', value: 'ALL' as const },
  ...layerOptions.value.map((layer) => ({ title: `第 ${layer} 层`, value: layer })),
]);

const visibleItems = computed(() =>
  (detail.value?.items ?? []).filter((item) => selectedLayer.value === 'ALL' || item.layerNo === selectedLayer.value),
);

const focusedHold = computed(() => {
  if (selectedHoldId.value) {
    return holds.value.find((hold) => hold.id === selectedHoldId.value) ?? holds.value[0] ?? null;
  }
  return holds.value[0] ?? null;
});

const focusedHoldItems = computed(() => visibleItems.value.filter((item) => item.holdId === focusedHold.value?.id));
const focusedSummary = computed(() =>
  detail.value?.plan.holdSummaries?.find((summary) => summary.holdId === focusedHold.value?.id),
);
const focusedWarnings = computed(() => {
  const cargoIds = new Set(focusedHoldItems.value.map((item) => item.cargoId));
  return detail.value?.warnings.filter(
    (warning) => warning.holdId === focusedHold.value?.id || (warning.cargoId != null && cargoIds.has(warning.cargoId)),
  ) ?? [];
});

const selectedItem = computed(() => visibleItems.value.find((item) => item.id === selectedItemId.value) ?? null);
const selectedCargo = computed(() => store.cargos.find((cargo) => cargo.id === selectedItem.value?.cargoId) ?? null);
const selectedCargoLabel = computed(() =>
  selectedCargo.value ? `${selectedCargo.value.cargoCode} - ${selectedCargo.value.cargoName}` : '未选择',
);

const focusedHoldRows = computed(() =>
  focusedHoldItems.value.map((item) => {
    const cargo = store.cargos.find((entry) => entry.id === item.cargoId);
    return {
      cargoCode: cargo?.cargoCode ?? `货物 ${item.cargoId}`,
      cargoName: cargo?.cargoName ?? '-',
      weight: cargo?.weight?.toFixed(1) ?? '-',
      layerNo: item.layerNo,
      originX: item.originX,
      originY: item.originY,
      originZ: item.originZ,
    };
  }),
);

onMounted(async () => {
  await store.loadBaseData();
  await store.fetchPlan(Number(route.params.id));
  if (shipId.value) {
    await store.loadHolds(shipId.value);
  }
  const holdIdFromQuery = Number(route.query.holdId);
  if (Number.isFinite(holdIdFromQuery) && holdIdFromQuery > 0) {
    selectedHoldId.value = holdIdFromQuery;
  }
});

watch(
  holds,
  (options) => {
    if (!options.length) {
      selectedHoldId.value = undefined;
      return;
    }
    if (selectedHoldId.value && options.some((hold) => hold.id === selectedHoldId.value)) {
      return;
    }
    selectedHoldId.value = options[0].id;
  },
  { immediate: true },
);

watch(selectedLayer, () => {
  if (!selectedItem.value) {
    selectedItemId.value = undefined;
  }
});

watch(
  visibleItems,
  (items) => {
    if (selectedItemId.value && items.some((item) => item.id === selectedItemId.value)) {
      return;
    }
    selectedItemId.value = items[0]?.id;
  },
  { immediate: true },
);

function handleSelectItem(itemId: number) {
  selectedItemId.value = itemId;
  const item = visibleItems.value.find((entry) => entry.id === itemId);
  if (item) {
    selectedHoldId.value = item.holdId;
  }
}
</script>

<style scoped>
.visualization-page {
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

.hero-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.control-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  align-items: start;
}

.selected-info {
  padding: 16px;
  border-radius: 18px;
  background: rgba(15, 92, 115, 0.05);
  border: 1px solid rgba(15, 92, 115, 0.08);
}

.selected-label {
  display: block;
  color: #6b7b8c;
  font-size: 13px;
  margin-bottom: 8px;
}

.selected-value {
  color: #17324d;
  font-weight: 700;
}

.detail-grid {
  display: grid;
  grid-template-columns: minmax(360px, 0.9fr) minmax(0, 1.35fr);
  gap: 16px;
  align-items: start;
}

.summary-stack {
  display: grid;
  gap: 12px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(15, 92, 115, 0.08);
}

.summary-row span {
  color: #6b7b8c;
}

.summary-row strong {
  text-align: right;
  color: #17324d;
}

.table-shell {
  overflow-x: auto;
}

@media (max-width: 1180px) {
  .hero-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
