import { createRouter, createWebHistory } from 'vue-router';

import { useAuthStore } from '@/store/auth';

const routes = [
  { path: '/login', component: () => import('@/views/LoginView.vue') },
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    children: [
      { path: '', redirect: '/ships' },
      { path: 'ships', component: () => import('@/views/ShipManagementView.vue') },
      { path: 'cargos', component: () => import('@/views/CargoManagementView.vue') },
      { path: 'voyages', component: () => import('@/views/VoyageManagementView.vue') },
      { path: 'plans', component: () => import('@/views/PlanTaskView.vue') },
      { path: 'plans/:id/result', component: () => import('@/views/PlanResultView.vue') },
      { path: 'plans/:id/visualization', component: () => import('@/views/HoldVisualizationView.vue') },
      { path: 'plans/:id/warnings', component: () => import('@/views/WarningPanelView.vue') },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const authStore = useAuthStore();
  if (to.path !== '/login' && !authStore.loggedIn) {
    return '/login';
  }
  if (to.path === '/login' && authStore.loggedIn) {
    return '/ships';
  }
  return true;
});

export default router;

