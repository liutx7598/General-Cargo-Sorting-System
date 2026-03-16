<template>
  <el-container style="min-height: 100vh;">
    <el-aside width="230px" style="background: rgba(18, 78, 102, 0.92); color: white;">
      <div style="padding: 24px 18px; font-size: 20px; font-weight: 700;">件杂货智能配载</div>
      <el-menu router background-color="transparent" text-color="#f8fafc" active-text-color="#fbbf24">
        <el-menu-item index="/ships">船舶管理</el-menu-item>
        <el-menu-item index="/cargos">货物管理</el-menu-item>
        <el-menu-item index="/voyages">航次管理</el-menu-item>
        <el-menu-item index="/plans">配载任务</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display: flex; justify-content: space-between; align-items: center; padding: 20px 24px;">
        <div>
          <div style="font-size: 24px; font-weight: 700;">件杂货智能配载系统</div>
          <div style="color: #64748b;">几何 -> 重心 -> 稳性 -> 规则 -> 结论</div>
        </div>
        <el-tag type="info">MVP 原型</el-tag>
      </el-header>
      <el-main style="padding: 0 24px 24px;">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
