from __future__ import annotations

from collections import defaultdict
from copy import deepcopy

from app.models.domain import CargoData, HoldData, PlacedCargo, ShipData
from app.solver.hold_allocator import allocate_holds, build_hold_priority_map
from app.solver.packer import pack_hold_items


def group_cargos_by_hold(cargos: list[CargoData], assignment: dict[int, int]) -> dict[int, list[CargoData]]:
    """Group cargoes according to the current hold assignment."""
    cargo_map = {cargo.id: cargo for cargo in cargos}
    grouped: dict[int, list[CargoData]] = defaultdict(list)
    for cargo_id, hold_id in assignment.items():
        grouped[hold_id].append(cargo_map[cargo_id])
    return grouped


def pack_assignment(
    holds: list[HoldData],
    cargos: list[CargoData],
    assignment: dict[int, int],
    default_isolation_distance: float = 1.0,
) -> tuple[list[PlacedCargo], list[CargoData]]:
    """Pack each hold independently based on the current assignment."""
    grouped = group_cargos_by_hold(cargos, assignment)
    placements: list[PlacedCargo] = []
    unplaced: list[CargoData] = []
    holds_by_id = {hold.id: hold for hold in holds}

    for hold_id, hold_cargos in grouped.items():
        hold_placements, hold_unplaced = pack_hold_items(
            holds_by_id[hold_id],
            hold_cargos,
            default_isolation_distance=default_isolation_distance,
        )
        placements.extend(hold_placements)
        unplaced.extend(hold_unplaced)

    assigned_ids = set(assignment.keys())
    placed_ids = {item.cargo_id for item in placements}
    for cargo in cargos:
        if cargo.id in assigned_ids and cargo.id not in placed_ids and cargo not in unplaced:
            unplaced.append(cargo)
    return placements, unplaced


def repair_assignment(
    ship: ShipData,
    holds: list[HoldData],
    cargos: list[CargoData],
    assignment: dict[int, int],
    unplaced: list[CargoData],
    solver_time_limit_seconds: int,
) -> tuple[dict[int, int], str]:
    """Try to repair a failed packing by moving unplaced cargoes to alternative holds."""
    repaired = deepcopy(assignment)
    hold_priority = build_hold_priority_map(ship, holds)
    for cargo in unplaced:
        alternatives = sorted(
            [hold_id for hold_id in cargo.candidate_holds if hold_id != repaired.get(cargo.id)],
            key=lambda hold_id: hold_priority.get(hold_id, 10_000),
        )
        if alternatives:
            repaired[cargo.id] = alternatives[0]
    if repaired == assignment:
        return assignment, "NO_CHANGE"
    return repaired, "REPAIRED"
