from __future__ import annotations

from app.models.domain import CargoData, HoldData, HydrostaticPoint, ShipData


def load_sample_context(ship_id: int) -> tuple[ShipData, list[HoldData], list[HydrostaticPoint]]:
    """Provide built-in sample ship context for standalone solver usage."""
    if ship_id != 1:
        raise ValueError(f"No embedded sample ship for id={ship_id}")

    ship = ShipData(
        id=1,
        ship_code="GC-001",
        ship_name="M/V Harmony Trader",
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
        remark="Sample general cargo vessel",
    )

    holds = [
        HoldData(1, 1, "H1", 17.0, 12.0, 8.0, 1632.0, 19.0, 0.0, 5.0, 420.0, 7.5, 1, "Fore hold"),
        HoldData(2, 1, "H2", 18.0, 12.6, 8.0, 1814.4, 37.5, 0.0, 5.0, 450.0, 7.8, 2, "Forward mid hold"),
        HoldData(3, 1, "H3", 19.5, 13.0, 8.5, 2154.75, 58.0, 0.0, 5.2, 480.0, 8.0, 3, "Aft mid hold"),
        HoldData(4, 1, "H4", 16.0, 11.8, 7.5, 1416.0, 77.5, 0.0, 4.8, 390.0, 7.2, 4, "Aft hold"),
    ]

    hydrostatic = [
        HydrostaticPoint(1600.0, 7.15, 4.5, "light"),
        HydrostaticPoint(1900.0, 7.45, 4.8, "sample-1"),
        HydrostaticPoint(2200.0, 7.72, 5.1, "sample-2"),
        HydrostaticPoint(2600.0, 8.01, 5.5, "sample-3"),
        HydrostaticPoint(3000.0, 8.24, 5.9, "sample-4"),
        HydrostaticPoint(3400.0, 8.46, 6.2, "sample-5"),
        HydrostaticPoint(3800.0, 8.63, 6.5, "sample-6"),
    ]
    return ship, holds, hydrostatic

