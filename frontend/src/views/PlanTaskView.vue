<template>
  <div class="page-grid">
    <div class="page-card">
      <div class="section-title">创建配载任务</div>
      <el-form :model="taskForm" label-width="140px">
        <el-form-item label="航次">
          <el-select v-model="taskForm.voyageId" style="width: 320px;">
            <el-option v-for="voyage in store.voyages" :key="voyage.id" :label="voyage.voyageNo" :value="voyage.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="方案编号">
          <el-input v-model="taskForm.planNo" style="width: 320px;" />
        </el-form-item>
        <el-form-item label="选择货物">
          <el-select v-model="selectedCargoIds" multiple filterable style="width: 100%;">
            <el-option
              v-for="cargo in store.cargos"
              :key="cargo.id"
              :label="`${cargo.cargoCode} - ${cargo.cargoName}`"
              :value="cargo.id"
            />
          </el-select>
        </el-form-item>
        <el-divider>阈值配置</el-divider>
        <el-form-item label="GM 下限"><el-input-number v-model="config.gmMin" :min="0" /></el-form-item>
        <el-form-item label="相邻舱差"><el-input-number v-model="config.adjacentHoldDiffMax" :min="0" :step="0.1" /></el-form-item>
        <el-form-item label="Ix 上限"><el-input-number v-model="config.ixMax" :min="0" :step="100" /></el-form-item>
        <el-form-item label="求解时限"><el-input-number v-model="config.solverTimeLimitSeconds" :min="1" /></el-form-item>
        <el-form-item label="默认隔离距离">
          <el-input-number v-model="config.defaultIsolationDistance" :min="0" :step="0.5" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="store.loading" @click="createAndGenerate">生成方案</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="page-card">
      <div class="section-title">已有方案</div>
      <el-table :data="store.plans" stripe>
        <el-table-column prop="planNo" label="方案号" width="180" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">{{ formatStatus(row.status) }}</template>
        </el-table-column>
        <el-table-column label="结论" width="120">
          <template #default="{ row }">{{ formatCompliance(row.complianceStatus) }}</template>
        </el-table-column>
        <el-table-column prop="gm" label="GM" width="120" />
        <el-table-column label="操作" width="260">
          <template #default="{ row }">
            <el-button link type="primary" @click="goResult(row.id)">结果</el-button>
            <el-button link type="warning" @click="goVisualization(row.id)">可视化</el-button>
            <el-button link type="danger" @click="goWarnings(row.id)">告警</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

import { defaultSolverConfig, usePlanStore } from '@/store/plan';

const router = useRouter();
const store = usePlanStore();
const selectedCargoIds = ref<number[]>([11, 12, 13, 14]);

function buildPlanNo() {
  return `PLAN-${Date.now()}-${Math.floor(Math.random() * 100)
    .toString()
    .padStart(2, '0')}`;
}

const taskForm = reactive({
  voyageId: 1,
  planNo: buildPlanNo(),
  remark: '前端页面生成',
});
const config = reactive({ ...defaultSolverConfig });

onMounted(async () => {
  await store.loadBaseData();
  if (!store.voyages.find((voyage) => voyage.id === taskForm.voyageId) && store.voyages[0]?.id) {
    taskForm.voyageId = store.voyages[0].id;
  }
  if (!selectedCargoIds.value.length && store.cargos.length) {
    selectedCargoIds.value = store.cargos.slice(0, 4).map((cargo) => cargo.id!).filter(Boolean);
  }
});

async function createAndGenerate() {
  try {
    taskForm.planNo = buildPlanNo();
    const plan = await store.createPlan(taskForm);
    if (!plan.id) {
      return;
    }
    await store.generate(plan.id, {
      cargoIds: selectedCargoIds.value,
      config,
    });
    ElMessage.success('方案已生成');
    taskForm.planNo = buildPlanNo();
    router.push(`/plans/${plan.id}/result`);
  } catch (error) {
    ElMessage.error((error as Error).message);
  }
}

function goResult(id: number) {
  router.push(`/plans/${id}/result`);
}

function goVisualization(id: number) {
  router.push(`/plans/${id}/visualization`);
}

function goWarnings(id: number) {
  router.push(`/plans/${id}/warnings`);
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
