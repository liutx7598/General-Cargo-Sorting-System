<template>
  <div class="page-grid">
    <div class="page-card">
      <div class="section-title">货物管理</div>
      <el-form :model="cargoForm" inline>
        <el-form-item label="编码"><el-input v-model="cargoForm.cargoCode" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="cargoForm.cargoName" /></el-form-item>
        <el-form-item label="类别">
          <el-select v-model="cargoForm.cargoCategory" style="width: 180px;">
            <el-option label="钢材" value="STEEL" />
            <el-option label="木材" value="TIMBER" />
            <el-option label="设备" value="EQUIPMENT" />
            <el-option label="工程货" value="PROJECT" />
            <el-option label="管材" value="PIPE" />
            <el-option label="危险货" value="DANGEROUS" />
          </el-select>
        </el-form-item>
        <el-form-item label="危险等级"><el-input v-model="cargoForm.dangerousClass" /></el-form-item>
        <el-form-item label="不兼容标签"><el-input v-model="cargoForm.incompatibleTags" /></el-form-item>
        <el-form-item label="隔离等级"><el-input-number v-model="cargoForm.isolationLevel" :min="0" /></el-form-item>
        <el-form-item label="重量"><el-input-number v-model="cargoForm.weight" :min="1" /></el-form-item>
        <el-form-item label="长"><el-input-number v-model="cargoForm.length" :min="0.1" /></el-form-item>
        <el-form-item label="宽"><el-input-number v-model="cargoForm.width" :min="0.1" /></el-form-item>
        <el-form-item label="高"><el-input-number v-model="cargoForm.height" :min="0.1" /></el-form-item>
        <el-form-item label="可堆叠"><el-switch v-model="cargoForm.stackable" /></el-form-item>
        <el-form-item label="可旋转"><el-switch v-model="cargoForm.rotatable" /></el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveCargo">保存货物</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="page-card">
      <div class="cargo-toolbar">
        <div class="section-title">货物列表</div>
        <div class="cargo-toolbar-actions">
          <span class="cargo-toolbar-label">快速新增数量</span>
          <el-input-number v-model="quickAddCount" :min="1" :max="20" />
        </div>
      </div>
      <el-table :data="store.cargos" stripe>
        <el-table-column prop="cargoCode" label="编码" width="120" />
        <el-table-column prop="cargoName" label="名称" />
        <el-table-column label="类别" width="120">
          <template #default="{ row }">{{ formatCargoCategory(row.cargoCategory) }}</template>
        </el-table-column>
        <el-table-column prop="dangerousClass" label="危险品" width="100" />
        <el-table-column prop="weight" label="重量" width="100" />
        <el-table-column label="尺寸" min-width="200">
          <template #default="{ row }">{{ row.length }} x {{ row.width }} x {{ row.height }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="quickAddCargo(row)">+{{ quickAddCount }} 同款货物</el-button>
            <el-button link @click="fillCargoForm(row)">用作模板</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';

import { usePlanStore } from '@/store/plan';
import type { Cargo } from '@/types';

const store = usePlanStore();

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
    ElMessage.success('货物已保存');
    Object.assign(cargoForm, createCargoForm());
  } catch (error) {
    ElMessage.error((error as Error).message);
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
    ElMessage.success(`已新增 ${clones.length} 条同款货物`);
  } catch (error) {
    ElMessage.error((error as Error).message);
  }
}

function fillCargoForm(baseCargo: Cargo) {
  const existingCodes = new Set(store.cargos.map((cargo) => cargo.cargoCode));
  const template = buildCargoClone(baseCargo, existingCodes);
  Object.assign(cargoForm, template);
}

function formatCargoCategory(category: string) {
  const categoryMap: Record<string, string> = {
    STEEL: '钢材',
    TIMBER: '木材',
    EQUIPMENT: '设备',
    PROJECT: '工程货',
    PIPE: '管材',
    DANGEROUS: '危险货',
  };
  return categoryMap[category] ?? category;
}
</script>

<style scoped>
.cargo-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 14px;
}

.cargo-toolbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.cargo-toolbar-label {
  color: #5f7383;
  font-size: 13px;
  font-weight: 600;
}

@media (max-width: 960px) {
  .cargo-toolbar {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
