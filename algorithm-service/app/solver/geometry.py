from __future__ import annotations

from math import sqrt


ORIENTATION_MAP: dict[str, tuple[int, int, int]] = {
    "LWH": (0, 1, 2),
    "LHW": (0, 2, 1),
    "WLH": (1, 0, 2),
    "WHL": (1, 2, 0),
    "HLW": (2, 0, 1),
    "HWL": (2, 1, 0),
}


def rotate_dimensions(length: float, width: float, height: float, orientation: str) -> tuple[float, float, float]:
    """Rotate a cargo bounding box into one of six orthogonal orientations."""
    if orientation not in ORIENTATION_MAP:
        raise ValueError(f"Unsupported orientation: {orientation}")
    dimensions = (length, width, height)
    axis_order = ORIENTATION_MAP[orientation]
    return dimensions[axis_order[0]], dimensions[axis_order[1]], dimensions[axis_order[2]]


def calculate_cargo_centroid(
    origin_x: float,
    origin_y: float,
    origin_z: float,
    placed_length: float,
    placed_width: float,
    placed_height: float,
    center_offset_x: float = 0.0,
    center_offset_y: float = 0.0,
    center_offset_z: float = 0.0,
) -> tuple[float, float, float]:
    """Calculate the centroid of a placed cargo using the left-aft-bottom origin."""
    centroid_x = origin_x + placed_length / 2.0 + center_offset_x
    centroid_y = origin_y + placed_width / 2.0 + center_offset_y
    centroid_z = origin_z + placed_height / 2.0 + center_offset_z
    return centroid_x, centroid_y, centroid_z


def check_bounds(
    origin_x: float,
    origin_y: float,
    origin_z: float,
    placed_length: float,
    placed_width: float,
    placed_height: float,
    hold_length: float,
    hold_width: float,
    hold_height: float,
    epsilon: float = 1e-6,
) -> bool:
    """Validate that a cargo remains inside hold boundaries."""
    return (
        origin_x >= -epsilon
        and origin_y >= -epsilon
        and origin_z >= -epsilon
        and origin_x + placed_length <= hold_length + epsilon
        and origin_y + placed_width <= hold_width + epsilon
        and origin_z + placed_height <= hold_height + epsilon
    )


def check_overlap(
    box_a_origin: tuple[float, float, float],
    box_a_size: tuple[float, float, float],
    box_b_origin: tuple[float, float, float],
    box_b_size: tuple[float, float, float],
    epsilon: float = 1e-6,
) -> bool:
    """Return True when two 3D boxes overlap with positive volume intersection."""
    ax, ay, az = box_a_origin
    al, aw, ah = box_a_size
    bx, by, bz = box_b_origin
    bl, bw, bh = box_b_size
    separated = (
        ax + al <= bx + epsilon
        or bx + bl <= ax + epsilon
        or ay + aw <= by + epsilon
        or by + bw <= ay + epsilon
        or az + ah <= bz + epsilon
        or bz + bh <= az + epsilon
    )
    return not separated


def calculate_distance_between_boxes(
    box_a_origin: tuple[float, float, float],
    box_a_size: tuple[float, float, float],
    box_b_origin: tuple[float, float, float],
    box_b_size: tuple[float, float, float],
) -> float:
    """Calculate the minimum Euclidean distance between two axis-aligned boxes."""
    ax, ay, az = box_a_origin
    al, aw, ah = box_a_size
    bx, by, bz = box_b_origin
    bl, bw, bh = box_b_size

    delta_x = max(0.0, bx - (ax + al), ax - (bx + bl))
    delta_y = max(0.0, by - (ay + aw), ay - (by + bw))
    delta_z = max(0.0, bz - (az + ah), az - (bz + bh))
    return sqrt(delta_x**2 + delta_y**2 + delta_z**2)

