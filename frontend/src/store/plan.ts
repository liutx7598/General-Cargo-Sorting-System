import { defineStore } from 'pinia';

import { api } from '@/api/stowage';
import type { Cargo, GeneratePlanCommand, Hold, Plan, PlanDetail, Ship, ValidatePlanCommand, Voyage } from '@/types';

export const defaultSolverConfig = {
  gmMin: 0.5,
  adjacentHoldDiffMax: 0.4,
  ixMax: 5000,
  solverTimeLimitSeconds: 10,
  fsc: 0,
  defaultIsolationDistance: 1,
  maxIterations: 3,
};

export const usePlanStore = defineStore('plan', {
  state: () => ({
    ships: [] as Ship[],
    holdsByShip: {} as Record<number, Hold[]>,
    cargos: [] as Cargo[],
    voyages: [] as Voyage[],
    plans: [] as Plan[],
    selectedPlanDetail: null as PlanDetail | null,
    loading: false,
  }),
  actions: {
    async loadBaseData() {
      this.loading = true;
      try {
        const [ships, cargos, voyages, plans] = await Promise.all([
          api.listShips(),
          api.listCargos(),
          api.listVoyages(),
          api.listPlans(),
        ]);
        this.ships = ships;
        this.cargos = cargos;
        this.voyages = voyages;
        this.plans = plans;
      } finally {
        this.loading = false;
      }
    },
    async loadHolds(shipId: number) {
      this.holdsByShip[shipId] = await api.listHolds(shipId);
    },
    async saveShip(payload: Ship) {
      await api.saveShip(payload);
      await this.loadBaseData();
    },
    async saveCargo(payload: Cargo) {
      await api.saveCargo(payload);
      await this.loadBaseData();
    },
    async saveCargos(payloads: Cargo[]) {
      this.loading = true;
      try {
        for (const payload of payloads) {
          await api.saveCargo(payload);
        }
        await this.loadBaseData();
      } finally {
        this.loading = false;
      }
    },
    async saveVoyage(payload: Voyage) {
      await api.saveVoyage(payload);
      await this.loadBaseData();
    },
    async saveHold(shipId: number, payload: Omit<Hold, 'shipId'> & { id?: number }) {
      await api.saveHold(shipId, payload);
      await this.loadHolds(shipId);
    },
    async createPlan(payload: Pick<Plan, 'voyageId' | 'planNo' | 'remark'>) {
      const plan = await api.createPlan(payload);
      await this.loadBaseData();
      return plan;
    },
    async fetchPlan(planId: number) {
      this.selectedPlanDetail = await api.getPlanDetail(planId);
      return this.selectedPlanDetail;
    },
    async generate(planId: number, payload: GeneratePlanCommand) {
      this.loading = true;
      try {
        this.selectedPlanDetail = await api.generatePlan(planId, payload);
        await this.loadBaseData();
        return this.selectedPlanDetail;
      } finally {
        this.loading = false;
      }
    },
    async validate(planId: number, payload: ValidatePlanCommand) {
      this.loading = true;
      try {
        this.selectedPlanDetail = await api.validatePlan(planId, payload);
        await this.loadBaseData();
        return this.selectedPlanDetail;
      } finally {
        this.loading = false;
      }
    },
  },
});
