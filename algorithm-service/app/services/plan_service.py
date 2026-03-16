from __future__ import annotations

from collections import defaultdict
from time import perf_counter

from app.models.domain import CargoData, HoldData, HydrostaticPoint, PlanResult, PlanSummary, PlacedCargo, ShipData, SolverMetrics, WarningData
from app.schemas.solver import GeneratePlanRequest, ValidatePlanRequest
from app.services.sample_data_service import load_sample_context
from app.solver.evaluator import build_empty_summary, evaluate_compliance
from app.solver.hold_allocator import allocate_holds
from app.solver.optimizer import pack_assignment, repair_assignment
from app.solver.rule_checker import check_rule_violations
from app.solver.stability import (
    calculate_gm,
    calculate_hold_centroid,
    calculate_longitudinal_index_in_ship_coordinates,
    calculate_ship_centroid,
)
from app.utils.logging import get_logger


logger = get_logger(__name__)


def to_ship_data(request_ship) -> ShipData:
    """Map request ship schema to internal model."""
    return ShipData(
        id=request_ship.id,
        ship_code=request_ship.shipCode,
        ship_name=request_ship.shipName,
        ship_type=request_ship.shipType,
        length_overall=request_ship.lengthOverall,
        length_between_perpendiculars=request_ship.lengthBetweenPerpendiculars,
        beam=request_ship.beam,
        depth=request_ship.depth,
        lightship_weight=request_ship.lightshipWeight,
        lightship_kg=request_ship.lightshipKG,
        lightship_lcg=request_ship.lightshipLCG,
        lightship_tcg=request_ship.lightshipTCG,
        design_displacement=request_ship.designDisplacement,
        design_gm=request_ship.designGM,
        remark=request_ship.remark,
    )


def to_hold_data(request_holds) -> list[HoldData]:
    """Map request hold schemas to internal models."""
    return [
        HoldData(
            id=hold.id,
            ship_id=hold.shipId,
            hold_no=hold.holdNo,
            length=hold.length,
            width=hold.width,
            height=hold.height,
            volume=hold.volume,
            lcg=hold.lcg,
            tcg=hold.tcg,
            vcg=hold.vcg,
            max_load_weight=hold.maxLoadWeight,
            deck_strength_limit=hold.deckStrengthLimit,
            sequence_no=hold.sequenceNo,
            remark=hold.remark,
        )
        for hold in request_holds
    ]


def to_cargo_data(request_cargos) -> list[CargoData]:
    """Map request cargo schemas to internal models."""
    return [
        CargoData(
            id=cargo.cargoId,
            cargo_code=cargo.cargoCode,
            cargo_name=cargo.cargoName,
            cargo_category=cargo.cargoCategory,
            dangerous_class=cargo.dangerousClass,
            incompatible_tags=cargo.incompatibleTags,
            isolation_level=cargo.isolationLevel,
            weight=cargo.weight,
            length=cargo.length,
            width=cargo.width,
            height=cargo.height,
            stackable=cargo.stackable,
            rotatable=cargo.rotatable,
            center_offset_x=cargo.centerOffsetX,
            center_offset_y=cargo.centerOffsetY,
            center_offset_z=cargo.centerOffsetZ,
            remark=cargo.remark,
            segregation_code=cargo.segregationCode,
        )
        for cargo in request_cargos
    ]


def to_hydrostatic_data(request_hydrostatic) -> list[HydrostaticPoint]:
    """Map hydrostatic rows."""
    return [
        HydrostaticPoint(item.displacement, item.kmValue, item.draft, item.note)
        for item in request_hydrostatic
    ]


def ensure_context(ship_id: int, ship_input, holds_input, hydrostatic_input) -> tuple[ShipData, list[HoldData], list[HydrostaticPoint]]:
    """Use request context or fall back to bundled sample data."""
    if ship_input and holds_input and hydrostatic_input:
        return to_ship_data(ship_input), to_hold_data(holds_input), to_hydrostatic_data(hydrostatic_input)
    return load_sample_context(ship_id)


def summarize(
    ship: ShipData,
    holds: list[HoldData],
    hydrostatic_table: list[HydrostaticPoint],
    items: list[PlacedCargo],
    warnings: list[WarningData],
    gm_min: float,
    adjacent_hold_diff_max: float,
    ix_max: float,
    fsc: float,
) -> tuple[PlanSummary, list[str]]:
    """Build plan summary and final compliance reasons."""
    hold_item_map: dict[int, list[PlacedCargo]] = defaultdict(list)
    for item in items:
        hold_item_map[item.hold_id].append(item)
    holds_by_id = {hold.id: hold for hold in holds}

    hold_summaries = [
        calculate_hold_centroid(hold.id, hold.hold_no, hold.volume, hold_item_map.get(hold.id, []))
        for hold in sorted(holds, key=lambda current: current.sequence_no)
    ]
    adjacent_diffs = [
        abs(current.utilization - next_item.utilization)
        for current, next_item in zip(hold_summaries, hold_summaries[1:])
    ]
    ship_metrics = calculate_ship_centroid(ship, items, holds_by_id=holds_by_id)
    _, gm = calculate_gm(ship_metrics["displacement"], ship_metrics["kg"], hydrostatic_table, fsc=fsc)
    ix = calculate_longitudinal_index_in_ship_coordinates(items, ship_metrics["lcg"], holds_by_id=holds_by_id)
    compliance_status, reasons = evaluate_compliance(
        warnings=warnings,
        hold_summaries=hold_summaries,
        adjacent_hold_diffs=adjacent_diffs,
        gm=gm,
        gm_min=gm_min,
        ix=ix,
        ix_max=ix_max,
        adjacent_hold_diff_max=adjacent_hold_diff_max,
    )
    return (
        PlanSummary(
            displacement=ship_metrics["displacement"],
            kg=ship_metrics["kg"],
            lcg=ship_metrics["lcg"],
            tcg=ship_metrics["tcg"],
            gm=gm,
            delta_gm=gm - ship.design_gm,
            ix=ix,
            compliance_status=compliance_status,
            longitudinal_moment=ship_metrics["longitudinal_moment"],
            transverse_moment=ship_metrics["transverse_moment"],
            vertical_moment=ship_metrics["vertical_moment"],
            hold_summaries=hold_summaries,
            adjacent_hold_diffs=adjacent_diffs,
        ),
        reasons,
    )


def generate_stowage_plan(request: GeneratePlanRequest) -> PlanResult:
    """Generate a stowage plan using staged allocation, packing and evaluation."""
    started_at = perf_counter()
    ship, holds, hydrostatic_table = ensure_context(request.shipId, request.ship, request.holds, request.hydrostaticTable)
    cargos = to_cargo_data(request.cargoList)
    config = request.config
    logs = ["Phase A: filtering candidate holds", "Phase B: assignment with greedy seed + CP-SAT"]

    assignment, solver_status, candidate_map = allocate_holds(
        ship,
        cargos,
        holds,
        config.solverTimeLimitSeconds,
        config.defaultIsolationDistance,
    )
    if not assignment:
        return PlanResult(
            success=False,
            plan_summary=build_empty_summary(),
            items=[],
            warnings=[WarningData(None, None, None, "INFEASIBLE", "No feasible hold assignment for at least one cargo", "ERROR")],
            metrics=SolverMetrics(int((perf_counter() - started_at) * 1000), 1, solver_status, logs),
            reason_list=["至少有一件货物找不到可行货舱"],
        )

    logs.append("Phase C: heuristic hold packing")
    placements, unplaced = pack_assignment(holds, cargos, assignment, config.defaultIsolationDistance)
    iteration_count = 1
    while unplaced and iteration_count < config.maxIterations:
        logs.append(f"Phase D: repair iteration {iteration_count}")
        assignment, repair_status = repair_assignment(ship, holds, cargos, assignment, unplaced, config.solverTimeLimitSeconds)
        if repair_status != "REPAIRED":
            solver_status = repair_status
        placements, unplaced = pack_assignment(holds, cargos, assignment, config.defaultIsolationDistance)
        iteration_count += 1

    holds_by_id = {hold.id: hold for hold in holds}
    cargos_by_id = {cargo.id: cargo for cargo in cargos}
    warnings = check_rule_violations(holds_by_id, cargos_by_id, placements, config.defaultIsolationDistance)
    for cargo in unplaced:
        warnings.append(
            WarningData(
                plan_id=None,
                cargo_id=cargo.id,
                hold_id=assignment.get(cargo.id),
                warning_type="UNPLACED",
                warning_message=f"Cargo {cargo.cargo_code} could not be packed in assigned hold",
                severity="ERROR",
            )
        )

    plan_summary, reasons = summarize(
        ship=ship,
        holds=holds,
        hydrostatic_table=hydrostatic_table,
        items=placements,
        warnings=warnings,
        gm_min=config.gmMin,
        adjacent_hold_diff_max=config.adjacentHoldDiffMax,
        ix_max=config.ixMax,
        fsc=config.fsc,
    )
    elapsed_ms = int((perf_counter() - started_at) * 1000)
    logs.append(
        "Candidate holds: " + ", ".join(f"{cargo_id}->{candidates}" for cargo_id, candidates in sorted(candidate_map.items()))
    )
    logger.info(
        "Generated plan voyage=%s success=%s status=%s solve_time_ms=%s",
        request.voyageId,
        plan_summary.compliance_status == "PASS",
        solver_status,
        elapsed_ms,
    )
    return PlanResult(
        success=plan_summary.compliance_status == "PASS",
        plan_summary=plan_summary,
        items=placements,
        warnings=warnings,
        metrics=SolverMetrics(elapsed_ms, iteration_count, solver_status, logs),
        reason_list=reasons,
    )


def validate_plan(request: ValidatePlanRequest) -> PlanResult:
    """Recalculate metrics and rule results for an existing placement."""
    started_at = perf_counter()
    ship, holds, hydrostatic_table = ensure_context(request.shipId, request.ship, request.holds, request.hydrostaticTable)
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
    plan_summary, reasons = summarize(
        ship=ship,
        holds=holds,
        hydrostatic_table=hydrostatic_table,
        items=items,
        warnings=warnings,
        gm_min=request.config.gmMin,
        adjacent_hold_diff_max=request.config.adjacentHoldDiffMax,
        ix_max=request.config.ixMax,
        fsc=request.config.fsc,
    )
    elapsed_ms = int((perf_counter() - started_at) * 1000)
    return PlanResult(
        success=plan_summary.compliance_status == "PASS",
        plan_summary=plan_summary,
        items=items,
        warnings=warnings,
        metrics=SolverMetrics(elapsed_ms, 1, "VALIDATED", ["Validate existing plan"]),
        reason_list=reasons,
    )
