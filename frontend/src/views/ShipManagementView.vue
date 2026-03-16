<template>
  <div class="page-grid">
    <div class="page-card">
      <div class="section-title">船舶管理</div>
      <el-form :model="shipForm" inline>
        <el-form-item label="船舶代码"><el-input v-model="shipForm.shipCode" /></el-form-item>
        <el-form-item label="船名"><el-input v-model="shipForm.shipName" /></el-form-item>
        <el-form-item label="船型">
          <el-select v-model="shipForm.shipType" style="width: 180px;">
            <el-option label="件杂货船" value="GENERAL_CARGO" />
          </el-select>
        </el-form-item>
        <el-form-item label="总长"><el-input-number v-model="shipForm.lengthOverall" :min="1" /></el-form-item>
        <el-form-item label="垂线间长"><el-input-number v-model="shipForm.lengthBetweenPerpendiculars" :min="1" /></el-form-item>
        <el-form-item label="型宽"><el-input-number v-model="shipForm.beam" :min="1" /></el-form-item>
        <el-form-item label="型深"><el-input-number v-model="shipForm.depth" :min="1" /></el-form-item>
        <el-form-item label="空船重"><el-input-number v-model="shipForm.lightshipWeight" :min="1" /></el-form-item>
        <el-form-item label="KG"><el-input-number v-model="shipForm.lightshipKG" :min="0" /></el-form-item>
        <el-form-item label="LCG"><el-input-number v-model="shipForm.lightshipLCG" :min="0" /></el-form-item>
        <el-form-item label="设计排水量"><el-input-number v-model="shipForm.designDisplacement" :min="1" /></el-form-item>
        <el-form-item label="设计GM"><el-input-number v-model="shipForm.designGM" :min="0" /></el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveShip">保存船舶</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="page-card">
      <div class="section-title">船舶列表</div>
      <el-table :data="store.ships" stripe @row-click="selectShip">
        <el-table-column prop="shipCode" label="代码" width="140" />
        <el-table-column prop="shipName" label="船名" />
        <el-table-column label="船型" width="180">
          <template #default="{ row }">{{ formatShipType(row.shipType) }}</template>
        </el-table-column>
        <el-table-column prop="designGM" label="设计GM" width="120" />
      </el-table>
    </div>

    <div v-if="selectedShip" class="page-card">
      <div class="section-title">货舱管理 - {{ selectedShip.shipName }}</div>
      <el-form :model="holdForm" inline>
        <el-form-item label="舱号"><el-input v-model="holdForm.holdNo" /></el-form-item>
        <el-form-item label="长度"><el-input-number v-model="holdForm.length" :min="1" /></el-form-item>
        <el-form-item label="宽度"><el-input-number v-model="holdForm.width" :min="1" /></el-form-item>
        <el-form-item label="高度"><el-input-number v-model="holdForm.height" :min="1" /></el-form-item>
        <el-form-item label="容积"><el-input-number v-model="holdForm.volume" :min="1" /></el-form-item>
        <el-form-item label="LCG"><el-input-number v-model="holdForm.lcg" /></el-form-item>
        <el-form-item label="TCG"><el-input-number v-model="holdForm.tcg" /></el-form-item>
        <el-form-item label="VCG"><el-input-number v-model="holdForm.vcg" :min="0" /></el-form-item>
        <el-form-item label="最大载重"><el-input-number v-model="holdForm.maxLoadWeight" :min="1" /></el-form-item>
        <el-form-item label="甲板限值"><el-input-number v-model="holdForm.deckStrengthLimit" :min="1" /></el-form-item>
        <el-form-item label="顺序号"><el-input-number v-model="holdForm.sequenceNo" :min="1" /></el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveHold">保存货舱</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="holds" stripe>
        <el-table-column prop="holdNo" label="舱号" width="100" />
        <el-table-column prop="volume" label="容积" width="120" />
        <el-table-column prop="maxLoadWeight" label="最大载重" width="140" />
        <el-table-column prop="lcg" label="LCG" width="120" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';

import { usePlanStore } from '@/store/plan';
import type { Hold, Ship } from '@/types';

const store = usePlanStore();
const selectedShip = ref<Ship | null>(null);

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
    ElMessage.success('船舶已保存');
    Object.assign(shipForm, createShipForm());
  } catch (error) {
    ElMessage.error((error as Error).message);
  }
}

async function saveHold() {
  if (!selectedShip.value?.id) {
    ElMessage.warning('请先选择船舶');
    return;
  }
  try {
    await store.saveHold(selectedShip.value.id, holdForm);
    ElMessage.success('货舱已保存');
    Object.assign(holdForm, createHoldForm((holds.value?.length ?? 0) + 1));
  } catch (error) {
    ElMessage.error((error as Error).message);
  }
}

function formatShipType(shipType: string) {
  return shipType === 'GENERAL_CARGO' ? '件杂货船' : shipType;
}
</script>
