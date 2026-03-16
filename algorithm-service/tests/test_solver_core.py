from app.models.domain import CargoData, HoldData, HydrostaticPoint, PlacedCargo, ShipData
from app.solver.evaluator import evaluate_compliance
from app.solver.geometry import calculate_cargo_centroid, calculate_distance_between_boxes, check_bounds, check_overlap, rotate_dimensions
from app.solver.hold_allocator import allocate_holds
from app.solver.packer import pack_hold_items
from app.solver.rule_checker import get_required_isolation_distance
from app.solver.stability import calculate_gm, calculate_hold_centroid, calculate_hold_utilization, calculate_longitudinal_index, calculate_ship_centroid, interpolate_km


def sample_ship() -> ShipData:
    return ShipData(
        id=1,
        ship_code="GC-001",
        ship_name="Harmony Trader",
        ship_type="GENERAL_CARGO",
        length_overall=96.0,
        length_between_perpendiculars=90.0,
        beam=16.8,
        depth=9.2,
        lightship_weight=1680.0,
        lightship_kg=5.5,
        lightship_lcg=47.0,
        lightship_tcg=0.0,
        design_displacement=3650.0,
        design_gm=1.6,
    )


def sample_hold() -> HoldData:
    return HoldData(1, 1, "H1", 17.0, 12.0, 8.0, 1632.0, 19.0, 0.0, 5.0, 420.0, 7.5, 1)


def sample_cargo() -> CargoData:
    return CargoData(11, "CG-001", "Steel Coil", "STEEL", None, [], 0.0, 30.0, 6.0, 2.4, 2.2, True, True)


def test_rotate_dimensions_supports_six_orientations() -> None:
    assert rotate_dimensions(6.0, 2.4, 2.2, "WHL") == (2.4, 2.2, 6.0)


def test_calculate_cargo_centroid() -> None:
    assert calculate_cargo_centroid(1.0, 2.0, 0.5, 6.0, 2.4, 2.2, 0.1, 0.0, -0.1) == (4.1, 3.2, 1.5)


def test_check_bounds() -> None:
    assert check_bounds(0.0, 0.0, 0.0, 6.0, 2.4, 2.2, 17.0, 12.0, 8.0)
    assert not check_bounds(12.0, 0.0, 0.0, 6.0, 2.4, 2.2, 17.0, 12.0, 8.0)


def test_check_overlap() -> None:
    assert check_overlap((0.0, 0.0, 0.0), (2.0, 2.0, 2.0), (1.0, 1.0, 0.0), (2.0, 2.0, 2.0))
    assert not check_overlap((0.0, 0.0, 0.0), (2.0, 2.0, 2.0), (2.0, 0.0, 0.0), (2.0, 2.0, 2.0))


def test_calculate_distance_between_boxes() -> None:
    distance = calculate_distance_between_boxes((0.0, 0.0, 0.0), (2.0, 2.0, 2.0), (3.0, 4.0, 0.0), (1.0, 1.0, 1.0))
    assert round(distance, 3) == round((5.0**0.5), 3)


def test_calculate_hold_centroid() -> None:
    item = PlacedCargo(11, "CG-001", "Steel Coil", 1, "H1", 1, "LWH", 0.0, 0.0, 0.0, 6.0, 2.4, 2.2, 3.0, 1.2, 1.1, 30.0, "STEEL", None)
    result = calculate_hold_centroid(1, "H1", 1632.0, [item])
    assert result.total_weight == 30.0
    assert result.centroid_x == 3.0
    assert result.utilization > 0


def test_calculate_ship_centroid_and_kg() -> None:
    ship = sample_ship()
    item = PlacedCargo(11, "CG-001", "Steel Coil", 1, "H1", 1, "LWH", 0.0, 0.0, 0.0, 6.0, 2.4, 2.2, 20.0, 0.0, 1.1, 30.0, "STEEL", None)
    result = calculate_ship_centroid(ship, [item])
    assert result["displacement"] == 1710.0
    assert result["kg"] < ship.lightship_kg


def test_interpolate_km() -> None:
    points = [HydrostaticPoint(1600.0, 7.1, 4.5), HydrostaticPoint(2000.0, 7.5, 4.9)]
    assert interpolate_km(1800.0, points) == 7.3


def test_calculate_gm() -> None:
    points = [HydrostaticPoint(1600.0, 7.1, 4.5), HydrostaticPoint(2000.0, 7.5, 4.9)]
    km, gm = calculate_gm(1800.0, 5.8, points, fsc=0.1)
    assert km == 7.3
    assert gm == 1.4


def test_calculate_hold_utilization() -> None:
    item = PlacedCargo(11, "CG-001", "Steel Coil", 1, "H1", 1, "LWH", 0.0, 0.0, 0.0, 5.0, 2.0, 2.0, 2.5, 1.0, 1.0, 20.0, "STEEL", None)
    eta, unit = calculate_hold_utilization([item], 100.0)
    assert eta == 0.2
    assert unit == 0.2


def test_calculate_longitudinal_index() -> None:
    items = [
        PlacedCargo(11, "CG-001", "Steel Coil", 1, "H1", 1, "LWH", 0.0, 0.0, 0.0, 5.0, 2.0, 2.0, 10.0, 0.0, 1.0, 20.0, "STEEL", None),
        PlacedCargo(12, "CG-002", "Timber", 2, "H2", 1, "LWH", 0.0, 0.0, 0.0, 5.0, 2.0, 2.0, 30.0, 0.0, 1.0, 10.0, "TIMBER", None),
    ]
    assert calculate_longitudinal_index(items, 20.0) == 300.0


def test_isolation_distance_only_applies_to_required_pairs() -> None:
    steel = CargoData(11, "CG-001", "Steel Coil", "STEEL", None, [], 0.0, 30.0, 6.0, 2.4, 2.2, True, True)
    timber = CargoData(12, "CG-002", "Timber", "TIMBER", None, ["SPARK"], 1.5, 18.0, 7.0, 2.2, 2.4, True, True)
    dangerous = CargoData(13, "CG-003", "Dangerous", "DANGEROUS", "3", ["SPARK"], 3.0, 12.0, 3.0, 2.5, 2.4, False, True)

    assert get_required_isolation_distance(steel, timber, 1.0) == 0.0
    assert get_required_isolation_distance(timber, dangerous, 1.0) >= 3.0


def test_evaluate_compliance() -> None:
    status, reasons = evaluate_compliance([], [], [0.1, 0.2], 1.2, 0.5, 100.0, 500.0, 0.4)
    assert status == "PASS"
    assert reasons == []


def test_allocate_holds_and_pack_hold_items() -> None:
    ship = sample_ship()
    holds = [sample_hold(), HoldData(2, 1, "H2", 18.0, 12.0, 8.0, 1728.0, 40.0, 0.0, 5.0, 450.0, 7.5, 2)]
    cargos = [sample_cargo(), CargoData(12, "CG-002", "Timber", "TIMBER", None, [], 0.0, 18.0, 5.0, 2.0, 2.0, True, True)]
    assignment, status, _ = allocate_holds(ship, cargos, holds, 2)
    assert status in {"OPTIMAL", "FEASIBLE"}
    placements, unplaced = pack_hold_items(holds[0], [cargos[0]])
    assert len(placements) == 1
    assert not unplaced


def test_allocate_holds_prefers_compact_loading_in_one_hold() -> None:
    ship = sample_ship()
    holds = [
        HoldData(1, 1, "H1", 18.0, 12.0, 8.0, 1728.0, 20.0, 0.0, 5.0, 450.0, 7.5, 1),
        HoldData(2, 1, "H2", 18.0, 12.0, 8.0, 1728.0, 47.0, 0.0, 5.0, 450.0, 7.5, 2),
    ]
    cargos = [
        CargoData(11, "CG-001", "Steel Coil A", "STEEL", None, [], 0.0, 30.0, 6.0, 2.4, 2.2, True, True),
        CargoData(12, "CG-002", "Steel Coil B", "STEEL", None, [], 0.0, 28.0, 5.8, 2.3, 2.1, True, True),
        CargoData(13, "CG-003", "Timber Pack", "TIMBER", None, ["SPARK"], 1.5, 18.0, 7.0, 2.4, 2.2, True, True),
    ]
    assignment, status, _ = allocate_holds(ship, cargos, holds, 2)
    assert status in {"OPTIMAL", "FEASIBLE"}
    assert set(assignment.values()) == {2}


def test_pack_hold_items_supports_multiple_rows_for_breakbulk() -> None:
    hold = HoldData(2, 1, "H2", 18.0, 12.0, 8.0, 1728.0, 40.0, 0.0, 5.0, 450.0, 7.5, 2)
    cargos = [
        CargoData(11, "CG-001", "Steel Coil A", "STEEL", None, [], 0.0, 30.0, 6.0, 2.4, 2.2, True, True),
        CargoData(12, "CG-002", "Steel Coil B", "STEEL", None, [], 0.0, 28.0, 5.8, 2.3, 2.1, True, True),
        CargoData(13, "CG-003", "Machinery", "PROJECT", None, [], 0.0, 24.0, 8.0, 1.8, 1.6, True, True),
        CargoData(14, "CG-004", "Timber Bundle", "TIMBER", None, [], 0.0, 18.0, 7.0, 2.4, 2.2, True, True),
    ]

    placements, unplaced = pack_hold_items(hold, cargos)

    assert len(placements) == 4
    assert not unplaced
    assert any(item.origin_y > 0 for item in placements)


def test_pack_hold_items_prefers_same_layer_rows_over_upright_rotation() -> None:
    hold = HoldData(3, 1, "H3", 19.5, 13.0, 8.5, 2154.75, 58.0, 0.0, 5.2, 480.0, 8.0, 3)
    cargos = [
        CargoData(14, "CG-004", "Timber Bundle", "TIMBER", None, ["SPARK"], 1.5, 18.0, 7.0, 2.2, 2.4, True, True),
        CargoData(13, "CG-003", "Steel Bundle", "STEEL", None, [], 0.0, 24.0, 8.0, 1.8, 1.6, True, True),
        CargoData(11, "CG-001", "Steel Coil A", "STEEL", None, [], 0.0, 30.5, 6.0, 2.4, 2.2, True, True),
        CargoData(12, "CG-002", "Steel Coil B", "STEEL", None, [], 0.0, 28.0, 5.8, 2.3, 2.1, True, True),
    ]

    placements, unplaced = pack_hold_items(hold, cargos)

    assert len(placements) == 4
    assert not unplaced
    assert {item.layer_no for item in placements} == {1}
    assert any(item.origin_y > 0 for item in placements)
    assert max(item.placed_height for item in placements) <= 2.4
