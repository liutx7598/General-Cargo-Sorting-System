<template>
  <div v-if="detail" class="page-grid visualization-page">
    <div class="page-card hero-card">
      <div>
        <div class="section-title">配载图</div>
        <div class="hero-subtitle">主视图为二维总配载图，风格接近人工配载图纸；三维视图作为辅助检查工具保留。</div>
      </div>
      <div class="hero-meta">
        <span class="hero-chip">方案 {{ detail.plan.planNo }}</span>
        <span class="hero-chip">状态 {{ formatStatus(detail.plan.status) }}</span>
        <span class="hero-chip" :class="{ pass: detail.plan.complianceStatus === 'PASS', fail: detail.plan.complianceStatus !== 'PASS' }">
          {{ formatCompliance(detail.plan.complianceStatus) }}
        </span>
        <span class="hero-chip warning">告警 {{ detail.warnings.length }}</span>
      </div>
    </div>

    <div class="page-card control-card">
      <div class="control-group">
        <span class="control-label">聚焦货舱</span>
        <el-select v-model="selectedHoldId" clearable placeholder="高亮一个货舱" style="width: 220px;">
          <el-option v-for="hold in holds" :key="hold.id" :label="hold.holdNo" :value="hold.id" />
        </el-select>
      </div>
      <div class="control-group">
        <span class="control-label">层号</span>
        <el-select v-model="selectedLayer" style="width: 180px;">
          <el-option label="全部层" value="ALL" />
          <el-option v-for="layer in layerOptions" :key="layer" :label="`第 ${layer} 层`" :value="layer" />
        </el-select>
      </div>
      <div class="control-group">
        <span class="control-label">当前货物</span>
        <span class="control-value">{{ selectedCargoLabel }}</span>
      </div>
    </div>

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
      <div class="page-grid">
        <div class="page-card">
          <div class="section-title">当前货舱摘要</div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="货舱">{{ focusedHold?.holdNo ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="货物数量">{{ focusedHoldItems.length }}</el-descriptions-item>
            <el-descriptions-item label="重量">{{ formatNumber(focusedSummary?.totalWeight) }} 吨</el-descriptions-item>
            <el-descriptions-item label="利用率">{{ formatPercent(focusedSummary?.utilization) }}</el-descriptions-item>
            <el-descriptions-item label="重心">
              ({{ formatNumber(focusedSummary?.centroidX) }}, {{ formatNumber(focusedSummary?.centroidY) }}, {{ formatNumber(focusedSummary?.centroidZ) }})
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="page-card">
          <div class="section-title">当前货物详情</div>
          <el-empty v-if="!selectedCargo" description="点击二维配载图中的货物块查看详情。" />
          <el-descriptions v-else :column="1" border>
            <el-descriptions-item label="编码">{{ selectedCargo.cargoCode }}</el-descriptions-item>
            <el-descriptions-item label="名称">{{ selectedCargo.cargoName }}</el-descriptions-item>
            <el-descriptions-item label="类别">{{ formatCategory(selectedCargo.cargoCategory) }}</el-descriptions-item>
            <el-descriptions-item label="重量">{{ formatNumber(selectedCargo.weight) }} 吨</el-descriptions-item>
            <el-descriptions-item label="危险等级">{{ selectedCargo.dangerousClass ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="摆放尺寸">
              {{ selectedItem?.placedLength }} x {{ selectedItem?.placedWidth }} x {{ selectedItem?.placedHeight }}
            </el-descriptions-item>
            <el-descriptions-item label="原点">
              ({{ selectedItem?.originX }}, {{ selectedItem?.originY }}, {{ selectedItem?.originZ }})
            </el-descriptions-item>
            <el-descriptions-item label="层号">{{ selectedItem?.layerNo }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="page-card">
          <div class="section-title">货舱货物表</div>
          <el-table :data="focusedHoldRows" stripe max-height="300">
            <el-table-column prop="cargoCode" label="编码" width="120" />
            <el-table-column prop="cargoName" label="名称" min-width="140" />
            <el-table-column prop="weight" label="重量" width="90" />
            <el-table-column prop="layerNo" label="层号" width="80" />
            <el-table-column label="原点" min-width="150">
              <template #default="{ row }">({{ row.originX }}, {{ row.originY }}, {{ row.originZ }})</template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <hold-viewer
        :hold="focusedHold"
        :items="focusedHoldItems"
        :cargos="store.cargos"
        :warnings="focusedWarnings"
      />
    </div>
  </div>

  <el-empty v-else description="正在加载配载可视化..." />
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import HoldViewer from '@/components/HoldViewer.vue';
import StowageDeckPlan from '@/components/StowageDeckPlan.vue';
import { usePlanStore } from '@/store/plan';

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
  if (selectedItem.value) {
    return;
  }
  selectedItemId.value = undefined;
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

function formatNumber(value?: number | null) {
  return value == null ? '-' : value.toFixed(2);
}

function formatPercent(value?: number | null) {
  return value == null ? '-' : `${(value * 100).toFixed(1)}%`;
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

function formatCategory(category?: string) {
  const categoryMap: Record<string, string> = {
    STEEL: '钢材',
    TIMBER: '木材',
    EQUIPMENT: '设备',
    PROJECT: '工程货',
    PIPE: '管材',
    DANGEROUS: '危险货',
  };
  return category ? (categoryMap[category] ?? category) : '-';
}
</script>

<style scoped>
.visualization-page {
  gap: 18px;
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.hero-subtitle {
  color: #5f7383;
  font-size: 14px;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-chip {
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(18, 78, 102, 0.12);
  font-size: 13px;
  font-weight: 600;
}

.hero-chip.pass {
  color: #166534;
  border-color: rgba(22, 101, 52, 0.18);
}

.hero-chip.fail,
.hero-chip.warning {
  color: #c2410c;
  border-color: rgba(194, 65, 12, 0.18);
}

.control-card {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  align-items: center;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.control-label {
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
}

.control-value {
  color: #124e66;
  font-weight: 600;
}

.detail-grid {
  display: grid;
  grid-template-columns: minmax(360px, 0.9fr) minmax(0, 1.35fr);
  gap: 16px;
  align-items: start;
}

@media (max-width: 1180px) {
  .hero-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
