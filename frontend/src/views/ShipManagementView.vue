<template>
  <div class="page-shell">
    <v-card class="page-card">
      <v-card-text>
        <div class="toolbar-row">
          <div>
            <div class="section-title">船舶管理</div>
            <div class="muted-text">维护船舶基础参数，并为后续货舱管理提供主船上下文。</div>
          </div>
          <v-chip color="primary" variant="tonal">当前船型：{{ formatShipType(shipForm.shipType) }}</v-chip>
        </div>

        <div class="form-grid mt-4">
          <v-text-field v-model="shipForm.shipCode" label="船舶代码" />
          <v-text-field v-model="shipForm.shipName" label="船名" />
          <v-select v-model="shipForm.shipType" :items="shipTypes" item-title="title" item-value="value" label="船型" />
          <app-number-field v-model="shipForm.lengthOverall" label="总长" :min="1" />
          <app-number-field v-model="shipForm.lengthBetweenPerpendiculars" label="垂线间长" :min="1" />
          <app-number-field v-model="shipForm.beam" label="型宽" :min="1" />
          <app-number-field v-model="shipForm.depth" label="型深" :min="1" />
          <app-number-field v-model="shipForm.lightshipWeight" label="空船重" :min="1" />
          <app-number-field v-model="shipForm.lightshipKG" label="KG" :min="0" />
          <app-number-field v-model="shipForm.lightshipLCG" label="LCG" :min="0" />
          <app-number-field v-model="shipForm.designDisplacement" label="设计排水量" :min="1" />
          <app-number-field v-model="shipForm.designGM" label="设计 GM" :min="0" />
        </div>

        <v-textarea v-model="shipForm.remark" label="备注" rows="2" class="mt-4" />

        <div class="mt-4">
          <v-btn color="primary" @click="saveShip">保存船舶</v-btn>
        </div>
      </v-card-text>
    </v-card>

    <v-card class="page-card">
      <v-card-text>
        <div class="toolbar-row">
          <div class="section-title">船舶列表</div>
          <div class="muted-text">点击某条船舶记录，可切换到对应的货舱管理区域。</div>
        </div>

        <div class="table-shell">
          <table class="data-table">
            <thead>
              <tr>
                <th>代码</th>
                <th>船名</th>
                <th>船型</th>
                <th>设计 GM</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="ship in store.ships"
                :key="ship.id"
                class="clickable-row"
                :class="{ selected: selectedShip?.id === ship.id }"
                @click="selectShip(ship)"
              >
                <td>{{ ship.shipCode }}</td>
                <td>{{ ship.shipName }}</td>
                <td>{{ formatShipType(ship.shipType) }}</td>
                <td>{{ formatNumber(ship.designGM) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </v-card-text>
    </v-card>

    <v-card v-if="selectedShip" class="page-card">
      <v-card-text>
        <div class="toolbar-row">
          <div>
            <div class="section-title">货舱管理 - {{ selectedShip.shipName }}</div>
            <div class="muted-text">为当前船舶维护各货舱尺寸、重量上限与重心位置。</div>
          </div>
          <v-chip color="secondary" variant="tonal">当前选中：{{ selectedShip.shipCode }}</v-chip>
        </div>

        <div class="form-grid mt-4">
          <v-text-field v-model="holdForm.holdNo" label="舱号" />
          <app-number-field v-model="holdForm.length" label="长度" :min="1" />
          <app-number-field v-model="holdForm.width" label="宽度" :min="1" />
          <app-number-field v-model="holdForm.height" label="高度" :min="1" />
          <app-number-field v-model="holdForm.volume" label="容积" :min="1" />
          <app-number-field v-model="holdForm.lcg" label="LCG" />
          <app-number-field v-model="holdForm.tcg" label="TCG" />
          <app-number-field v-model="holdForm.vcg" label="VCG" :min="0" />
          <app-number-field v-model="holdForm.maxLoadWeight" label="最大载重" :min="1" />
          <app-number-field v-model="holdForm.deckStrengthLimit" label="甲板强度上限" :min="1" />
          <app-number-field v-model="holdForm.sequenceNo" label="顺序号" :min="1" />
        </div>

        <v-textarea v-model="holdForm.remark" label="备注" rows="2" class="mt-4" />

        <div class="mt-4">
          <v-btn color="primary" @click="saveHold">保存货舱</v-btn>
        </div>

        <div class="table-shell mt-6">
          <table class="data-table">
            <thead>
              <tr>
                <th>舱号</th>
                <th>长度</th>
                <th>宽度</th>
                <th>高度</th>
                <th>容积</th>
                <th>最大载重</th>
                <th>LCG</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="hold in holds" :key="hold.id">
                <td>{{ hold.holdNo }}</td>
                <td>{{ formatNumber(hold.length) }}</td>
                <td>{{ formatNumber(hold.width) }}</td>
                <td>{{ formatNumber(hold.height) }}</td>
                <td>{{ formatNumber(hold.volume) }}</td>
                <td>{{ formatNumber(hold.maxLoadWeight) }}</td>
                <td>{{ formatNumber(hold.lcg) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';

import AppNumberField from '@/components/AppNumberField.vue';
import { usePlanStore } from '@/store/plan';
import { useUiStore } from '@/store/ui';
import type { Hold, Ship } from '@/types';
import { formatNumber, formatShipType } from '@/utils/formatters';

const store = usePlanStore();
const ui = useUiStore();
const selectedShip = ref<Ship | null>(null);

const shipTypes = [{ title: '件杂货船', value: 'GENERAL_CARGO' }];

function buildSuffix() {
  return `${Date.now().toString().slice(-6)}${Math.floor(Math.random() * 100)
    .toString()
    .padStart(2, '0')}`;
}

function createShipForm(): Ship {
  const suffix = buildSuffix();
  return {
    shipCode: `GC-${suffix}`,
    shipName: `示例船舶 ${suffix}`,
    shipType: 'GENERAL_CARGO',
    lengthOverall: 96,
    lengthBetweenPerpendiculars: 90,
    beam: 16.8,
    depth: 9.2,
    lightshipWeight: 1680,
    lightshipKG: 5.5,
    lightshipLCG: 47,
    lightshipTCG: 0,
    designDisplacement: 3650,
    designGM: 1.6,
    remark: '示例件杂货船',
  };
}

function createHoldForm(sequenceNo = 1): Omit<Hold, 'shipId'> {
  return {
    holdNo: `H${sequenceNo}`,
    length: 17,
    width: 12,
    height: 8,
    volume: 1632,
    lcg: 19,
    tcg: 0,
    vcg: 5,
    maxLoadWeight: 420,
    deckStrengthLimit: 7.5,
    sequenceNo,
    remark: `第 ${sequenceNo} 舱`,
  };
}

const shipForm = reactive<Ship>(createShipForm());
const holdForm = reactive<Omit<Hold, 'shipId'>>(createHoldForm());
const holds = computed(() => (selectedShip.value?.id ? store.holdsByShip[selectedShip.value.id] ?? [] : []));

watch(
  holds,
  (value) => {
    const nextSequence = Math.max(1, value.length + 1);
    holdForm.holdNo = `H${nextSequence}`;
    holdForm.sequenceNo = nextSequence;
    holdForm.remark = `第 ${nextSequence} 舱`;
  },
  { immediate: true },
);

onMounted(() => {
  store.loadBaseData();
});

function selectShip(ship: Ship) {
  selectedShip.value = ship;
  if (ship.id) {
    store.loadHolds(ship.id);
  }
}

async function saveShip() {
  try {
    await store.saveShip(shipForm);
    ui.success('船舶已保存');
    Object.assign(shipForm, createShipForm());
  } catch (error) {
    ui.error((error as Error).message);
  }
}

async function saveHold() {
  if (!selectedShip.value?.id) {
    ui.warning('请先选择船舶');
    return;
  }
  try {
    await store.saveHold(selectedShip.value.id, holdForm);
    ui.success('货舱已保存');
    Object.assign(holdForm, createHoldForm((holds.value?.length ?? 0) + 1));
  } catch (error) {
    ui.error((error as Error).message);
  }
}
</script>

<style scoped>
.table-shell {
  overflow-x: auto;
}

.clickable-row {
  cursor: pointer;
  transition: background-color 160ms ease;
}

.clickable-row:hover {
  background: rgba(15, 92, 115, 0.05);
}

.clickable-row.selected {
  background: rgba(15, 92, 115, 0.1);
}
</style>
