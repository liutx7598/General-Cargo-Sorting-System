<template>
  <div class="page-shell">
    <v-card class="page-card">
      <v-card-text>
        <div class="toolbar-row">
          <div>
            <div class="section-title">货物管理</div>
            <div class="muted-text">维护货物基础参数，并支持按当前记录快速复制多件同款货物。</div>
          </div>
          <v-chip color="accent" variant="tonal">专利增强：隔离等级</v-chip>
        </div>

        <div class="form-grid mt-4">
          <v-text-field v-model="cargoForm.cargoCode" label="编码" />
          <v-text-field v-model="cargoForm.cargoName" label="名称" />
          <v-select
            v-model="cargoForm.cargoCategory"
            :items="cargoCategories"
            item-title="title"
            item-value="value"
            label="类别"
          />
          <v-text-field v-model="cargoForm.dangerousClass" label="危险类别" />
          <v-text-field v-model="cargoForm.incompatibleTags" label="不兼容标签" />
          <app-number-field v-model="cargoForm.isolationLevel" label="最小隔离距离(m)" :min="0" />
          <app-number-field v-model="cargoForm.segregationCode" label="隔离等级(0-4)" :min="0" :max="4" />
          <app-number-field v-model="cargoForm.weight" label="重量" :min="1" />
          <app-number-field v-model="cargoForm.length" label="长" :min="0.1" :step="0.1" />
          <app-number-field v-model="cargoForm.width" label="宽" :min="0.1" :step="0.1" />
          <app-number-field v-model="cargoForm.height" label="高" :min="0.1" :step="0.1" />
          <app-number-field v-model="cargoForm.centerOffsetX" label="偏心 X" :step="0.1" />
          <app-number-field v-model="cargoForm.centerOffsetY" label="偏心 Y" :step="0.1" />
          <app-number-field v-model="cargoForm.centerOffsetZ" label="偏心 Z" :step="0.1" />
        </div>

        <div class="switch-row mt-2">
          <v-switch v-model="cargoForm.stackable" label="可堆叠" />
          <v-switch v-model="cargoForm.rotatable" label="可旋转" />
        </div>

        <v-textarea v-model="cargoForm.remark" label="备注" rows="2" class="mt-2" />

        <div class="mt-4">
          <v-btn color="primary" @click="saveCargo">保存货物</v-btn>
        </div>
      </v-card-text>
    </v-card>

    <v-card class="page-card">
      <v-card-text>
        <div class="toolbar-row">
          <div>
            <div class="section-title">货物列表</div>
            <div class="muted-text">可直接按选中货物快速复制多件同规格记录。</div>
          </div>
          <div class="quick-actions">
            <app-number-field v-model="quickAddCount" label="快速新增数量" :min="1" :max="20" />
          </div>
        </div>

        <div class="table-shell">
          <table class="data-table">
            <thead>
              <tr>
                <th>编码</th>
                <th>名称</th>
                <th>类别</th>
                <th>危险类</th>
                <th>隔离等级</th>
                <th>重量</th>
                <th>尺寸</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cargo in store.cargos" :key="cargo.id">
                <td>{{ cargo.cargoCode }}</td>
                <td>{{ cargo.cargoName }}</td>
                <td>{{ formatCargoCategory(cargo.cargoCategory) }}</td>
                <td>{{ cargo.dangerousClass ?? '-' }}</td>
                <td>{{ cargo.segregationCode > 0 ? cargo.segregationCode : '-' }}</td>
                <td>{{ formatNumber(cargo.weight, 1) }}</td>
                <td>{{ cargo.length }} x {{ cargo.width }} x {{ cargo.height }}</td>
                <td class="action-cell">
                  <v-btn size="small" color="primary" variant="text" @click="quickAddCargo(cargo)">
                    +{{ quickAddCount }} 同款货物
                  </v-btn>
                  <v-btn size="small" color="secondary" variant="text" @click="fillCargoForm(cargo)">
                    用作模板
                  </v-btn>
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
import { onMounted, reactive, ref } from 'vue';

import AppNumberField from '@/components/AppNumberField.vue';
import { usePlanStore } from '@/store/plan';
import { useUiStore } from '@/store/ui';
import type { Cargo } from '@/types';
import { formatCargoCategory, formatNumber } from '@/utils/formatters';

const store = usePlanStore();
const ui = useUiStore();

const cargoCategories = [
  { title: '钢材', value: 'STEEL' },
  { title: '木材', value: 'TIMBER' },
  { title: '设备', value: 'EQUIPMENT' },
  { title: '工程货', value: 'PROJECT' },
  { title: '管材', value: 'PIPE' },
  { title: '危险货', value: 'DANGEROUS' },
];

function buildSuffix() {
  return `${Date.now().toString().slice(-6)}${Math.floor(Math.random() * 100)
    .toString()
    .padStart(2, '0')}`;
}

function createCargoForm(): Cargo {
  const suffix = buildSuffix();
  return {
    cargoCode: `CG-${suffix}`,
    cargoName: `货物 ${suffix}`,
    cargoCategory: 'STEEL',
    dangerousClass: null,
    incompatibleTags: '',
    isolationLevel: 0,
    segregationCode: 0,
    weight: 10,
    length: 2,
    width: 2,
    height: 2,
    stackable: true,
    rotatable: true,
    centerOffsetX: 0,
    centerOffsetY: 0,
    centerOffsetZ: 0,
    remark: '',
  };
}

const cargoForm = reactive<Cargo>(createCargoForm());
const quickAddCount = ref(1);

onMounted(() => store.loadBaseData());

async function saveCargo() {
  try {
    await store.saveCargo(cargoForm);
    ui.success('货物已保存');
    Object.assign(cargoForm, createCargoForm());
  } catch (error) {
    ui.error((error as Error).message);
  }
}

function nextCloneCode(baseCode: string, existingCodes: Set<string>) {
  let index = 1;
  let candidate = `${baseCode}-C${index.toString().padStart(2, '0')}`;
  while (existingCodes.has(candidate)) {
    index += 1;
    candidate = `${baseCode}-C${index.toString().padStart(2, '0')}`;
  }
  existingCodes.add(candidate);
  return { code: candidate, index };
}

function buildCargoClone(baseCargo: Cargo, existingCodes: Set<string>): Cargo {
  const next = nextCloneCode(baseCargo.cargoCode, existingCodes);
  return {
    ...baseCargo,
    id: undefined,
    segregationCode: baseCargo.segregationCode ?? 0,
    cargoCode: next.code,
    cargoName: `${baseCargo.cargoName} 副本 ${next.index.toString().padStart(2, '0')}`,
  };
}

async function quickAddCargo(baseCargo: Cargo) {
  try {
    const existingCodes = new Set(store.cargos.map((cargo) => cargo.cargoCode));
    const clones = Array.from({ length: quickAddCount.value }, () => buildCargoClone(baseCargo, existingCodes));
    const batchSave = (store as typeof store & { saveCargos?: (payloads: Cargo[]) => Promise<void> }).saveCargos;
    if (typeof batchSave === 'function') {
      await batchSave.call(store, clones);
    } else {
      for (const cargo of clones) {
        await store.saveCargo(cargo);
      }
    }
    ui.success(`已新增 ${clones.length} 条同款货物`);
  } catch (error) {
    ui.error((error as Error).message);
  }
}

function fillCargoForm(baseCargo: Cargo) {
  const existingCodes = new Set(store.cargos.map((cargo) => cargo.cargoCode));
  const template = buildCargoClone(baseCargo, existingCodes);
  Object.assign(cargoForm, template);
}
</script>

<style scoped>
.switch-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.table-shell {
  overflow-x: auto;
}

.quick-actions {
  min-width: 180px;
}

.action-cell {
  white-space: nowrap;
}
</style>
