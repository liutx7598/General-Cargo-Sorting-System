<template>
  <div class="page-card viewer-card">
    <div class="viewer-top">
      <div>
        <div class="section-title">{{ hold ? `${hold.holdNo} 三维视图` : '货舱三维视图' }}</div>
        <div class="viewer-subtitle">
          {{ hold ? `尺寸 ${hold.length} x ${hold.width} x ${hold.height} 米` : '请选择货舱查看配载。' }}
        </div>
      </div>
      <div class="viewer-legend">
        <span class="legend-pill"><i class="legend-dot normal"></i>正常</span>
        <span class="legend-pill"><i class="legend-dot dangerous"></i>危险货</span>
        <span class="legend-pill"><i class="legend-dot warning"></i>告警</span>
      </div>
    </div>

    <div class="viewer-body">
      <div ref="canvasHostRef" class="viewer-canvas" @pointerdown="handlePointerDown"></div>
      <div class="side-panel">
        <div class="meta-card">
          <div class="meta-label">货物数</div>
          <div class="meta-value">{{ itemEntries.length }}</div>
        </div>
        <div class="meta-card">
          <div class="meta-label">利用率</div>
          <div class="meta-value">{{ holdUtilization }}</div>
        </div>
        <div class="meta-card">
          <div class="meta-label">告警数</div>
          <div class="meta-value danger">{{ holdWarningCount }}</div>
        </div>

        <div class="detail-panel">
          <div class="detail-title">当前货物</div>
          <template v-if="selectedEntry">
            <div class="detail-name">{{ selectedEntry.cargo?.cargoCode ?? `货物 ${selectedEntry.item.cargoId}` }}</div>
            <div class="detail-subtitle">{{ selectedEntry.cargo?.cargoName ?? '未命名货物' }}</div>
            <div class="detail-list">
              <span>类别：{{ formatCategory(selectedEntry.cargo?.cargoCategory) }}</span>
              <span>重量：{{ selectedEntry.cargo?.weight?.toFixed(1) ?? '-' }} 吨</span>
              <span>尺寸：{{ selectedEntry.item.placedLength }} x {{ selectedEntry.item.placedWidth }} x {{ selectedEntry.item.placedHeight }}</span>
              <span>原点：({{ selectedEntry.item.originX }}, {{ selectedEntry.item.originY }}, {{ selectedEntry.item.originZ }})</span>
              <span>层号：{{ selectedEntry.item.layerNo }}</span>
              <span>状态：{{ formatStatus(selectedEntry.item.status) }}</span>
              <span v-if="selectedEntry.hasWarning" class="warning-text">该货物存在关联告警。</span>
            </div>
          </template>
          <div v-else class="detail-empty">点击三维场景中的货物块查看详情。</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';

import type { Cargo, Hold, StowageItem, WarningRecord } from '@/types';

type ItemEntry = {
  key: string;
  item: StowageItem;
  cargo?: Cargo;
  hasWarning: boolean;
};

const props = defineProps<{
  hold: Hold | null;
  items: StowageItem[];
  cargos: Cargo[];
  warnings: WarningRecord[];
}>();

const canvasHostRef = ref<HTMLDivElement>();
const selectedKey = ref<string | null>(null);

let renderer: THREE.WebGLRenderer | null = null;
let scene: THREE.Scene | null = null;
let camera: THREE.PerspectiveCamera | null = null;
let controls: OrbitControls | null = null;
let resizeObserver: ResizeObserver | null = null;
let animationFrameId = 0;
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const itemMeshes = new Map<string, THREE.Mesh>();

const itemEntries = computed<ItemEntry[]>(() =>
  props.items.map((item, index) => {
    const cargo = props.cargos.find((entry) => entry.id === item.cargoId);
    const hasWarning = props.warnings.some((warning) => warning.cargoId === item.cargoId);
    return {
      key: `${item.id ?? index}-${item.cargoId}-${index}`,
      item,
      cargo,
      hasWarning,
    };
  }),
);

const selectedEntry = computed(() => itemEntries.value.find((entry) => entry.key === selectedKey.value) ?? null);

const holdUtilization = computed(() => {
  if (!props.hold?.volume) {
    return '0.0%';
  }
  const totalVolume = itemEntries.value.reduce(
    (sum, entry) => sum + entry.item.placedLength * entry.item.placedWidth * entry.item.placedHeight,
    0,
  );
  return `${((totalVolume / props.hold.volume) * 100).toFixed(1)}%`;
});

const holdWarningCount = computed(() => {
  const cargoIds = new Set(itemEntries.value.map((entry) => entry.item.cargoId));
  return props.warnings.filter(
    (warning) => warning.holdId === props.hold?.id || (warning.cargoId != null && cargoIds.has(warning.cargoId)),
  ).length;
});

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

function formatStatus(status?: string) {
  const statusMap: Record<string, string> = {
    PLACED: '已摆放',
    UNPLACED: '未摆放',
    GENERATED: '已生成',
  };
  return status ? (statusMap[status] ?? status) : '-';
}

function colorForEntry(entry: ItemEntry) {
  if (entry.hasWarning) {
    return '#c2410c';
  }
  if (entry.cargo?.dangerousClass) {
    return '#d17b0f';
  }
  return '#124e66';
}

function disposeThreeScene() {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
    animationFrameId = 0;
  }
  controls?.dispose();
  controls = null;
  itemMeshes.forEach((mesh) => {
    mesh.geometry.dispose();
    const material = mesh.material as THREE.Material;
    material.dispose();
  });
  itemMeshes.clear();
  renderer?.dispose();
  renderer = null;
  if (canvasHostRef.value) {
    canvasHostRef.value.innerHTML = '';
  }
  scene = null;
  camera = null;
}

function updateRendererSize() {
  if (!canvasHostRef.value || !renderer || !camera) {
    return;
  }
  const width = canvasHostRef.value.clientWidth;
  const height = canvasHostRef.value.clientHeight;
  renderer.setSize(width, height);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

function updateMeshHighlight() {
  itemEntries.value.forEach((entry) => {
    const mesh = itemMeshes.get(entry.key);
    if (!mesh) {
      return;
    }
    const material = mesh.material as THREE.MeshPhongMaterial;
    const isSelected = entry.key === selectedKey.value;
    material.opacity = selectedKey.value && !isSelected ? 0.56 : 0.88;
    material.emissive.set(isSelected ? '#fff7ed' : '#000000');
    material.emissiveIntensity = isSelected ? 0.42 : 0;
    material.needsUpdate = true;
  });
}

function animate() {
  if (!renderer || !scene || !camera || !controls) {
    return;
  }
  controls.update();
  renderer.render(scene, camera);
  animationFrameId = requestAnimationFrame(animate);
}

function renderScene() {
  disposeThreeScene();
  if (!canvasHostRef.value || !props.hold) {
    return;
  }

  scene = new THREE.Scene();
  scene.background = new THREE.Color('#edf5f9');

  camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1500);
  camera.position.set(props.hold.length * 1.08, props.hold.height * 1.2, props.hold.width * 1.75);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  canvasHostRef.value.appendChild(renderer.domElement);
  updateRendererSize();

  scene.add(new THREE.AmbientLight('#ffffff', 1.9));
  const mainLight = new THREE.DirectionalLight('#ffffff', 1.3);
  mainLight.position.set(props.hold.length, props.hold.height * 1.4, props.hold.width * 0.6);
  scene.add(mainLight);

  const secondaryLight = new THREE.DirectionalLight('#dbeafe', 0.9);
  secondaryLight.position.set(-props.hold.length * 0.6, props.hold.height, props.hold.width);
  scene.add(secondaryLight);

  const grid = new THREE.GridHelper(
    Math.max(props.hold.length, props.hold.width) * 1.2,
    10,
    '#cbd5e1',
    '#e2e8f0',
  );
  grid.rotation.x = Math.PI / 2;
  grid.position.set(props.hold.length / 2, -0.02, props.hold.width / 2);
  scene.add(grid);

  const axes = new THREE.AxesHelper(Math.max(props.hold.length, props.hold.width) * 0.25);
  axes.position.set(0, 0, 0);
  scene.add(axes);

  const holdBox = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(props.hold.length, props.hold.height, props.hold.width)),
    new THREE.LineBasicMaterial({ color: '#7c8ea3' }),
  );
  holdBox.position.set(props.hold.length / 2, props.hold.height / 2, props.hold.width / 2);
  scene.add(holdBox);

  const floor = new THREE.Mesh(
    new THREE.BoxGeometry(props.hold.length, 0.08, props.hold.width),
    new THREE.MeshPhongMaterial({ color: '#d9e2ec', transparent: true, opacity: 0.7 }),
  );
  floor.position.set(props.hold.length / 2, 0, props.hold.width / 2);
  scene.add(floor);

  itemEntries.value.forEach((entry) => {
    const material = new THREE.MeshPhongMaterial({
      color: colorForEntry(entry),
      transparent: true,
      opacity: 0.88,
      shininess: 65,
    });
    const geometry = new THREE.BoxGeometry(entry.item.placedLength, entry.item.placedHeight, entry.item.placedWidth);
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(
      entry.item.originX + entry.item.placedLength / 2,
      entry.item.originZ + entry.item.placedHeight / 2,
      entry.item.originY + entry.item.placedWidth / 2,
    );
    mesh.userData = { key: entry.key };
    itemMeshes.set(entry.key, mesh);
    scene?.add(mesh);
  });

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.minDistance = Math.max(props.hold.length, props.hold.width) * 0.3;
  controls.maxDistance = Math.max(props.hold.length, props.hold.width) * 4.2;
  controls.target.set(props.hold.length / 2, props.hold.height / 2.5, props.hold.width / 2);
  controls.update();

  updateMeshHighlight();
  animate();
}

function handlePointerDown(event: PointerEvent) {
  if (!renderer || !camera || !canvasHostRef.value) {
    return;
  }
  const bounds = canvasHostRef.value.getBoundingClientRect();
  pointer.x = ((event.clientX - bounds.left) / bounds.width) * 2 - 1;
  pointer.y = -((event.clientY - bounds.top) / bounds.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);

  const intersections = raycaster.intersectObjects([...itemMeshes.values()], false);
  if (!intersections.length) {
    selectedKey.value = null;
    updateMeshHighlight();
    return;
  }

  selectedKey.value = intersections[0].object.userData.key as string;
  updateMeshHighlight();
}

onMounted(() => {
  renderScene();
  if (typeof ResizeObserver !== 'undefined' && canvasHostRef.value) {
    resizeObserver = new ResizeObserver(() => updateRendererSize());
    resizeObserver.observe(canvasHostRef.value);
  }
});

watch(
  () => [props.hold, props.items, props.cargos, props.warnings],
  () => {
    selectedKey.value = null;
    renderScene();
  },
  { deep: true },
);

onBeforeUnmount(() => {
  resizeObserver?.disconnect();
  disposeThreeScene();
});
</script>

<style scoped>
.viewer-card {
  min-height: 580px;
}

.viewer-top {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.viewer-subtitle {
  color: #5f7383;
  font-size: 14px;
}

.viewer-legend {
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

.viewer-body {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.75fr);
  gap: 16px;
  align-items: stretch;
}

.viewer-canvas {
  min-height: 470px;
  border-radius: 18px;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.7), rgba(219, 234, 254, 0.55));
  box-shadow: inset 0 0 0 1px rgba(18, 78, 102, 0.1);
}

.side-panel {
  display: grid;
  gap: 12px;
  align-content: start;
}

.meta-card {
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid rgba(18, 78, 102, 0.1);
}

.meta-label {
  color: #64748b;
  font-size: 13px;
  margin-bottom: 6px;
}

.meta-value {
  font-size: 24px;
  font-weight: 700;
  color: #124e66;
}

.meta-value.danger {
  color: #c2410c;
}

.detail-panel {
  padding: 16px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.8), rgba(18, 78, 102, 0.06));
  border: 1px solid rgba(18, 78, 102, 0.12);
  min-height: 228px;
}

.detail-title {
  font-weight: 700;
  margin-bottom: 12px;
}

.detail-name {
  font-size: 18px;
  font-weight: 700;
  color: #124e66;
}

.detail-subtitle {
  color: #5f7383;
  margin: 4px 0 14px;
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
  color: #334155;
}

.detail-empty {
  color: #64748b;
  font-size: 14px;
  line-height: 1.6;
}

.warning-text {
  color: #c2410c;
  font-weight: 600;
}

@media (max-width: 1080px) {
  .viewer-top {
    flex-direction: column;
  }

  .viewer-body {
    grid-template-columns: 1fr;
  }

  .viewer-canvas {
    min-height: 380px;
  }
}
</style>
