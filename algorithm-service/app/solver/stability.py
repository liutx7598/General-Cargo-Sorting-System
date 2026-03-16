from __future__ import annotations

from typing import Iterable

from app.models.domain import HoldCentroidResult, HoldData, HydrostaticPoint, PlacedCargo, ShipData


def calculate_hold_centroid(
    hold_id: int,
    hold_no: str,
    hold_volume: float,
    items: Iterable[PlacedCargo],
) -> HoldCentroidResult:
    """Calculate total weight, centroid and utilization for a hold."""
    cargo_items = list(items)
    total_weight = sum(item.weight for item in cargo_items)
    total_volume = sum(item.volume for item in cargo_items)
    if total_weight <= 0:
        return HoldCentroidResult(hold_id, hold_no, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    centroid_x = sum(item.weight * item.centroid_x for item in cargo_items) / total_weight
    centroid_y = sum(item.weight * item.centroid_y for item in cargo_items) / total_weight
    centroid_z = sum(item.weight * item.centroid_z for item in cargo_items) / total_weight
    utilization = total_volume / hold_volume if hold_volume > 0 else 0.0
    unit_weight_per_volume = total_weight / hold_volume if hold_volume > 0 else 0.0
    return HoldCentroidResult(
        hold_id=hold_id,
        hold_no=hold_no,
        total_weight=total_weight,
        centroid_x=centroid_x,
        centroid_y=centroid_y,
        centroid_z=centroid_z,
        utilization=utilization,
        unit_weight_per_volume=unit_weight_per_volume,
        total_volume=total_volume,
    )


def calculate_ship_centroid(
    ship: ShipData,
    items: Iterable[PlacedCargo],
    holds_by_id: dict[int, HoldData] | None = None,
    fuel_weight: float = 0.0,
    ballast_weight: float = 0.0,
    fresh_water_weight: float = 0.0,
    stores_weight: float = 0.0,
    other_long_moment: float = 0.0,
    other_tran_moment: float = 0.0,
    other_vert_moment: float = 0.0,
) -> dict[str, float]:
    """Calculate ship displacement, combined centroid and total moments."""
    cargo_items = list(items)
    cargo_weight = sum(item.weight for item in cargo_items)
    displacement = ship.lightship_weight + cargo_weight + fuel_weight + ballast_weight + fresh_water_weight + stores_weight

    def resolve_ship_coordinates(item: PlacedCargo) -> tuple[float, float, float]:
        if not holds_by_id or item.hold_id not in holds_by_id:
            return item.centroid_x, item.centroid_y, item.centroid_z
        hold = holds_by_id[item.hold_id]
        ship_x = hold.lcg - hold.length / 2.0 + item.centroid_x
        ship_y = hold.tcg - hold.width / 2.0 + item.centroid_y
        ship_z = hold.vcg - hold.height / 2.0 + item.centroid_z
        return ship_x, ship_y, ship_z

    ship_coordinates = {item.cargo_id: resolve_ship_coordinates(item) for item in cargo_items}
    longitudinal_moment = sum(item.weight * ship_coordinates[item.cargo_id][0] for item in cargo_items)
    transverse_moment = sum(item.weight * ship_coordinates[item.cargo_id][1] for item in cargo_items)
    vertical_moment = sum(item.weight * ship_coordinates[item.cargo_id][2] for item in cargo_items)

    if displacement <= 0:
        return {
            "displacement": 0.0,
            "lcg": 0.0,
            "tcg": 0.0,
            "kg": 0.0,
            "longitudinal_moment": 0.0,
            "transverse_moment": 0.0,
            "vertical_moment": 0.0,
        }

    lcg = (ship.lightship_weight * ship.lightship_lcg + longitudinal_moment + other_long_moment) / displacement
    tcg = (ship.lightship_weight * ship.lightship_tcg + transverse_moment + other_tran_moment) / displacement
    kg = (ship.lightship_weight * ship.lightship_kg + vertical_moment + other_vert_moment) / displacement
    return {
        "displacement": displacement,
        "lcg": lcg,
        "tcg": tcg,
        "kg": kg,
        "longitudinal_moment": longitudinal_moment,
        "transverse_moment": transverse_moment,
        "vertical_moment": vertical_moment,
    }


def interpolate_km(displacement: float, hydrostatic_points: Iterable[HydrostaticPoint]) -> float:
    """Interpolate KM against the hydrostatic table using displacement."""
    points = sorted(hydrostatic_points, key=lambda item: item.displacement)
    if not points:
        raise ValueError("Hydrostatic table is empty")
    if displacement <= points[0].displacement:
        return points[0].km_value
    if displacement >= points[-1].displacement:
        return points[-1].km_value

    for lower, upper in zip(points, points[1:]):
        if lower.displacement <= displacement <= upper.displacement:
            ratio = (displacement - lower.displacement) / (upper.displacement - lower.displacement)
            return lower.km_value + ratio * (upper.km_value - lower.km_value)
    return points[-1].km_value


def calculate_gm(
    displacement: float,
    kg: float,
    hydrostatic_points: Iterable[HydrostaticPoint],
    fsc: float = 0.0,
) -> tuple[float, float]:
    """Calculate KM and GM using the hydrostatic table and KG."""
    km_value = interpolate_km(displacement, hydrostatic_points)
    gm_value = km_value - kg - fsc
    return km_value, gm_value


def calculate_hold_utilization(items: Iterable[PlacedCargo], hold_volume: float) -> tuple[float, float]:
    """Calculate volume utilization and unit weight per hold volume."""
    cargo_items = list(items)
    total_volume = sum(item.volume for item in cargo_items)
    total_weight = sum(item.weight for item in cargo_items)
    if hold_volume <= 0:
        return 0.0, 0.0
    return total_volume / hold_volume, total_weight / hold_volume


def calculate_longitudinal_index(items: Iterable[PlacedCargo], x_ref: float) -> float:
    """Calculate the simplified longitudinal concentration index."""
    return sum(item.weight * abs(item.centroid_x - x_ref) for item in items)


def calculate_longitudinal_index_in_ship_coordinates(
    items: Iterable[PlacedCargo],
    x_ref: float,
    holds_by_id: dict[int, HoldData] | None = None,
) -> float:
    """Calculate the simplified longitudinal concentration index in ship coordinates."""
    total = 0.0
    for item in items:
        if holds_by_id and item.hold_id in holds_by_id:
            hold = holds_by_id[item.hold_id]
            ship_x = hold.lcg - hold.length / 2.0 + item.centroid_x
        else:
            ship_x = item.centroid_x
        total += item.weight * abs(ship_x - x_ref)
    return total
