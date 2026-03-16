import { defineStore } from 'pinia';

type SnackbarColor = 'success' | 'error' | 'warning' | 'info';

export const useUiStore = defineStore('ui', {
  state: () => ({
    snackbar: {
      visible: false,
      text: '',
      color: 'info' as SnackbarColor,
      timeout: 3000,
    },
  }),
  actions: {
    notify(text: string, color: SnackbarColor = 'info', timeout = 3000) {
      this.snackbar = {
        visible: true,
        text,
        color,
        timeout,
      };
    },
    success(text: string) {
      this.notify(text, 'success');
    },
    error(text: string) {
      this.notify(text, 'error', 4500);
    },
    warning(text: string) {
      this.notify(text, 'warning');
    },
  },
});
