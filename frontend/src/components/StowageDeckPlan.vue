<template>
  <div class="page-card deck-plan-card">
    <div class="deck-plan-header">
      <div>
        <div class="section-title">二维配载总图</div>
        <div class="deck-plan-subtitle">
          根据货舱边界、货物原点坐标和摆放尺寸绘制的顶视配载图。
        </div>
      </div>
      <div class="deck-plan-legend">
        <span class="legend-pill"><i class="legend-dot steel"></i>钢材 / 设备</span>
        <span class="legend-pill"><i class="legend-dot timber"></i>木材 / 工程货</span>
        <span class="legend-pill"><i class="legend-dot dangerous"></i>危险货</span>
        <span class="legend-pill"><i class="legend-dot warning"></i>告警货</span>
      </div>
    </div>

    <div v-if="cargoRects.length" class="deck-plan-scroll">
      <svg
        :viewBox="`0 0 ${layout.width} ${layout.height}`"
        :style="{ width: `${layout.width}px`, height: `${layout.height}px` }"
        class="deck-plan-svg"
      >
        <defs>
          <pattern id="deck-grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#d8dde3" stroke-width="1" />
          </pattern>
          <filter id="cargo-shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="rgba(15, 23, 42, 0.18)" />
          </filter>
        </defs>

        <rect x="0" y="0" :width="layout.width" :height="layout.height" fill="url(#deck-grid)" />

        <g v-for="holdRect in holdRects" :key="holdRect.hold.id">
          <rect
            :x="holdRect.x"
            :y="holdRect.y"
            :width="holdRect.width"
            :height="holdRect.height"
            rx="4"
            fill="rgba(255,255,255,0.72)"
            stroke="#202020"
            stroke-width="2"
            @click="$emit('selectHold', holdRect.hold.id!)"
          />
          <text :x="holdRect.x + 6" :y="holdRect.y - 10" class="hold-label">
            {{ holdRect.hold.holdNo }} | {{ holdRect.hold.length }} x {{ holdRect.hold.width }} 米
          </text>
        </g>

        <g
          v-for="cargoRect in cargoRects"
          :key="cargoRect.itemId"
          class="cargo-group"
          :class="{ selected: cargoRect.isSelected }"
          @click.stop="selectItem(cargoRect.itemId, cargoRect.holdId)"
        >
          <rect
            :x="cargoRect.x"
            :y="cargoRect.y"
            :width="cargoRect.width"
            :height="cargoRect.height"
            rx="2"
            :fill="cargoRect.fill"
            :stroke="cargoRect.stroke"
            :stroke-width="cargoRect.strokeWidth"
            filter="url(#cargo-shadow)"
          />

          <rect
            :x="cargoRect.x + 4"
            :y="cargoRect.y + 4"
            width="34"
            height="18"
            rx="2"
            fill="rgba(255,255,255,0.78)"
            stroke="rgba(15, 23, 42, 0.18)"
            stroke-width="1"
          />
          <text :x="cargoRect.x + 10" :y="cargoRect.y + 17" class="layer-badge">{{ cargoRect.layerNo }}层</text>

          <g v-if="!cargoRect.verticalText">
            <text
              :x="cargoRect.x + 8"
              :y="cargoRect.y + 34"
              class="cargo-text"
              :style="{ fontSize: `${cargoRect.fontSize}px` }"
            >
              <tspan :x="cargoRect.x + 8" dy="0">{{ cargoRect.line1 }}</tspan>
              <tspan v-if="cargoRect.line2" :x="cargoRect.x + 8" dy="1.35em">{{ cargoRect.line2 }}</tspan>
              <tspan v-if="cargoRect.line3" :x="cargoRect.x + 8" dy="1.25em">{{ cargoRect.line3 }}</tspan>
            </text>
          </g>

          <g v-else :transform="`translate(${cargoRect.x + cargoRect.width - 10}, ${cargoRect.y + 12}) rotate(90)`">
            <text class="cargo-text" :style="{ fontSize: `${cargoRect.fontSize}px` }">
              <tspan x="0" dy="0">{{ cargoRect.line1 }}</tspan>
              <tspan v-if="cargoRect.line2" x="0" dy="1.35em">{{ cargoRect.line2 }}</tspan>
            </text>
          </g>

          <title>{{ cargoRect.tooltip }}</title>
        </g>
      </svg>
    </div>

    <el-empty v-else description="当前筛选条件下暂无配载数据。" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import type { Cargo, Hold, StowageItem, WarningRecord } from '@/types';

type HoldRect = {
  hold: Hold;
  x: number;
  y: number;
  width: number;
  height: number;
};

type CargoRect = {
  itemId: number;
  holdId: number;
  layerNo: number;
  x: number;
  y: number;
  width: number;
  height: number;
  fill: string;
  stroke: string;
  strokeWidth: number;
  line1: string;
  line2: string;
  line3?: string;
  fontSize: number;
  verticalText: boolean;
  tooltip: string;
  isSelected: boolean;
};

const props = defineProps<{
  holds: Hold[];
  items: StowageItem[];
  cargos: Cargo[];
  warnings: WarningRecord[];
  selectedHoldId?: number;
  selectedItemId?: number | null;
}>();

const emit = defineEmits<{
  selectHold: [holdId: number];
  selectItem: [itemId: number];
}>();

const SCALE = 26;
const HOLD_GAP = 40;
const HORIZONTAL_MARGIN = 34;
const TOP_MARGIN = 56;
const BOTTOM_MARGIN = 36;

const holdRects = computed<HoldRect[]>(() => {
  const sortedHolds = [...props.holds].sort((left, right) => left.sequenceNo - right.sequenceNo);
  const maxWidth = Math.max(...sortedHolds.map((hold) => hold.width), 0);
  let currentX = HORIZONTAL_MARGIN;

  return sortedHolds.map((hold) => {
    const width = hold.length * SCALE;
    const height = hold.width * SCALE;
    const y = TOP_MARGIN + (maxWidth * SCALE - height) / 2;
    const rect = { hold, x: currentX, y, width, height };
    currentX += width + HOLD_GAP;
    return rect;
  });
});

const layout = computed(() => {
  if (!holdRects.value.length) {
    return { width: 900, height: 360 };
  }
  const last = holdRects.value[holdRects.value.length - 1];
  const maxBottom = Math.max(...holdRects.value.map((holdRect) => holdRect.y + holdRect.height));
  return {
    width: last.x + last.width + HORIZONTAL_MARGIN,
    height: maxBottom + BOTTOM_MARGIN,
  };
});

function cargoLabelColor(cargo: Cargo | undefined, hasWarning: boolean) {
  if (hasWarning) {
    return { fill: '#ffd36f', stroke: '#b45309' };
  }
  if (cargo?.dangerousClass) {
    return { fill: '#facc15', stroke: '#a16207' };
  }
  switch (cargo?.cargoCategory) {
    case 'STEEL':
    case 'EQUIPMENT':
      return { fill: '#d8e3ef', stroke: '#8aa0b8' };
    case 'TIMBER':
    case 'PROJECT':
    case 'PIPE':
      return { fill: '#b7d59a', stroke: '#7ea061' };
    default:
      return { fill: '#c7ddae', stroke: '#84a768' };
  }
}

function shortenName(name: string | undefined, maxLength: number) {
  if (!name) {
    return '';
  }
  return name.length <= maxLength ? name : `${name.slice(0, Math.max(0, maxLength - 1))}…`;
}

function formatCargoCategory(category?: string) {
  const categoryMap: Record<string, string> = {
    STEEL: '钢材',
    TIMBER: '木材',
    EQUIPMENT: '设备',
    PROJECT: '工程货',
    PIPE: '管材',
    DANGEROUS: '危险货',
  };
  return category ? (categoryMap[category] ?? category) : '';
}

const cargoRects = computed<CargoRect[]>(() => {
  const holdRectMap = new Map(holdRects.value.map((entry) => [entry.hold.id, entry]));
  const rectangles: CargoRect[] = [];

  props.items.forEach((item, index) => {
    const holdRect = holdRectMap.get(item.holdId);
    if (!holdRect) {
      return;
    }

    const cargo = props.cargos.find((entry) => entry.id === item.cargoId);
    const hasWarning = props.warnings.some((warning) => warning.cargoId === item.cargoId || warning.holdId === item.holdId);
    const palette = cargoLabelColor(cargo, hasWarning);
    const width = Math.max(item.placedLength * SCALE, 14);
    const height = Math.max(item.placedWidth * SCALE, 14);
    const x = holdRect.x + item.originX * SCALE;
    const y = holdRect.y + item.originY * SCALE;
    const verticalText = width < 92 && height > 110;
    const fontSize = width < 110 || height < 58 ? 12 : 14;
    const itemId = item.id ?? index + 1;
    const weightText = cargo?.weight != null ? `${cargo.weight.toFixed(1)}吨` : '';
    const dimensionText = `${item.placedLength}*${item.placedWidth}*${item.placedHeight}`;
    const titleText = [cargo?.cargoCode ?? `C${item.cargoId}`, shortenName(cargo?.cargoName, verticalText ? 8 : 12), weightText]
      .filter(Boolean)
      .join(' ');
    const tooltip = [
      `货物：${cargo?.cargoCode ?? item.cargoId}`,
      cargo?.cargoName ? `名称：${cargo.cargoName}` : undefined,
      cargo?.cargoCategory ? `类别：${formatCargoCategory(cargo.cargoCategory)}` : undefined,
      cargo?.weight != null ? `重量：${cargo.weight.toFixed(1)}吨` : undefined,
      `尺寸：${dimensionText}`,
      `原点：(${item.originX}, ${item.originY}, ${item.originZ})`,
      `货舱：${holdRect.hold.holdNo}`,
      `层号：${item.layerNo}`,
    ]
      .filter(Boolean)
      .join('\n');

    rectangles.push({
      itemId,
      holdId: item.holdId,
      layerNo: item.layerNo,
      x,
      y,
      width,
      height,
      fill: palette.fill,
      stroke: palette.stroke,
      strokeWidth: props.selectedItemId === itemId ? 3 : props.selectedHoldId === item.holdId ? 2.4 : 1.6,
      line1: titleText,
      line2: dimensionText,
      line3: !verticalText && width > 140 && cargo?.cargoCategory ? formatCargoCategory(cargo.cargoCategory) : undefined,
      fontSize,
      verticalText,
      tooltip,
      isSelected: props.selectedItemId === itemId,
    });
  });

  return rectangles.sort((left, right) => left.layerNo - right.layerNo || left.y - right.y || left.x - right.x);
});

function selectItem(itemId: number, holdId: number) {
  emit('selectHold', holdId);
  emit('selectItem', itemId);
}
</script>

<style scoped>
.deck-plan-card {
  overflow: hidden;
}

.deck-plan-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.deck-plan-subtitle {
  color: #5f7383;
  font-size: 14px;
}

.deck-plan-legend {
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
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(18, 78, 102, 0.12);
  font-size: 13px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.legend-dot.steel {
  background: #8aa0b8;
}

.legend-dot.timber {
  background: #84a768;
}

.legend-dot.dangerous {
  background: #facc15;
}

.legend-dot.warning {
  background: #b45309;
}

.deck-plan-scroll {
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 8px;
}

.deck-plan-svg {
  display: block;
  border-radius: 14px;
  background: #f4f6f8;
}

.hold-label {
  fill: #1f2937;
  font-size: 14px;
  font-weight: 600;
}

.cargo-group {
  cursor: pointer;
}

.cargo-group.selected {
  filter: saturate(1.08);
}

.layer-badge {
  fill: #0f172a;
  font-size: 11px;
  font-weight: 700;
}

.cargo-text {
  fill: #17212b;
  font-weight: 600;
  letter-spacing: 0.1px;
}
</style>
