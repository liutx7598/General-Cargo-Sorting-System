<template>
  <div style="min-height: 100vh; display: grid; place-items: center; padding: 24px;">
    <div class="page-card" style="width: min(460px, 100%);">
      <div style="font-size: 30px; font-weight: 700; margin-bottom: 12px;">件杂货智能配载系统</div>
      <div style="color: #64748b; margin-bottom: 20px;">MVP 登录页，便于快速进入主流程联调。</div>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-button type="primary" style="width: 100%;" @click="handleLogin">进入系统</el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { useRouter } from 'vue-router';

import { useAuthStore } from '@/store/auth';

const router = useRouter();
const authStore = useAuthStore();
const form = reactive({
  username: 'planner',
  password: 'demo',
});

function handleLogin() {
  authStore.login(form.username);
  router.push('/ships');
}
</script>
