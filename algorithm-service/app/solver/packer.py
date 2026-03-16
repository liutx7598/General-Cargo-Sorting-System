from __future__ import annotations

from dataclasses import dataclass, field

from app.models.domain import CargoData, HoldData, PlacedCargo
from app.solver.geometry import (
    ORIENTATION_MAP,
    calculate_cargo_centroid,
    calculate_distance_between_boxes,
    check_bounds,
    rotate_dimensions,
)
from app.solver.rule_checker import get_required_isolation_distance


EXISTING_SHELF_PREFERENCE = 0
NEW_SHELF_PREFERENCE = 180
NEW_LAYER_PREFERENCE = 100_000
SHELF_LENGTH_SLACK_WEIGHT = 10
SHELF_DEPTH_SLACK_WEIGHT = 20
LAYER_HEIGHT_GROWTH_WEIGHT = 200
PLACED_HEIGHT_PENALTY_WEIGHT = 3_000
HEIGHT_INFLATION_WEIGHT = 10_000
FOOTPRINT_STABILITY_WEIGHT = 50


@dataclass(slots=True)
class ShelfState:
    """One breakbulk loading row inside a layer."""

    y_offset: float
    depth: float
    x_cursor: float = 0.0


@dataclass(slots=True)
class LayerState:
    """One vertical loading layer made of multiple shelves."""

    z_offset: float
    height: float
    layer_no: int
    shelves: list[ShelfState] = field(default_factory=list)


@dataclass(slots=True)
class PlacementOption:
    """Candidate placement option scored by best-fit decreasing rules."""

    score: tuple[int, int, int, int, int, int, int]
    placement_mode: str
    layer_index: int
    shelf_index: int | None
    layer_no: int
    orientation: str
    origin_x: float
    origin_y: float
    origin_z: float
    placed_length: float
    placed_width: float
    placed_height: float


def orientation_candidates(cargo: CargoData) -> list[str]:
    """Return valid orientation candidates for the cargo."""
    return ["LWH"] if not cargo.rotatable else list(ORIENTATION_MAP.keys())


def _sort_orientations(cargo: CargoData) -> list[str]:
    """Prefer low-height, long-edge-forward orientations for breakbulk rows."""
    return sorted(
        orientation_candidates(cargo),
        key=lambda orientation: (
            rotate_dimensions(cargo.length, cargo.width, cargo.height, orientation)[2],
            rotate_dimensions(cargo.length, cargo.width, cargo.height, orientation)[1],
            -rotate_dimensions(cargo.length, cargo.width, cargo.height, orientation)[0],
        ),
    )


def _can_grow_layer(layer_index: int, layers: list[LayerState]) -> bool:
    """Only the topmost layer may increase in height after it is opened."""
    return layer_index == len(layers) - 1


def _build_score(
    cargo: CargoData,
    placement_preference: int,
    layer_index: int,
    hold: HoldData,
    origin_x: float,
    origin_y: float,
    placed_length: float,
    placed_width: float,
    placed_height: float,
    current_layer_height: float,
) -> tuple[int, int, int, int, int, int, int]:
    """Score a candidate with breakbulk priorities: stable, flat and consolidated."""
    height_inflation = max(0.0, placed_height - cargo.height)
    footprint_area = placed_length * placed_width
    return (
        layer_index,
        int(round(height_inflation * HEIGHT_INFLATION_WEIGHT)),
        int(round(placed_height * PLACED_HEIGHT_PENALTY_WEIGHT)),
        placement_preference,
        int(round(max(0.0, current_layer_height - placed_height) * LAYER_HEIGHT_GROWTH_WEIGHT)),
        int(round((hold.length - (origin_x + placed_length)) * SHELF_LENGTH_SLACK_WEIGHT)),
        int(round((hold.width - (origin_y + placed_width)) * SHELF_DEPTH_SLACK_WEIGHT))
        - int(round(footprint_area * FOOTPRINT_STABILITY_WEIGHT)),
    )


def _build_existing_shelf_option(
    cargo: CargoData,
    hold: HoldData,
    layers: list[LayerState],
    layer_index: int,
    shelf_index: int,
    orientation: str,
) -> PlacementOption | None:
    """Try placing on an existing shelf row."""
    layer = layers[layer_index]
    shelf = layer.shelves[shelf_index]
    placed_length, placed_width, placed_height = rotate_dimensions(cargo.length, cargo.width, cargo.height, orientation)

    if layer.z_offset > 0 and not cargo.stackable:
        return None
    if placed_width > shelf.depth + 1e-6:
        return None
    if not _can_grow_layer(layer_index, layers) and placed_height > layer.height + 1e-6:
        return None

    candidate_x = shelf.x_cursor
    candidate_y = shelf.y_offset
    candidate_z = layer.z_offset
    new_layer_height = max(layer.height, placed_height) if _can_grow_layer(layer_index, layers) else layer.height
    if candidate_z + new_layer_height > hold.height + 1e-6:
        return None
    if not check_bounds(
        candidate_x,
        candidate_y,
        candidate_z,
        placed_length,
        placed_width,
        placed_height,
        hold.length,
        hold.width,
        hold.height,
    ):
        return None

    return PlacementOption(
        score=_build_score(
            cargo=cargo,
            placement_preference=EXISTING_SHELF_PREFERENCE,
            layer_index=layer_index,
            hold=hold,
            origin_x=candidate_x,
            origin_y=candidate_y,
            placed_length=placed_length,
            placed_width=placed_width,
            placed_height=placed_height,
            current_layer_height=layer.height,
        ),
        placement_mode="existing_shelf",
        layer_index=layer_index,
        shelf_index=shelf_index,
        layer_no=layer.layer_no,
        orientation=orientation,
        origin_x=candidate_x,
        origin_y=candidate_y,
        origin_z=candidate_z,
        placed_length=placed_length,
        placed_width=placed_width,
        placed_height=placed_height,
    )


def _build_new_shelf_option(
    cargo: CargoData,
    hold: HoldData,
    layers: list[LayerState],
    layer_index: int,
    orientation: str,
) -> PlacementOption | None:
    """Try opening a new shelf row inside an existing layer."""
    layer = layers[layer_index]
    placed_length, placed_width, placed_height = rotate_dimensions(cargo.length, cargo.width, cargo.height, orientation)

    if layer.z_offset > 0 and not cargo.stackable:
        return None
    if not _can_grow_layer(layer_index, layers) and placed_height > layer.height + 1e-6:
        return None

    candidate_y = sum(shelf.depth for shelf in layer.shelves)
    candidate_x = 0.0
    candidate_z = layer.z_offset
    new_layer_height = max(layer.height, placed_height) if _can_grow_layer(layer_index, layers) else layer.height
    if candidate_y + placed_width > hold.width + 1e-6:
        return None
    if candidate_z + new_layer_height > hold.height + 1e-6:
        return None
    if not check_bounds(
        candidate_x,
        candidate_y,
        candidate_z,
        placed_length,
        placed_width,
        placed_height,
        hold.length,
        hold.width,
        hold.height,
    ):
        return None

    return PlacementOption(
        score=_build_score(
            cargo=cargo,
            placement_preference=NEW_SHELF_PREFERENCE,
            layer_index=layer_index,
            hold=hold,
            origin_x=candidate_x,
            origin_y=candidate_y,
            placed_length=placed_length,
            placed_width=placed_width,
            placed_height=placed_height,
            current_layer_height=layer.height,
        ),
        placement_mode="new_shelf",
        layer_index=layer_index,
        shelf_index=None,
        layer_no=layer.layer_no,
        orientation=orientation,
        origin_x=candidate_x,
        origin_y=candidate_y,
        origin_z=candidate_z,
        placed_length=placed_length,
        placed_width=placed_width,
        placed_height=placed_height,
    )


def _build_new_layer_option(
    cargo: CargoData,
    hold: HoldData,
    layers: list[LayerState],
    orientation: str,
) -> PlacementOption | None:
    """Try opening a new vertical layer."""
    placed_length, placed_width, placed_height = rotate_dimensions(cargo.length, cargo.width, cargo.height, orientation)
    next_z = sum(layer.height for layer in layers)

    if next_z > 0 and not cargo.stackable:
        return None
    if next_z + placed_height > hold.height + 1e-6:
        return None
    if not check_bounds(
        0.0,
        0.0,
        next_z,
        placed_length,
        placed_width,
        placed_height,
        hold.length,
        hold.width,
        hold.height,
    ):
        return None

    return PlacementOption(
        score=_build_score(
            cargo=cargo,
            placement_preference=NEW_LAYER_PREFERENCE,
            layer_index=len(layers),
            hold=hold,
            origin_x=0.0,
            origin_y=0.0,
            placed_length=placed_length,
            placed_width=placed_width,
            placed_height=placed_height,
            current_layer_height=placed_height,
        ),
        placement_mode="new_layer",
        layer_index=len(layers),
        shelf_index=None,
        layer_no=len(layers) + 1,
        orientation=orientation,
        origin_x=0.0,
        origin_y=0.0,
        origin_z=next_z,
        placed_length=placed_length,
        placed_width=placed_width,
        placed_height=placed_height,
    )


def _respects_clearance(
    cargo: CargoData,
    option: PlacementOption,
    placements: list[PlacedCargo],
    cargo_map: dict[int, CargoData],
    default_isolation_distance: float,
) -> bool:
    """Reject candidates that already violate mandatory cargo separation."""
    for placed in placements:
        existing_cargo = cargo_map[placed.cargo_id]
        required_distance = get_required_isolation_distance(existing_cargo, cargo, default_isolation_distance)
        if required_distance <= 0:
            continue
        actual_distance = calculate_distance_between_boxes(
            (placed.origin_x, placed.origin_y, placed.origin_z),
            (placed.placed_length, placed.placed_width, placed.placed_height),
            (option.origin_x, option.origin_y, option.origin_z),
            (option.placed_length, option.placed_width, option.placed_height),
        )
        if actual_distance + 1e-6 < required_distance:
            return False
    return True


def _select_best_option(
    cargo: CargoData,
    hold: HoldData,
    layers: list[LayerState],
    placements: list[PlacedCargo],
    cargo_map: dict[int, CargoData],
    default_isolation_distance: float,
) -> PlacementOption | None:
    """Enumerate all feasible row/layer placements and choose the best fit."""
    options: list[PlacementOption] = []
    for orientation in _sort_orientations(cargo):
        for layer_index, layer in enumerate(layers):
            for shelf_index, _ in enumerate(layer.shelves):
                option = _build_existing_shelf_option(cargo, hold, layers, layer_index, shelf_index, orientation)
                if option is not None and _respects_clearance(cargo, option, placements, cargo_map, default_isolation_distance):
                    options.append(option)
            option = _build_new_shelf_option(cargo, hold, layers, layer_index, orientation)
            if option is not None and _respects_clearance(cargo, option, placements, cargo_map, default_isolation_distance):
                options.append(option)

        option = _build_new_layer_option(cargo, hold, layers, orientation)
        if option is not None and _respects_clearance(cargo, option, placements, cargo_map, default_isolation_distance):
            options.append(option)

    return min(options, key=lambda option: option.score) if options else None


def _apply_option(layers: list[LayerState], option: PlacementOption) -> None:
    """Commit the selected placement option to the mutable packing state."""
    if option.placement_mode == "new_layer":
        layers.append(
            LayerState(
                z_offset=option.origin_z,
                height=option.placed_height,
                layer_no=option.layer_no,
                shelves=[ShelfState(y_offset=0.0, depth=option.placed_width, x_cursor=option.placed_length)],
            )
        )
        return

    layer = layers[option.layer_index]
    if option.placement_mode == "new_shelf":
        new_y_offset = sum(shelf.depth for shelf in layer.shelves)
        layer.shelves.append(ShelfState(y_offset=new_y_offset, depth=option.placed_width, x_cursor=option.placed_length))
    elif option.shelf_index is not None:
        layer.shelves[option.shelf_index].x_cursor = option.origin_x + option.placed_length

    if _can_grow_layer(option.layer_index, layers):
        layer.height = max(layer.height, option.placed_height)


def pack_hold_items(
    hold: HoldData,
    cargos: list[CargoData],
    default_isolation_distance: float = 1.0,
) -> tuple[list[PlacedCargo], list[CargoData]]:
    """Stage C: pack one hold using layered best-fit decreasing shelf packing."""
    placements: list[PlacedCargo] = []
    unplaced: list[CargoData] = []
    layers: list[LayerState] = []
    cargo_map = {cargo.id: cargo for cargo in cargos}
    sorted_cargos = sorted(
        cargos,
        key=lambda item: (
            not item.stackable,
            item.length * item.width,
            item.weight,
            item.length * item.width * item.height,
        ),
        reverse=True,
    )

    for cargo in sorted_cargos:
        option = _select_best_option(cargo, hold, layers, placements, cargo_map, default_isolation_distance)
        if option is None:
            unplaced.append(cargo)
            continue

        _apply_option(layers, option)
        centroid_x, centroid_y, centroid_z = calculate_cargo_centroid(
            option.origin_x,
            option.origin_y,
            option.origin_z,
            option.placed_length,
            option.placed_width,
            option.placed_height,
            cargo.center_offset_x,
            cargo.center_offset_y,
            cargo.center_offset_z,
        )
        placements.append(
            PlacedCargo(
                cargo_id=cargo.id,
                cargo_code=cargo.cargo_code,
                cargo_name=cargo.cargo_name,
                hold_id=hold.id,
                hold_no=hold.hold_no,
                layer_no=option.layer_no,
                orientation=option.orientation,
                origin_x=option.origin_x,
                origin_y=option.origin_y,
                origin_z=option.origin_z,
                placed_length=option.placed_length,
                placed_width=option.placed_width,
                placed_height=option.placed_height,
                centroid_x=centroid_x,
                centroid_y=centroid_y,
                centroid_z=centroid_z,
                weight=cargo.weight,
                cargo_category=cargo.cargo_category,
                dangerous_class=cargo.dangerous_class,
            )
        )

    return placements, unplaced
