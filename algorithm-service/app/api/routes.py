from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.domain import PlacedCargo, dataclass_to_dict
from app.schemas.solver import (
    CargoCentroidRequest,
    CargoCentroidResponse,
    GeneratePlanRequest,
    GeneratePlanResponse,
    HoldCentroidRequest,
    HoldCentroidResponse,
    RuleCheckRequest,
    ShipStabilityRequest,
    ValidatePlanRequest,
)
from app.services.plan_service import generate_stowage_plan, to_cargo_data, to_hold_data, to_hydrostatic_data, to_ship_data, validate_plan
from app.solver.geometry import calculate_cargo_centroid, rotate_dimensions
from app.solver.rule_checker import check_rule_violations
from app.solver.stability import calculate_gm, calculate_hold_centroid, calculate_ship_centroid


router = APIRouter(prefix="/api/solver", tags=["solver"])


def serialize_plan_result(result) -> dict:
    """Serialize plan result to API response shape."""
    return {
        "success": result.success,
        "planSummary": {
            "displacement": result.plan_summary.displacement,
            "kg": result.plan_summary.kg,
            "lcg": result.plan_summary.lcg,
            "tcg": result.plan_summary.tcg,
            "gm": result.plan_summary.gm,
            "deltaGM": result.plan_summary.delta_gm,
            "ix": result.plan_summary.ix,
            "complianceStatus": result.plan_summary.compliance_status,
            "longitudinalMoment": result.plan_summary.longitudinal_moment,
            "transverseMoment": result.plan_summary.transverse_moment,
            "verticalMoment": result.plan_summary.vertical_moment,
            "holdSummaries": [
                {
                    "holdId": item.hold_id,
                    "holdNo": item.hold_no,
                    "totalWeight": item.total_weight,
                    "centroidX": item.centroid_x,
                    "centroidY": item.centroid_y,
                    "centroidZ": item.centroid_z,
                    "utilization": item.utilization,
                    "unitWeightPerVolume": item.unit_weight_per_volume,
                    "totalVolume": item.total_volume,
                }
                for item in result.plan_summary.hold_summaries
            ],
            "adjacentHoldDiffs": result.plan_summary.adjacent_hold_diffs,
        },
        "items": [
            {
                "cargoId": item.cargo_id,
                "cargoCode": item.cargo_code,
                "cargoName": item.cargo_name,
                "holdId": item.hold_id,
                "holdNo": item.hold_no,
                "layerNo": item.layer_no,
                "orientation": item.orientation,
                "originX": item.origin_x,
                "originY": item.origin_y,
                "originZ": item.origin_z,
                "placedLength": item.placed_length,
                "placedWidth": item.placed_width,
                "placedHeight": item.placed_height,
                "centroidX": item.centroid_x,
                "centroidY": item.centroid_y,
                "centroidZ": item.centroid_z,
                "weight": item.weight,
                "cargoCategory": item.cargo_category,
                "dangerousClass": item.dangerous_class,
                "status": item.status,
                "violationFlags": item.violation_flags,
            }
            for item in result.items
        ],
        "warnings": [
            {
                "planId": warning.plan_id,
                "cargoId": warning.cargo_id,
                "holdId": warning.hold_id,
                "warningType": warning.warning_type,
                "warningMessage": warning.warning_message,
                "severity": warning.severity,
                "resolved": warning.resolved,
            }
            for warning in result.warnings
        ],
        "metrics": {
            "solveTimeMs": result.metrics.solve_time_ms,
            "iterationCount": result.metrics.iteration_count,
            "solverStatus": result.metrics.solver_status,
            "logs": result.metrics.logs,
        },
        "reasonList": result.reason_list,
    }


@router.post("/generate-plan", response_model=GeneratePlanResponse)
def generate_plan(request: GeneratePlanRequest) -> dict:
    """Generate a stowage plan."""
    return serialize_plan_result(generate_stowage_plan(request))


@router.post("/validate-plan", response_model=GeneratePlanResponse)
def validate_existing_plan(request: ValidatePlanRequest) -> dict:
    """Validate an existing plan."""
    return serialize_plan_result(validate_plan(request))


@router.post("/cargo-centroid", response_model=CargoCentroidResponse)
def cargo_centroid(request: CargoCentroidRequest) -> CargoCentroidResponse:
    """Calculate the centroid of one cargo."""
    placed_length, placed_width, placed_height = rotate_dimensions(
        request.length,
        request.width,
        request.height,
        request.orientation,
    )
    centroid_x, centroid_y, centroid_z = calculate_cargo_centroid(
        request.originX,
        request.originY,
        request.originZ,
        placed_length,
        placed_width,
        placed_height,
        request.centerOffsetX,
        request.centerOffsetY,
        request.centerOffsetZ,
    )
    return CargoCentroidResponse(
        placedLength=placed_length,
        placedWidth=placed_width,
        placedHeight=placed_height,
        centroidX=centroid_x,
        centroidY=centroid_y,
        centroidZ=centroid_z,
    )


@router.post("/hold-centroid", response_model=HoldCentroidResponse)
def hold_centroid(request: HoldCentroidRequest) -> HoldCentroidResponse:
    """Calculate hold centroid metrics from weighted item centroids."""
    items = [
        PlacedCargo(
            cargo_id=index,
            cargo_code=f"TEMP-{index}",
            cargo_name=f"TEMP-{index}",
            hold_id=request.holdId,
            hold_no=request.holdNo,
            layer_no=1,
            orientation="LWH",
            origin_x=0.0,
            origin_y=0.0,
            origin_z=0.0,
            placed_length=0.0,
            placed_width=0.0,
            placed_height=0.0,
            centroid_x=item.centroidX,
            centroid_y=item.centroidY,
            centroid_z=item.centroidZ,
            weight=item.weight,
            cargo_category="TEMP",
            dangerous_class=None,
        )
        for index, item in enumerate(request.items, start=1)
    ]
    result = calculate_hold_centroid(request.holdId, request.holdNo, request.holdVolume, items)
    return HoldCentroidResponse(
        holdId=result.hold_id,
        holdNo=result.hold_no,
        totalWeight=result.total_weight,
        centroidX=result.centroid_x,
        centroidY=result.centroid_y,
        centroidZ=result.centroid_z,
        utilization=result.utilization,
        unitWeightPerVolume=result.unit_weight_per_volume,
    )


@router.post("/ship-stability")
def ship_stability(request: ShipStabilityRequest) -> dict[str, float]:
    """Calculate displacement, centroids and GM for a ship."""
    if not request.hydrostaticTable:
        raise HTTPException(status_code=400, detail="hydrostaticTable is required")
    ship = to_ship_data(request.ship)
    hydrostatic = to_hydrostatic_data(request.hydrostaticTable)
    items = [
        PlacedCargo(
            cargo_id=index,
            cargo_code=f"TEMP-{index}",
            cargo_name=f"TEMP-{index}",
            hold_id=0,
            hold_no="TEMP",
            layer_no=1,
            orientation="LWH",
            origin_x=0.0,
            origin_y=0.0,
            origin_z=0.0,
            placed_length=0.0,
            placed_width=0.0,
            placed_height=0.0,
            centroid_x=item.centroidX,
            centroid_y=item.centroidY,
            centroid_z=item.centroidZ,
            weight=item.weight,
            cargo_category="TEMP",
            dangerous_class=None,
        )
        for index, item in enumerate(request.items, start=1)
    ]
    metrics = calculate_ship_centroid(ship, items)
    km_value, gm_value = calculate_gm(metrics["displacement"], metrics["kg"], hydrostatic, fsc=request.fsc)
    reference_gm = request.referenceGM if request.referenceGM is not None else ship.design_gm
    return {**metrics, "km": km_value, "gm": gm_value, "deltaGM": gm_value - reference_gm}


@router.post("/rule-check")
def rule_check(request: RuleCheckRequest) -> dict[str, list[dict]]:
    """Validate rule compliance for a plan."""
    holds = to_hold_data(request.holds)
    cargos = to_cargo_data(request.cargoList)
    hold_map = {hold.id: hold for hold in holds}
    cargo_map = {cargo.id: cargo for cargo in cargos}
    items = [
        PlacedCargo(
            cargo_id=item.cargoId,
            cargo_code=cargo_map[item.cargoId].cargo_code,
            cargo_name=cargo_map[item.cargoId].cargo_name,
            hold_id=item.holdId,
            hold_no=hold_map[item.holdId].hold_no,
            layer_no=item.layerNo,
            orientation=item.orientation,
            origin_x=item.originX,
            origin_y=item.originY,
            origin_z=item.originZ,
            placed_length=item.placedLength,
            placed_width=item.placedWidth,
            placed_height=item.placedHeight,
            centroid_x=item.centroidX,
            centroid_y=item.centroidY,
            centroid_z=item.centroidZ,
            weight=cargo_map[item.cargoId].weight,
            cargo_category=cargo_map[item.cargoId].cargo_category,
            dangerous_class=cargo_map[item.cargoId].dangerous_class,
            status=item.status,
            violation_flags=list(item.violationFlags),
        )
        for item in request.items
    ]
    warnings = check_rule_violations(hold_map, cargo_map, items, request.config.defaultIsolationDistance)
    return {"warnings": [dataclass_to_dict(warning) for warning in warnings]}
