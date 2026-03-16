from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ShipData:
    """Ship parameters used by the solver."""

    id: int
    ship_code: str
    ship_name: str
    ship_type: str
    length_overall: float
    length_between_perpendiculars: float
    beam: float
    depth: float
    lightship_weight: float
    lightship_kg: float
    lightship_lcg: float
    lightship_tcg: float = 0.0
    design_displacement: float = 0.0
    design_gm: float = 0.0
    remark: str | None = None


@dataclass(slots=True)
class HoldData:
    """Hold parameters used by the solver."""

    id: int
    ship_id: int
    hold_no: str
    length: float
    width: float
    height: float
    volume: float
    lcg: float
    tcg: float
    vcg: float
    max_load_weight: float
    deck_strength_limit: float
    sequence_no: int
    remark: str | None = None


@dataclass(slots=True)
class CargoData:
    """Cargo parameters used by the solver."""

    id: int
    cargo_code: str
    cargo_name: str
    cargo_category: str
    dangerous_class: str | None
    incompatible_tags: list[str]
    isolation_level: float
    weight: float
    length: float
    width: float
    height: float
    stackable: bool
    rotatable: bool
    center_offset_x: float = 0.0
    center_offset_y: float = 0.0
    center_offset_z: float = 0.0
    remark: str | None = None
    candidate_holds: list[int] = field(default_factory=list)
    segregation_code: int | None = None


@dataclass(slots=True)
class HydrostaticPoint:
    """Static hydrostatic input row."""

    displacement: float
    km_value: float
    draft: float
    note: str | None = None


@dataclass(slots=True)
class PlacedCargo:
    """Placed cargo result."""

    cargo_id: int
    cargo_code: str
    cargo_name: str
    hold_id: int
    hold_no: str
    layer_no: int
    orientation: str
    origin_x: float
    origin_y: float
    origin_z: float
    placed_length: float
    placed_width: float
    placed_height: float
    centroid_x: float
    centroid_y: float
    centroid_z: float
    weight: float
    cargo_category: str
    dangerous_class: str | None
    status: str = "PLACED"
    violation_flags: list[str] = field(default_factory=list)

    @property
    def volume(self) -> float:
        """Return placed cargo volume."""
        return self.placed_length * self.placed_width * self.placed_height


@dataclass(slots=True)
class WarningData:
    """Validation warning."""

    plan_id: int | None
    cargo_id: int | None
    hold_id: int | None
    warning_type: str
    warning_message: str
    severity: str
    resolved: bool = False


@dataclass(slots=True)
class HoldCentroidResult:
    """Aggregated hold centroid metrics."""

    hold_id: int
    hold_no: str
    total_weight: float
    centroid_x: float
    centroid_y: float
    centroid_z: float
    utilization: float
    unit_weight_per_volume: float
    total_volume: float


@dataclass(slots=True)
class PlanSummary:
    """Top-level plan summary."""

    displacement: float
    kg: float
    lcg: float
    tcg: float
    gm: float
    delta_gm: float
    ix: float
    compliance_status: str
    longitudinal_moment: float
    transverse_moment: float
    vertical_moment: float
    hold_summaries: list[HoldCentroidResult]
    adjacent_hold_diffs: list[float]


@dataclass(slots=True)
class SolverMetrics:
    """Execution metrics."""

    solve_time_ms: int
    iteration_count: int
    solver_status: str
    logs: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PlanResult:
    """Complete plan result."""

    success: bool
    plan_summary: PlanSummary
    items: list[PlacedCargo]
    warnings: list[WarningData]
    metrics: SolverMetrics
    reason_list: list[str] = field(default_factory=list)


def dataclass_to_dict(value: Any) -> Any:
    """Convert nested dataclasses to dictionaries."""
    if isinstance(value, list):
        return [dataclass_to_dict(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        result: dict[str, Any] = {}
        for key in value.__dataclass_fields__.keys():
            result[key] = dataclass_to_dict(getattr(value, key))
        return result
    return value
