import client, { unwrap } from './client';
import type {
  Cargo,
  GeneratePlanCommand,
  Hold,
  Plan,
  PlanDetail,
  Ship,
  ValidatePlanCommand,
  Voyage,
} from '@/types';

export const api = {
  listShips: () => unwrap<Ship[]>(client.get('/ships')),
  saveShip: (payload: Ship) => unwrap<Ship>(client.post('/ships', payload)),
  listHolds: (shipId: number) => unwrap<Hold[]>(client.get(`/ships/${shipId}/holds`)),
  saveHold: (shipId: number, payload: Omit<Hold, 'shipId'> & { id?: number }) =>
    unwrap<Hold>(client.post(`/ships/${shipId}/holds`, payload)),
  listCargos: () => unwrap<Cargo[]>(client.get('/cargos')),
  saveCargo: (payload: Cargo) => unwrap<Cargo>(client.post('/cargos', payload)),
  listVoyages: () => unwrap<Voyage[]>(client.get('/voyages')),
  saveVoyage: (payload: Voyage) => unwrap<Voyage>(client.post('/voyages', payload)),
  listPlans: () => unwrap<Plan[]>(client.get('/plans')),
  createPlan: (payload: Pick<Plan, 'voyageId' | 'planNo' | 'remark'>) => unwrap<Plan>(client.post('/plans', payload)),
  getPlanDetail: (planId: number) => unwrap<PlanDetail>(client.get(`/plans/${planId}`)),
  generatePlan: (planId: number, payload: GeneratePlanCommand) =>
    unwrap<PlanDetail>(client.post(`/plans/${planId}/generate`, payload)),
  validatePlan: (planId: number, payload: ValidatePlanCommand) =>
    unwrap<PlanDetail>(client.post(`/plans/${planId}/validate`, payload)),
};

