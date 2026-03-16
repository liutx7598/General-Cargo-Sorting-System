<template>
  <div ref="chartRef" class="page-card" style="height: 360px;"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import * as echarts from 'echarts';

import type { HoldMetric } from '@/types';

const props = defineProps<{
  holds: HoldMetric[];
  warningCount: number;
  gm?: number;
}>();

const chartRef = ref<HTMLDivElement>();
let chart: echarts.ECharts | undefined;

function render() {
  if (!chartRef.value) return;
  chart ??= echarts.init(chartRef.value);
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { top: 8 },
    xAxis: { type: 'category', data: props.holds.map((item) => item.holdNo) },
    yAxis: [{ type: 'value', name: '重量/容积' }],
    series: [
      {
        type: 'bar',
        name: '重量',
        data: props.holds.map((item) => item.totalWeight),
        itemStyle: { color: '#124e66' },
      },
      {
        type: 'bar',
        name: '利用率',
        data: props.holds.map((item) => Number((item.utilization * 100).toFixed(2))),
        itemStyle: { color: '#d17b0f' },
      },
      {
        type: 'line',
        name: 'GM',
        data: props.holds.map(() => props.gm ?? 0),
        itemStyle: { color: '#748cab' },
      },
    ],
    graphic: [
      {
        type: 'text',
        left: '75%',
        top: '10%',
        style: {
          text: `告警数 ${props.warningCount}`,
          fill: '#c2410c',
          font: '600 18px sans-serif',
        },
      },
    ],
  });
}

onMounted(render);
watch(() => props.holds, render, { deep: true });
watch(() => props.warningCount, render);
watch(() => props.gm, render);
onBeforeUnmount(() => chart?.dispose());
</script>
