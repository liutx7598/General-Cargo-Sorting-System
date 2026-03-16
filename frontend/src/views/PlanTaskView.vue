<template>
  <div class="page-shell">
    <v-card class="page-card">
      <v-card-text>
        <div class="toolbar-row">
          <div>
            <div class="section-title">创建配载任务</div>
            <div class="muted-text">选择航次、货物和求解阈值，发起一次完整的配载求解。</div>
          </div>
          <v-chip color="primary" variant="tonal">求解时长 {{ config.solverTimeLimitSeconds }} 秒</v-chip>
        </div>

        <div class="form-grid mt-4">
          <v-select
            v-model="taskForm.voyageId"
            :items="voyageOptions"
            item-title="title"
            item-value="value"
            label="航次"
          />
          <v-text-field v-model="taskForm.planNo" label="方案编号" />
        </div>

        <v-autocomplete
          v-model="selectedCargoIds"
          :items="cargoOptions"
          item-title="title"
          item-value="value"
          label="选择货物"
          multiple
          chips
          closable-chips
          class="mt-4"
        />

        <v-divider class="my-4" />

        <div class="section-subtitle">阈值配置</div>
        <div class="form-grid mt-3">
          <app-number-field v-model="config.gmMin" label="GM 下限" :min="0" :step="0.1" />
          <app-number-field v-model="config.adjacentHoldDiffMax" label="相邻舱差异" :min="0" :step="0.1" />
          <app-number-field v-model="config.ixMax" label="Ix 上限" :min="0" :step="100" />
          <app-number-field v-model="config.solverTimeLimitSeconds" label="求解时限" :min="1" />
          <app-number-field v-model="config.defaultIsolationDistance" label="默认隔离距离" :min="0" :step="0.5" />
        </div>

        <div class="mt-4">
          <v-btn color="primary" :loading="store.loading" @click="createAndGenerate">生成方案</v-btn>
        </div>
      </v-card-text>
    </v-card>

    <v-card class="page-card">
      <v-card-text>
        <div class="section-title">已有方案</div>
        <div class="table-shell">
          <table class="data-table">
            <thead>
              <tr>
                <th>方案号</th>
                <th>状态</th>
                <th>结论</th>
                <th>GM</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="plan in store.plans" :key="plan.id">
                <td>{{ plan.planNo }}</td>
                <td>{{ formatStatus(plan.status) }}</td>
                <td>
                  <v-chip
                    size="small"
                    :color="plan.complianceStatus === 'PASS' ? 'success' : 'error'"
                    variant="tonal"
                  >
                    {{ formatCompliance(plan.complianceStatus) }}
                  </v-chip>
                </td>
                <td>{{ plan.gm != null ? plan.gm.toFixed(2) : '-' }}</td>
                <td class="action-cell">
                  <v-btn size="small" color="primary" variant="text" @click="goResult(plan.id!)">结果</v-btn>
                  <v-btn size="small" color="warning" variant="text" @click="goVisualization(plan.id!)">可视化</v-btn>
                  <v-btn size="small" color="error" variant="text" @click="goWarnings(plan.id!)">告警</v-btn>
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
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

import AppNumberField from '@/components/AppNumberField.vue';
import { defaultSolverConfig, usePlanStore } from '@/store/plan';
import { useUiStore } from '@/store/ui';
import { formatCompliance, formatStatus } from '@/utils/formatters';

const router = useRouter();
const store = usePlanStore();
const ui = useUiStore();
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

const voyageOptions = computed(() =>
  store.voyages.map((voyage) => ({
    title: voyage.voyageNo,
    value: voyage.id,
  })),
);

const cargoOptions = computed(() =>
  store.cargos.map((cargo) => ({
    title: `${cargo.cargoCode} - ${cargo.cargoName}`,
    value: cargo.id,
  })),
);

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
    ui.success('方案已生成');
    taskForm.planNo = buildPlanNo();
    router.push(`/plans/${plan.id}/result`);
  } catch (error) {
    ui.error((error as Error).message);
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
</script>

<style scoped>
.table-shell {
  overflow-x: auto;
}

.action-cell {
  white-space: nowrap;
}

.section-subtitle {
  font-size: 15px;
  font-weight: 700;
  color: #4f6d7a;
}
</style>
