export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface Ship {
  id?: number;
  shipCode: string;
  shipName: string;
  shipType: string;
  lengthOverall: number;
  lengthBetweenPerpendiculars: number;
  beam: number;
  depth: number;
  lightshipWeight: number;
  lightshipKG: number;
  lightshipLCG: number;
  lightshipTCG: number;
  designDisplacement: number;
  designGM: number;
  remark?: string;
}

export interface Hold {
  id?: number;
  shipId: number;
  holdNo: string;
  length: number;
  width: number;
  height: number;
  volume: number;
  lcg: number;
  tcg: number;
  vcg: number;
  maxLoadWeight: number;
  deckStrengthLimit: number;
  sequenceNo: number;
  remark?: string;
}

export interface Cargo {
  id?: number;
  cargoCode: string;
  cargoName: string;
  cargoCategory: string;
  dangerousClass?: string | null;
  incompatibleTags: string;
  isolationLevel: number;
  segregationCode: number;
  weight: number;
  length: number;
  width: number;
  height: number;
  stackable: boolean;
  rotatable: boolean;
  centerOffsetX: number;
  centerOffsetY: number;
  centerOffsetZ: number;
  remark?: string;
}

export interface Voyage {
  id?: number;
  voyageNo: string;
  shipId: number;
  routeInfo?: string;
  departurePort?: string;
  arrivalPort?: string;
  eta?: string;
  etd?: string;
  status: string;
}

export interface HoldMetric {
  holdId: number;
  holdNo: string;
  totalWeight: number;
  centroidX: number;
  centroidY: number;
  centroidZ: number;
  utilization: number;
  unitWeightPerVolume: number;
  totalVolume: number;
}

export interface StowageItem {
  id?: number;
  planId: number;
  cargoId: number;
  holdId: number;
  layerNo: number;
  orientation: string;
  originX: number;
  originY: number;
  originZ: number;
  placedLength: number;
  placedWidth: number;
  placedHeight: number;
  centroidX: number;
  centroidY: number;
  centroidZ: number;
  status: string;
  violationFlags: string[];
}

export interface WarningRecord {
  id?: number;
  planId: number;
  cargoId?: number | null;
  holdId?: number | null;
  warningType: string;
  warningMessage: string;
  severity: string;
  resolved: boolean;
}

export interface Plan {
  id?: number;
  voyageId: number;
  planNo: string;
  version?: number;
  status?: string;
  totalCargoWeight?: number;
  displacement?: number;
  kg?: number;
  lcg?: number;
  tcg?: number;
  gm?: number;
  complianceStatus?: string;
  warningCount?: number;
  remark?: string;
  holdSummaries?: HoldMetric[];
  adjacentHoldDiffs?: number[];
}

export interface PlanDetail {
  plan: Plan;
  items: StowageItem[];
  warnings: WarningRecord[];
}

export interface SolverConfig {
  gmMin: number;
  adjacentHoldDiffMax: number;
  ixMax: number;
  solverTimeLimitSeconds: number;
  fsc: number;
  defaultIsolationDistance: number;
  maxIterations: number;
}

export interface GeneratePlanCommand {
  cargoIds: number[];
  config: SolverConfig;
}

export interface ValidatePlanCommand {
  config: SolverConfig;
}
