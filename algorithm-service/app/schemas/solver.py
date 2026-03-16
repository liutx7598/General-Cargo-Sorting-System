from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Orientation = Literal["LWH", "LHW", "WLH", "WHL", "HLW", "HWL"]


class ShipSchema(BaseModel):
    id: int
    shipCode: str
    shipName: str
    shipType: str
    lengthOverall: float
    lengthBetweenPerpendiculars: float
    beam: float
    depth: float
    lightshipWeight: float
    lightshipKG: float
    lightshipLCG: float
    lightshipTCG: float = 0.0
    designDisplacement: float = 0.0
    designGM: float = 0.0
    remark: str | None = None


class HoldSchema(BaseModel):
    id: int
    shipId: int
    holdNo: str
    length: float
    width: float
    height: float
    volume: float
    lcg: float
    tcg: float
    vcg: float
    maxLoadWeight: float
    deckStrengthLimit: float
    sequenceNo: int
    remark: str | None = None


class CargoSchema(BaseModel):
    cargoId: int
    cargoCode: str
    cargoName: str
    cargoCategory: str
    dangerousClass: str | None = None
    incompatibleTags: list[str] = Field(default_factory=list)
    isolationLevel: float = 0.0
    weight: float
    length: float
    width: float
    height: float
    stackable: bool = True
    rotatable: bool = True
    centerOffsetX: float = 0.0
    centerOffsetY: float = 0.0
    centerOffsetZ: float = 0.0
    remark: str | None = None


class HydrostaticSchema(BaseModel):
    displacement: float
    kmValue: float
    draft: float
    note: str | None = None


class SolverConfigSchema(BaseModel):
    gmMin: float = 0.5
    adjacentHoldDiffMax: float = 0.4
    ixMax: float = 5000.0
    solverTimeLimitSeconds: int = 10
    fsc: float = 0.0
    defaultIsolationDistance: float = 1.0
    maxIterations: int = 3


class GeneratePlanRequest(BaseModel):
    shipId: int
    voyageId: int
    ship: ShipSchema | None = None
    holds: list[HoldSchema] = Field(default_factory=list)
    hydrostaticTable: list[HydrostaticSchema] = Field(default_factory=list)
    cargoList: list[CargoSchema]
    config: SolverConfigSchema = Field(default_factory=SolverConfigSchema)


class ExistingPlacementSchema(BaseModel):
    cargoId: int
    holdId: int
    layerNo: int
    orientation: Orientation
    originX: float
    originY: float
    originZ: float
    placedLength: float
    placedWidth: float
    placedHeight: float
    centroidX: float
    centroidY: float
    centroidZ: float
    status: str = "PLACED"
    violationFlags: list[str] = Field(default_factory=list)


class ValidatePlanRequest(BaseModel):
    shipId: int
    voyageId: int
    ship: ShipSchema | None = None
    holds: list[HoldSchema] = Field(default_factory=list)
    hydrostaticTable: list[HydrostaticSchema] = Field(default_factory=list)
    cargoList: list[CargoSchema]
    items: list[ExistingPlacementSchema]
    config: SolverConfigSchema = Field(default_factory=SolverConfigSchema)


class CargoCentroidRequest(BaseModel):
    length: float
    width: float
    height: float
    orientation: Orientation
    originX: float
    originY: float
    originZ: float
    centerOffsetX: float = 0.0
    centerOffsetY: float = 0.0
    centerOffsetZ: float = 0.0


class CargoCentroidResponse(BaseModel):
    placedLength: float
    placedWidth: float
    placedHeight: float
    centroidX: float
    centroidY: float
    centroidZ: float


class HoldCentroidItemSchema(BaseModel):
    weight: float
    centroidX: float
    centroidY: float
    centroidZ: float


class HoldCentroidRequest(BaseModel):
    holdId: int
    holdNo: str
    holdVolume: float
    items: list[HoldCentroidItemSchema]


class HoldCentroidResponse(BaseModel):
    holdId: int
    holdNo: str
    totalWeight: float
    centroidX: float
    centroidY: float
    centroidZ: float
    utilization: float
    unitWeightPerVolume: float


class ShipStabilityRequest(BaseModel):
    ship: ShipSchema
    hydrostaticTable: list[HydrostaticSchema]
    items: list[HoldCentroidItemSchema]
    referenceGM: float | None = None
    fsc: float = 0.0


class RuleCheckRequest(BaseModel):
    shipId: int
    voyageId: int
    ship: ShipSchema | None = None
    holds: list[HoldSchema]
    cargoList: list[CargoSchema]
    items: list[ExistingPlacementSchema]
    config: SolverConfigSchema = Field(default_factory=SolverConfigSchema)


class SolverItemResponse(BaseModel):
    cargoId: int
    cargoCode: str
    cargoName: str
    holdId: int
    holdNo: str
    layerNo: int
    orientation: Orientation
    originX: float
    originY: float
    originZ: float
    placedLength: float
    placedWidth: float
    placedHeight: float
    centroidX: float
    centroidY: float
    centroidZ: float
    weight: float
    cargoCategory: str
    dangerousClass: str | None
    status: str
    violationFlags: list[str]


class WarningResponse(BaseModel):
    planId: int | None
    cargoId: int | None
    holdId: int | None
    warningType: str
    warningMessage: str
    severity: str
    resolved: bool


class HoldSummaryResponse(BaseModel):
    holdId: int
    holdNo: str
    totalWeight: float
    centroidX: float
    centroidY: float
    centroidZ: float
    utilization: float
    unitWeightPerVolume: float
    totalVolume: float


class PlanSummaryResponse(BaseModel):
    displacement: float
    kg: float
    lcg: float
    tcg: float
    gm: float
    deltaGM: float
    ix: float
    complianceStatus: str
    longitudinalMoment: float
    transverseMoment: float
    verticalMoment: float
    holdSummaries: list[HoldSummaryResponse]
    adjacentHoldDiffs: list[float]


class SolverMetricsResponse(BaseModel):
    solveTimeMs: int
    iterationCount: int
    solverStatus: str
    logs: list[str]


class GeneratePlanResponse(BaseModel):
    success: bool
    planSummary: PlanSummaryResponse
    items: list[SolverItemResponse]
    warnings: list[WarningResponse]
    metrics: SolverMetricsResponse
    reasonList: list[str]

