from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from app.models.domain import CargoData, HoldData, PlacedCargo, WarningData
from app.solver.geometry import calculate_distance_between_boxes, check_bounds, check_overlap


def are_cargos_incompatible(cargo_a: CargoData, cargo_b: CargoData) -> bool:
    """Check whether two cargoes share incompatible tags."""
    if not cargo_a.incompatible_tags or not cargo_b.incompatible_tags:
        return False
    return bool(set(cargo_a.incompatible_tags) & set(cargo_b.incompatible_tags))


def get_required_isolation_distance(cargo_a: CargoData, cargo_b: CargoData, default_distance: float) -> float:
    """Determine the minimum required isolation distance for a cargo pair."""
    if are_cargos_incompatible(cargo_a, cargo_b):
        return max(cargo_a.isolation_level, cargo_b.isolation_level, default_distance)

    # In breakbulk stowage, isolation is pair-specific rather than global.
    # A standalone isolation level should not force separation from every cargo.
    # Only dangerous cargo pairings without explicit incompatible tags keep a minimum clearance.
    if cargo_a.dangerous_class and cargo_b.dangerous_class:
        return max(cargo_a.isolation_level, cargo_b.isolation_level, default_distance)

    return 0.0


def check_rule_violations(
    holds_by_id: dict[int, HoldData],
    cargos_by_id: dict[int, CargoData],
    items: list[PlacedCargo],
    default_isolation_distance: float,
) -> list[WarningData]:
    """Check bounds, overlap, incompatible cargo and isolation violations."""
    warnings: list[WarningData] = []
    items_by_hold: dict[int, list[PlacedCargo]] = defaultdict(list)
    for item in items:
        items_by_hold[item.hold_id].append(item)

    for hold_id, hold_items in items_by_hold.items():
        hold = holds_by_id[hold_id]
        for item in hold_items:
            is_inside = check_bounds(
                item.origin_x,
                item.origin_y,
                item.origin_z,
                item.placed_length,
                item.placed_width,
                item.placed_height,
                hold.length,
                hold.width,
                hold.height,
            )
            if not is_inside:
                item.violation_flags.append("BOUNDARY")
                warnings.append(
                    WarningData(
                        plan_id=None,
                        cargo_id=item.cargo_id,
                        hold_id=item.hold_id,
                        warning_type="BOUNDARY",
                        warning_message=f"Cargo {item.cargo_code} exceeds hold {hold.hold_no} boundary",
                        severity="ERROR",
                    )
                )

        for left, right in combinations(hold_items, 2):
            overlap = check_overlap(
                (left.origin_x, left.origin_y, left.origin_z),
                (left.placed_length, left.placed_width, left.placed_height),
                (right.origin_x, right.origin_y, right.origin_z),
                (right.placed_length, right.placed_width, right.placed_height),
            )
            if overlap:
                left.violation_flags.append("OVERLAP")
                right.violation_flags.append("OVERLAP")
                warnings.append(
                    WarningData(
                        plan_id=None,
                        cargo_id=left.cargo_id,
                        hold_id=hold_id,
                        warning_type="OVERLAP",
                        warning_message=f"Cargo {left.cargo_code} overlaps cargo {right.cargo_code} in hold {hold.hold_no}",
                        severity="ERROR",
                    )
                )

            cargo_a = cargos_by_id[left.cargo_id]
            cargo_b = cargos_by_id[right.cargo_id]
            required_distance = get_required_isolation_distance(cargo_a, cargo_b, default_isolation_distance)
            if required_distance <= 0:
                continue

            actual_distance = calculate_distance_between_boxes(
                (left.origin_x, left.origin_y, left.origin_z),
                (left.placed_length, left.placed_width, left.placed_height),
                (right.origin_x, right.origin_y, right.origin_z),
                (right.placed_length, right.placed_width, right.placed_height),
            )

            if are_cargos_incompatible(cargo_a, cargo_b):
                left.violation_flags.append("INCOMPATIBLE")
                right.violation_flags.append("INCOMPATIBLE")
                warnings.append(
                    WarningData(
                        plan_id=None,
                        cargo_id=left.cargo_id,
                        hold_id=hold_id,
                        warning_type="INCOMPATIBLE",
                        warning_message=f"Cargo {left.cargo_code} is incompatible with cargo {right.cargo_code}",
                        severity="ERROR",
                    )
                )

            if actual_distance + 1e-6 < required_distance:
                left.violation_flags.append("ISOLATION")
                right.violation_flags.append("ISOLATION")
                warnings.append(
                    WarningData(
                        plan_id=None,
                        cargo_id=left.cargo_id,
                        hold_id=hold_id,
                        warning_type="ISOLATION",
                        warning_message=(
                            f"Cargo pair {left.cargo_code}/{right.cargo_code} distance "
                            f"{actual_distance:.2f}m below required {required_distance:.2f}m"
                        ),
                        severity="ERROR",
                    )
                )
    return warnings
