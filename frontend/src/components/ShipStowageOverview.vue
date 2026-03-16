<template>
  <div class="page-card ship-overview">
    <div class="overview-header">
      <div>
        <div class="section-title">整船货舱概览</div>
        <div class="overview-subtitle">点击下方货舱查看详细配载。</div>
      </div>
      <div class="legend">
        <span class="legend-pill"><i class="legend-dot normal"></i>正常</span>
        <span class="legend-pill"><i class="legend-dot dangerous"></i>危险货</span>
        <span class="legend-pill"><i class="legend-dot warning"></i>告警</span>
      </div>
    </div>

    <div class="ship-stage">
      <div class="ship-shell">
        <div class="ship-end stern"></div>
        <button
          v-for="entry in holdEntries"
          :key="entry.hold.id"
          type="button"
          class="hold-segment"
          :class="{ active: selectedHoldId === entry.hold.id, alerted: entry.warningCount > 0 }"
          :style="{ flex: `${Math.max(entry.hold.length, 1)} 1 0` }"
          @click="$emit('selectHold', entry.hold.id!)"
        >
          <div class="hold-frame">
            <div class="utilization-fill" :style="{ height: `${entry.fillHeight}%` }">
              <div class="cargo-chips">
                <span
                  v-for="chip in entry.cargoChips"
                  :key="chip.key"
                  class="cargo-chip"
                  :style="{ background: chip.color }"
                  :title="chip.label"
                ></span>
              </div>
            </div>
            <div class="hold-caption">
              <strong>{{ entry.hold.holdNo }}</strong>
              <span>{{ entry.cargoCount }} 件货物</span>
              <span>{{ formatPercent(entry.utilization) }}</span>
            </div>
          </div>
        </button>
        <div class="ship-end bow"></div>
      </div>
    </div>

    <div class="hold-summary-grid">
      <button
        v-for="entry in holdEntries"
        :key="`${entry.hold.id}-summary`"
        type="button"
        class="hold-summary-card"
        :class="{ active: selectedHoldId === entry.hold.id }"
        @click="$emit('selectHold', entry.hold.id!)"
      >
        <div class="summary-top">
          <span class="summary-hold">{{ entry.hold.holdNo }}</span>
          <span class="summary-warnings" :class="{ raised: entry.warningCount > 0 }">
            {{ entry.warningCount }} 条告警
          </span>
        </div>
        <div class="summary-metrics">
          <span>{{ formatNumber(entry.totalWeight) }} 吨</span>
          <span>{{ entry.cargoCount }} 件</span>
          <span>LCG {{ formatNumber(entry.centroidX) }}</span>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import type { Cargo, Hold, HoldMetric, StowageItem, WarningRecord } from '@/types';

const props = defineProps<{
  holds: Hold[];
  items: StowageItem[];
  holdSummaries: HoldMetric[];
  cargos: Cargo[];
  warnings: WarningRecord[];
  selectedHoldId?: number;
}>();

defineEmits<{
  selectHold: [holdId: number];
}>();

function colorForCargo(cargo: Cargo | undefined, hasWarning: boolean) {
  if (hasWarning) {
    return '#c2410c';
  }
  if (cargo?.dangerousClass) {
    return '#d17b0f';
  }
  return '#124e66';
}

const holdEntries = computed(() => {
  const summaryMap = new Map(props.holdSummaries.map((summary) => [summary.holdId, summary]));
  return [...props.holds]
    .sort((left, right) => left.sequenceNo - right.sequenceNo)
    .map((hold) => {
      const holdItems = props.items.filter((item) => item.holdId === hold.id);
      const summary = summaryMap.get(hold.id ?? -1);
      const warningCount = props.warnings.filter((warning) => warning.holdId === hold.id).length;
      const cargoChips = holdItems.slice(0, 10).map((item, index) => {
        const cargo = props.cargos.find((entry) => entry.id === item.cargoId);
        const hasWarning = props.warnings.some((warning) => warning.cargoId === item.cargoId);
        return {
          key: `${item.cargoId}-${index}`,
          label: cargo ? `${cargo.cargoCode} - ${cargo.cargoName}` : `货物 ${item.cargoId}`,
          color: colorForCargo(cargo, hasWarning),
        };
      });

      return {
        hold,
        utilization: summary?.utilization ?? 0,
        fillHeight: Math.max(10, Math.min(94, (summary?.utilization ?? 0) * 100)),
        cargoCount: holdItems.length,
        totalWeight: summary?.totalWeight ?? 0,
        centroidX: summary?.centroidX ?? 0,
        warningCount,
        cargoChips,
      };
    });
});

function formatPercent(value: number) {
  return `${(value * 100).toFixed(1)}%`;
}

function formatNumber(value: number) {
  return value.toFixed(1);
}
</script>

<style scoped>
.ship-overview {
  overflow: hidden;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.overview-subtitle {
  color: #5f7383;
  font-size: 14px;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.legend-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(18, 78, 102, 0.12);
  font-size: 13px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.legend-dot.normal {
  background: #124e66;
}

.legend-dot.dangerous {
  background: #d17b0f;
}

.legend-dot.warning {
  background: #c2410c;
}

.ship-stage {
  padding: 24px 8px 12px;
  overflow-x: auto;
}

.ship-shell {
  min-width: 760px;
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 28px 0 6px;
  position: relative;
}

.ship-shell::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(18, 78, 102, 0.35), rgba(17, 94, 89, 0.18));
}

.ship-end {
  width: 54px;
  height: 168px;
  position: relative;
  flex: 0 0 54px;
}

.ship-end::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.7), rgba(18, 78, 102, 0.12));
  border: 2px solid rgba(18, 78, 102, 0.16);
}

.ship-end.stern::before {
  clip-path: polygon(100% 0, 26% 18%, 0 100%, 100% 100%);
  border-radius: 22px 0 12px 22px;
}

.ship-end.bow::before {
  clip-path: polygon(0 0, 100% 22%, 100% 100%, 0 100%);
  border-radius: 0 22px 22px 12px;
}

.hold-segment {
  appearance: none;
  background: transparent;
  border: none;
  padding: 0;
  cursor: pointer;
  min-width: 120px;
}

.hold-frame {
  height: 184px;
  border-radius: 18px 18px 14px 14px;
  border: 2px solid rgba(18, 78, 102, 0.16);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(18, 78, 102, 0.06));
  position: relative;
  overflow: hidden;
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.hold-segment:hover .hold-frame,
.hold-segment.active .hold-frame {
  transform: translateY(-4px);
  border-color: rgba(18, 78, 102, 0.38);
  box-shadow: 0 12px 26px rgba(18, 78, 102, 0.16);
}

.hold-segment.alerted .hold-frame {
  border-color: rgba(194, 65, 12, 0.3);
}

.utilization-fill {
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: 10px;
  border-radius: 12px 12px 10px 10px;
  background: linear-gradient(180deg, rgba(17, 94, 89, 0.16), rgba(18, 78, 102, 0.42));
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 10px;
}

.hold-segment.alerted .utilization-fill {
  background: linear-gradient(180deg, rgba(217, 119, 6, 0.28), rgba(194, 65, 12, 0.5));
}

.cargo-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  max-width: 100%;
}

.cargo-chip {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.45);
}

.hold-caption {
  position: absolute;
  left: 12px;
  right: 12px;
  top: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: left;
  color: #1f2a36;
  font-size: 12px;
}

.hold-caption strong {
  font-size: 15px;
}

.hold-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.hold-summary-card {
  appearance: none;
  border: 1px solid rgba(18, 78, 102, 0.12);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.62);
  padding: 14px 16px;
  text-align: left;
  cursor: pointer;
  transition: border-color 180ms ease, transform 180ms ease, box-shadow 180ms ease;
}

.hold-summary-card:hover,
.hold-summary-card.active {
  transform: translateY(-2px);
  border-color: rgba(18, 78, 102, 0.32);
  box-shadow: 0 12px 20px rgba(18, 78, 102, 0.12);
}

.summary-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.summary-hold {
  font-weight: 700;
}

.summary-warnings {
  font-size: 12px;
  color: #617182;
}

.summary-warnings.raised {
  color: #c2410c;
}

.summary-metrics {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #334155;
  font-size: 13px;
}

@media (max-width: 900px) {
  .overview-header {
    flex-direction: column;
  }
}
</style>
