import { createApp } from 'vue';
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import { ElMessage } from 'element-plus';
import 'element-plus/dist/index.css';

import App from './App.vue';
import router from './router';
import './assets/main.css';

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(ElementPlus);

app.config.errorHandler = (error) => {
  ElMessage.error(error instanceof Error ? error.message : '页面发生异常');
};

window.addEventListener('unhandledrejection', (event) => {
  const reason = event.reason;
  ElMessage.error(reason instanceof Error ? reason.message : '请求失败');
});

app.mount('#app');
