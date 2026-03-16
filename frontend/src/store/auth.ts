import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    loggedIn: false,
    username: 'planner',
  }),
  actions: {
    login(username: string) {
      this.username = username;
      this.loggedIn = true;
    },
    logout() {
      this.loggedIn = false;
    },
  },
});

