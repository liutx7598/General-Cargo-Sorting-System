<template>
  <v-layout class="app-shell">
    <v-navigation-drawer permanent width="260" color="primary">
      <div class="drawer-head">
        <div class="drawer-title">件杂货智能配载</div>
        <div class="drawer-subtitle">General Cargo Stowage</div>
      </div>

      <v-list nav density="comfortable" theme="dark">
        <v-list-item
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          rounded="xl"
        />
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-app-bar flat color="transparent" height="88">
        <div class="topbar">
          <div>
            <div class="topbar-title">件杂货智能配载系统</div>
            <div class="topbar-subtitle">几何 → 重心 → 稳性 → 规则 → 结论</div>
          </div>
          <div class="topbar-actions">
            <v-chip color="info" variant="tonal">MVP Prototype</v-chip>
          </div>
        </div>
      </v-app-bar>

      <v-container fluid class="main-container">
        <router-view />
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup lang="ts">
const navItems = [
  { to: '/ships', title: '船舶管理', icon: 'mdi-ferry' },
  { to: '/cargos', title: '货物管理', icon: 'mdi-package-variant-closed' },
  { to: '/voyages', title: '航次管理', icon: 'mdi-map-marker-path' },
  { to: '/plans', title: '配载任务', icon: 'mdi-view-dashboard-edit-outline' },
];
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.drawer-head {
  padding: 28px 20px 18px;
  color: white;
}

.drawer-title {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 0.4px;
}

.drawer-subtitle {
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.78);
  font-size: 13px;
}

.topbar {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 0 24px 0 12px;
}

.topbar-title {
  font-size: 28px;
  font-weight: 800;
  color: #17324d;
}

.topbar-subtitle {
  color: #617182;
  font-size: 14px;
}

.main-container {
  padding: 8px 24px 24px;
}

@media (max-width: 960px) {
  .topbar {
    padding-right: 8px;
  }

  .topbar-title {
    font-size: 22px;
  }
}
</style>
