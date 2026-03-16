import { createApp } from 'vue';
import { createPinia } from 'pinia';

import App from './App.vue';
import { vuetify } from './plugins/vuetify';
import router from './router';
import { useUiStore } from './store/ui';
import './assets/main.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(vuetify);

const ui = useUiStore(pinia);

app.config.errorHandler = (error) => {
  ui.error(error instanceof Error ? error.message : '页面发生异常');
};

window.addEventListener('unhandledrejection', (event) => {
  const reason = event.reason;
  ui.error(reason instanceof Error ? reason.message : '请求失败');
});

app.mount('#app');
