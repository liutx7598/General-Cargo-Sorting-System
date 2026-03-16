<template>
  <div class="login-shell">
    <div class="login-backdrop"></div>
    <v-card class="login-card" rounded="xl" elevation="8">
      <v-card-text class="login-content">
        <div class="login-kicker">MVP Access</div>
        <h1 class="login-title">件杂货智能配载系统</h1>
        <p class="login-subtitle">
          当前登录页用于演示快速进入系统，不做复杂权限控制。
        </p>

        <div class="form-grid">
          <v-text-field v-model="form.username" label="用户名" prepend-inner-icon="mdi-account-circle-outline" />
          <v-text-field
            v-model="form.password"
            label="密码"
            type="password"
            prepend-inner-icon="mdi-lock-outline"
          />
        </div>

        <v-btn color="primary" size="large" block class="mt-4" @click="handleLogin">
          进入系统
        </v-btn>
      </v-card-text>
    </v-card>
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

<style scoped>
.login-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px;
  position: relative;
  overflow: hidden;
}

.login-backdrop {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 15% 20%, rgba(15, 92, 115, 0.18), transparent 28%),
    radial-gradient(circle at 85% 15%, rgba(197, 123, 20, 0.18), transparent 22%),
    linear-gradient(145deg, #eef4f8 0%, #dfe8f1 100%);
}

.login-card {
  width: min(520px, 100%);
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(8px);
}

.login-content {
  padding: 28px;
}

.login-kicker {
  color: #0f5c73;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.login-title {
  margin: 10px 0 8px;
  font-size: 34px;
  line-height: 1.1;
  color: #17324d;
}

.login-subtitle {
  margin: 0 0 22px;
  color: #617182;
  line-height: 1.6;
}
</style>
