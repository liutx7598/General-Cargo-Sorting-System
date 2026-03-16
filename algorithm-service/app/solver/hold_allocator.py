from __future__ import annotations

from collections import defaultdict

from ortools.sat.python import cp_model

from app.models.domain import CargoData, HoldData, ShipData
from app.solver.geometry import ORIENTATION_MAP, rotate_dimensions
from app.solver.rule_checker import are_cargos_incompatible


ASSIGNMENT_SCALE = 100
OPEN_HOLD_OBJECTIVE_WEIGHT = 1_000_000
USED_HOLD_PRIORITY_WEIGHT = 20_000
LATE_HOLD_ASSIGNMENT_WEIGHT = 2_000
MIDSHIP_DISTANCE_WEIGHT = 1
GREEDY_BIAS_WEIGHT = 500
UTILIZATION_SPREAD_WEIGHT = 25

GREEDY_NEW_HOLD_PENALTY = 10_000
GREEDY_HOLD_PRIORITY_WEIGHT = 250
GREEDY_RESIDUAL_VOLUME_WEIGHT = 120
GREEDY_RESIDUAL_WEIGHT_WEIGHT = 90
GREEDY_CATEGORY_MIX_PENALTY = 180
GREEDY_DANGEROUS_MIX_PENALTY = 360


def cargo_fits_hold(cargo: CargoData, hold: HoldData) -> bool:
    """Check whether at least one valid orientation fits inside the hold."""
    orientations = ["LWH"] if not cargo.rotatable else list(ORIENTATION_MAP.keys())
    for orientation in orientations:
        placed_length, placed_width, placed_height = rotate_dimensions(
            cargo.length,
            cargo.width,
            cargo.height,
            orientation,
        )
        if (
            placed_length <= hold.length + 1e-6
            and placed_width <= hold.width + 1e-6
            and placed_height <= hold.height + 1e-6
        ):
            return True
    return False


def estimate_cargo_volume(cargo: CargoData) -> float:
    """Return the axis-aligned cargo volume used during hold assignment."""
    return cargo.length * cargo.width * cargo.height


def estimate_min_footprint(cargo: CargoData, hold: HoldData) -> float:
    """Estimate the smallest floor footprint for a cargo inside the target hold."""
    orientations = ["LWH"] if not cargo.rotatable else list(ORIENTATION_MAP.keys())
    footprints: list[float] = []
    for orientation in orientations:
        placed_length, placed_width, placed_height = rotate_dimensions(
            cargo.length,
            cargo.width,
            cargo.height,
            orientation,
        )
        if (
            placed_length <= hold.length + 1e-6
            and placed_width <= hold.width + 1e-6
            and placed_height <= hold.height + 1e-6
        ):
            footprints.append(placed_length * placed_width)
    return min(footprints) if footprints else cargo.length * cargo.width


def build_hold_priority(ship: ShipData, holds: list[HoldData]) -> list[int]:
    """Rank holds for breakbulk loading: minimize open holds and stay close to midship."""
    ship_midship = ship.length_overall / 2.0
    ranked = sorted(
        holds,
        key=lambda hold: (
            abs(hold.lcg - ship_midship),
            hold.sequence_no,
            -hold.volume,
        ),
    )
    return [hold.id for hold in ranked]


def build_hold_priority_map(ship: ShipData, holds: list[HoldData]) -> dict[int, int]:
    """Return a 0-based hold priority map."""
    return {hold_id: index for index, hold_id in enumerate(build_hold_priority(ship, holds))}


def static_filter_candidates(cargos: list[CargoData], holds: list[HoldData]) -> dict[int, list[int]]:
    """Stage A: filter candidate holds by geometry and max load constraints."""
    candidate_map: dict[int, list[int]] = {}
    for cargo in cargos:
        candidate_map[cargo.id] = [
            hold.id
            for hold in holds
            if cargo.weight <= hold.max_load_weight and cargo_fits_hold(cargo, hold)
        ]
        cargo.candidate_holds = candidate_map[cargo.id]
    return candidate_map


def _score_greedy_hold(
    cargo: CargoData,
    hold_id: int,
    holds_by_id: dict[int, HoldData],
    hold_priority: dict[int, int],
    loaded_weight: dict[int, float],
    loaded_volume: dict[int, float],
    loaded_categories: dict[int, set[str]],
    loaded_dangerous: dict[int, set[str]],
    cargo_volume: float,
    is_new_hold: bool,
) -> tuple[int, int, int, int, int]:
    """Score a hold for the greedy seed, preferring already-open compact blocks."""
    hold = holds_by_id[hold_id]
    projected_volume_ratio = (loaded_volume[hold_id] + cargo_volume) / max(hold.volume, 1.0)
    projected_weight_ratio = (loaded_weight[hold_id] + cargo.weight) / max(hold.max_load_weight, 1.0)
    category_penalty = 0
    if loaded_categories[hold_id] and cargo.cargo_category not in loaded_categories[hold_id]:
        category_penalty += GREEDY_CATEGORY_MIX_PENALTY
    if cargo.dangerous_class and loaded_dangerous[hold_id] and cargo.dangerous_class not in loaded_dangerous[hold_id]:
        category_penalty += GREEDY_DANGEROUS_MIX_PENALTY

    residual_volume_penalty = int(round(max(0.0, 1.0 - projected_volume_ratio) * GREEDY_RESIDUAL_VOLUME_WEIGHT))
    residual_weight_penalty = int(round(max(0.0, 1.0 - projected_weight_ratio) * GREEDY_RESIDUAL_WEIGHT_WEIGHT))
    open_hold_penalty = GREEDY_NEW_HOLD_PENALTY if is_new_hold else 0
    hold_priority_penalty = hold_priority[hold_id] * GREEDY_HOLD_PRIORITY_WEIGHT
    return (
        open_hold_penalty,
        hold_priority_penalty,
        category_penalty,
        residual_volume_penalty,
        residual_weight_penalty,
    )


def build_greedy_consolidated_assignment(
    ship: ShipData,
    cargos: list[CargoData],
    holds: list[HoldData],
    candidate_map: dict[int, list[int]],
) -> dict[int, int]:
    """Build a greedy seed that fills already-open holds before opening new ones."""
    holds_by_id = {hold.id: hold for hold in holds}
    hold_priority = build_hold_priority_map(ship, holds)
    loaded_weight: dict[int, float] = defaultdict(float)
    loaded_volume: dict[int, float] = defaultdict(float)
    loaded_categories: dict[int, set[str]] = defaultdict(set)
    loaded_dangerous: dict[int, set[str]] = defaultdict(set)
    assignment: dict[int, int] = {}
    opened_holds: set[int] = set()

    def cargo_sort_key(cargo: CargoData) -> tuple[bool, float, float, float]:
        best_priority_hold = min(candidate_map[cargo.id], key=lambda hold_id: hold_priority[hold_id])
        footprint = estimate_min_footprint(cargo, holds_by_id[best_priority_hold])
        return (not cargo.stackable, footprint, cargo.weight, estimate_cargo_volume(cargo))

    for cargo in sorted(cargos, key=cargo_sort_key, reverse=True):
        cargo_volume = estimate_cargo_volume(cargo)
        feasible_holds = [
            hold_id
            for hold_id in candidate_map[cargo.id]
            if loaded_weight[hold_id] + cargo.weight <= holds_by_id[hold_id].max_load_weight + 1e-6
            and loaded_volume[hold_id] + cargo_volume <= holds_by_id[hold_id].volume + 1e-6
        ]
        if not feasible_holds:
            feasible_holds = list(candidate_map[cargo.id])

        open_candidates = [hold_id for hold_id in feasible_holds if hold_id in opened_holds]
        if open_candidates:
            best_hold_id = min(
                open_candidates,
                key=lambda hold_id: _score_greedy_hold(
                    cargo,
                    hold_id,
                    holds_by_id,
                    hold_priority,
                    loaded_weight,
                    loaded_volume,
                    loaded_categories,
                    loaded_dangerous,
                    cargo_volume,
                    is_new_hold=False,
                ),
            )
        else:
            best_hold_id = min(
                feasible_holds,
                key=lambda hold_id: _score_greedy_hold(
                    cargo,
                    hold_id,
                    holds_by_id,
                    hold_priority,
                    loaded_weight,
                    loaded_volume,
                    loaded_categories,
                    loaded_dangerous,
                    cargo_volume,
                    is_new_hold=True,
                ),
            )
            opened_holds.add(best_hold_id)

        assignment[cargo.id] = best_hold_id
        loaded_weight[best_hold_id] += cargo.weight
        loaded_volume[best_hold_id] += cargo_volume
        loaded_categories[best_hold_id].add(cargo.cargo_category)
        if cargo.dangerous_class:
            loaded_dangerous[best_hold_id].add(cargo.dangerous_class)

    return assignment


def allocate_holds(
    ship: ShipData,
    cargos: list[CargoData],
    holds: list[HoldData],
    solver_time_limit_seconds: int,
) -> tuple[dict[int, int], str, dict[int, list[int]]]:
    """Stage B: allocate cargoes to holds with compact breakbulk-focused assignment."""
    holds_by_id = {hold.id: hold for hold in holds}
    candidate_map = static_filter_candidates(cargos, holds)
    if any(not candidates for candidates in candidate_map.values()):
        return {}, "INFEASIBLE", candidate_map

    ship_midship = ship.length_overall / 2.0
    hold_priority = build_hold_priority_map(ship, holds)
    greedy_assignment = build_greedy_consolidated_assignment(ship, cargos, holds, candidate_map)

    model = cp_model.CpModel()
    variable_map: dict[tuple[int, int], cp_model.IntVar] = {}
    used_hold_map: dict[int, cp_model.IntVar] = {}
    total_volume = sum(hold.volume for hold in holds)
    total_cargo_volume = sum(estimate_cargo_volume(cargo) for cargo in cargos)
    average_utilization = (total_cargo_volume / total_volume) if total_volume > 0 else 0.0
    target_midship = int(round(ship_midship * ASSIGNMENT_SCALE))

    for hold in holds:
        used_hold_map[hold.id] = model.NewBoolVar(f"used_hold_{hold.id}")

    for cargo in cargos:
        for hold_id in candidate_map[cargo.id]:
            variable_map[(cargo.id, hold_id)] = model.NewBoolVar(f"cargo_{cargo.id}_hold_{hold_id}")
            model.Add(variable_map[(cargo.id, hold_id)] <= used_hold_map[hold_id])
        model.Add(sum(variable_map[(cargo.id, hold_id)] for hold_id in candidate_map[cargo.id]) == 1)

    for hold in holds:
        hold_weight_terms = []
        hold_volume_terms = []
        hold_assignments = []
        for cargo in cargos:
            if (cargo.id, hold.id) not in variable_map:
                continue
            hold_assignments.append(variable_map[(cargo.id, hold.id)])
            hold_weight_terms.append(int(round(cargo.weight * ASSIGNMENT_SCALE)) * variable_map[(cargo.id, hold.id)])
            hold_volume_terms.append(int(round(estimate_cargo_volume(cargo) * ASSIGNMENT_SCALE)) * variable_map[(cargo.id, hold.id)])

        if hold_assignments:
            model.Add(sum(hold_assignments) >= used_hold_map[hold.id])
        model.Add(sum(hold_weight_terms) <= int(round(hold.max_load_weight * ASSIGNMENT_SCALE)))
        model.Add(sum(hold_volume_terms) <= int(round(hold.volume * ASSIGNMENT_SCALE)))

    for index, cargo in enumerate(cargos):
        for other in cargos[index + 1 :]:
            if not are_cargos_incompatible(cargo, other):
                continue
            common_holds = set(candidate_map[cargo.id]) & set(candidate_map[other.id])
            for hold_id in common_holds:
                model.Add(variable_map[(cargo.id, hold_id)] + variable_map[(other.id, hold_id)] <= 1)

    objective_terms = []
    for hold in holds:
        volume_expr = sum(
            int(round(estimate_cargo_volume(cargo) * ASSIGNMENT_SCALE)) * variable_map[(cargo.id, hold.id)]
            for cargo in cargos
            if (cargo.id, hold.id) in variable_map
        )
        utilization_target = int(round(hold.volume * average_utilization * ASSIGNMENT_SCALE))
        utilization_diff = model.NewIntVar(0, int(round(hold.volume * ASSIGNMENT_SCALE)), f"util_diff_{hold.id}")
        model.Add(utilization_diff >= volume_expr - utilization_target)
        model.Add(utilization_diff >= utilization_target - volume_expr)
        objective_terms.append(utilization_diff * UTILIZATION_SPREAD_WEIGHT)

        open_hold_cost = OPEN_HOLD_OBJECTIVE_WEIGHT + hold_priority[hold.id] * USED_HOLD_PRIORITY_WEIGHT
        objective_terms.append(used_hold_map[hold.id] * open_hold_cost)

    for cargo in cargos:
        for hold_id in candidate_map[cargo.id]:
            hold = holds_by_id[hold_id]
            distance_cost = int(abs(hold.lcg * ASSIGNMENT_SCALE - target_midship))
            greedy_bias = 0 if greedy_assignment[cargo.id] == hold_id else GREEDY_BIAS_WEIGHT
            priority_cost = hold_priority[hold_id] * LATE_HOLD_ASSIGNMENT_WEIGHT
            objective_terms.append(
                variable_map[(cargo.id, hold_id)] * (priority_cost + distance_cost * MIDSHIP_DISTANCE_WEIGHT + greedy_bias)
            )

    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = solver_time_limit_seconds
    solver.parameters.log_search_progress = False
    status = solver.Solve(model)
    status_name = solver.StatusName(status)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return greedy_assignment, status_name, candidate_map

    assignment: dict[int, int] = {}
    for cargo in cargos:
        for hold_id in candidate_map[cargo.id]:
            if solver.BooleanValue(variable_map[(cargo.id, hold_id)]):
                assignment[cargo.id] = hold_id
                break
    return assignment, status_name, candidate_map
