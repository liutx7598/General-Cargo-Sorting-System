from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations

from app.models.domain import CargoData, HoldData, PlacedCargo, WarningData
from app.solver.geometry import calculate_distance_between_boxes, check_bounds, check_overlap


LEVEL_ONE_MIN_DISTANCE = 3.0
LEVEL_THREE_MIN_HOLDS_BETWEEN = 1
LEVEL_FOUR_MIN_HOLDS_BETWEEN = 1
LEVEL_FOUR_MIN_LONGITUDINAL_GAP = 24.0


@dataclass(frozen=True, slots=True)
class SeparationRequirement:
    """Pair-specific cargo segregation requirement."""

    min_distance: float = 0.0
    require_different_hold: bool = False
    min_holds_between: int = 0
    min_longitudinal_gap: float = 0.0
    segregation_code: int | None = None


def are_cargos_incompatible(cargo_a: CargoData, cargo_b: CargoData) -> bool:
    """Check whether two cargoes share incompatible tags."""
    if not cargo_a.incompatible_tags or not cargo_b.incompatible_tags:
        return False
    return bool(set(cargo_a.incompatible_tags) & set(cargo_b.incompatible_tags))


def build_separation_requirement(
    cargo_a: CargoData,
    cargo_b: CargoData,
    default_distance: float,
) -> SeparationRequirement:
    """Build a cargo-pair separation rule using distance and hold-level segregation."""
    segregation_codes = [
        code
        for code in (cargo_a.segregation_code, cargo_b.segregation_code)
        if code is not None and code > 0
    ]
    if segregation_codes:
        segregation_code = max(segregation_codes)
        if segregation_code == 1:
            return SeparationRequirement(
                min_distance=max(
                    LEVEL_ONE_MIN_DISTANCE,
                    cargo_a.isolation_level,
                    cargo_b.isolation_level,
                    default_distance,
                ),
                segregation_code=1,
            )
        if segregation_code == 2:
            return SeparationRequirement(
                require_different_hold=True,
                segregation_code=2,
            )
        if segregation_code == 3:
            return SeparationRequirement(
                require_different_hold=True,
                min_holds_between=LEVEL_THREE_MIN_HOLDS_BETWEEN,
                segregation_code=3,
            )
        if segregation_code >= 4:
            return SeparationRequirement(
                require_different_hold=True,
                min_holds_between=LEVEL_FOUR_MIN_HOLDS_BETWEEN,
                min_longitudinal_gap=LEVEL_FOUR_MIN_LONGITUDINAL_GAP,
                segregation_code=4,
            )

    if are_cargos_incompatible(cargo_a, cargo_b):
        return SeparationRequirement(
            min_distance=max(cargo_a.isolation_level, cargo_b.isolation_level, default_distance),
        )

    if cargo_a.dangerous_class and cargo_b.dangerous_class:
        return SeparationRequirement(
            min_distance=max(cargo_a.isolation_level, cargo_b.isolation_level, default_distance),
        )

    return SeparationRequirement()


def get_required_isolation_distance(cargo_a: CargoData, cargo_b: CargoData, default_distance: float) -> float:
    """Return the minimum same-space distance requirement for two cargoes."""
    return build_separation_requirement(cargo_a, cargo_b, default_distance).min_distance


def _hold_longitudinal_range(hold: HoldData) -> tuple[float, float]:
    """Return the aft/forward ship-coordinate range of a hold."""
    start_x = hold.lcg - hold.length / 2.0
    end_x = hold.lcg + hold.length / 2.0
    return start_x, end_x


def _hold_longitudinal_gap(hold_a: HoldData, hold_b: HoldData) -> float:
    """Return the clear longitudinal gap between two holds."""
    aft_a, fore_a = _hold_longitudinal_range(hold_a)
    aft_b, fore_b = _hold_longitudinal_range(hold_b)
    return max(0.0, aft_b - fore_a, aft_a - fore_b)


def holds_satisfy_separation(
    hold_a: HoldData,
    hold_b: HoldData,
    requirement: SeparationRequirement,
) -> bool:
    """Evaluate whether a pair of holds satisfies the hold-level segregation rule."""
    if hold_a.id == hold_b.id:
        return not (
            requirement.require_different_hold
            or requirement.min_holds_between > 0
            or requirement.min_longitudinal_gap > 0.0
        )

    holds_between = max(0, abs(hold_a.sequence_no - hold_b.sequence_no) - 1)
    if holds_between < requirement.min_holds_between:
        return False

    if requirement.min_longitudinal_gap > 0.0:
        return _hold_longitudinal_gap(hold_a, hold_b) + 1e-6 >= requirement.min_longitudinal_gap

    return True


def _describe_requirement(requirement: SeparationRequirement) -> str:
    """Return a human-readable description for a segregation rule."""
    if requirement.segregation_code == 2:
        return "requires different holds"
    if requirement.segregation_code == 3:
        return "requires at least one whole hold separation"
    if requirement.segregation_code == 4:
        return "requires one hold separation and at least 24.00m longitudinal clearance"
    if requirement.min_distance > 0.0:
        return f"requires at least {requirement.min_distance:.2f}m clearance"
    return "violates separation requirement"


def check_rule_violations(
    holds_by_id: dict[int, HoldData],
    cargos_by_id: dict[int, CargoData],
    items: list[PlacedCargo],
    default_isolation_distance: float,
) -> list[WarningData]:
    """Check bounds, overlap, incompatibility and segregation violations."""
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

    for left, right in combinations(items, 2):
        cargo_a = cargos_by_id[left.cargo_id]
        cargo_b = cargos_by_id[right.cargo_id]
        requirement = build_separation_requirement(cargo_a, cargo_b, default_isolation_distance)
        same_hold = left.hold_id == right.hold_id

        if same_hold and are_cargos_incompatible(cargo_a, cargo_b):
            left.violation_flags.append("INCOMPATIBLE")
            right.violation_flags.append("INCOMPATIBLE")
            warnings.append(
                WarningData(
                    plan_id=None,
                    cargo_id=left.cargo_id,
                    hold_id=left.hold_id,
                    warning_type="INCOMPATIBLE",
                    warning_message=f"Cargo {left.cargo_code} is incompatible with cargo {right.cargo_code}",
                    severity="ERROR",
                )
            )

        if same_hold:
            if (
                requirement.require_different_hold
                or requirement.min_holds_between > 0
                or requirement.min_longitudinal_gap > 0.0
            ):
                left.violation_flags.append("ISOLATION")
                right.violation_flags.append("ISOLATION")
                warnings.append(
                    WarningData(
                        plan_id=None,
                        cargo_id=left.cargo_id,
                        hold_id=left.hold_id,
                        warning_type="ISOLATION",
                        warning_message=(
                            f"Cargo pair {left.cargo_code}/{right.cargo_code} violates segregation "
                            f"level {requirement.segregation_code}: {_describe_requirement(requirement)}"
                        ),
                        severity="ERROR",
                    )
                )
                continue

            if requirement.min_distance <= 0.0:
                continue

            actual_distance = calculate_distance_between_boxes(
                (left.origin_x, left.origin_y, left.origin_z),
                (left.placed_length, left.placed_width, left.placed_height),
                (right.origin_x, right.origin_y, right.origin_z),
                (right.placed_length, right.placed_width, right.placed_height),
            )
            if actual_distance + 1e-6 < requirement.min_distance:
                left.violation_flags.append("ISOLATION")
                right.violation_flags.append("ISOLATION")
                warnings.append(
                    WarningData(
                        plan_id=None,
                        cargo_id=left.cargo_id,
                        hold_id=left.hold_id,
                        warning_type="ISOLATION",
                        warning_message=(
                            f"Cargo pair {left.cargo_code}/{right.cargo_code} distance "
                            f"{actual_distance:.2f}m below required {requirement.min_distance:.2f}m"
                        ),
                        severity="ERROR",
                    )
                )
            continue

        if (
            requirement.require_different_hold
            or requirement.min_holds_between > 0
            or requirement.min_longitudinal_gap > 0.0
        ) and not holds_satisfy_separation(
            holds_by_id[left.hold_id],
            holds_by_id[right.hold_id],
            requirement,
        ):
            left.violation_flags.append("ISOLATION")
            right.violation_flags.append("ISOLATION")
            warnings.append(
                WarningData(
                    plan_id=None,
                    cargo_id=left.cargo_id,
                    hold_id=left.hold_id,
                    warning_type="ISOLATION",
                    warning_message=(
                        f"Cargo pair {left.cargo_code}/{right.cargo_code} violates segregation "
                        f"level {requirement.segregation_code}: {_describe_requirement(requirement)}"
                    ),
                    severity="ERROR",
                )
            )

    return warnings
