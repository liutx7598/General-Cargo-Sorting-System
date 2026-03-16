from __future__ import annotations

from app.models.domain import PlanSummary, WarningData


def evaluate_compliance(
    warnings: list[WarningData],
    hold_summaries: list,
    adjacent_hold_diffs: list[float],
    gm: float,
    gm_min: float,
    ix: float,
    ix_max: float,
    adjacent_hold_diff_max: float,
) -> tuple[str, list[str]]:
    """Evaluate final PASS / FAIL status using stability and rule results."""
    reasons: list[str] = []

    if any(warning.warning_type == "BOUNDARY" for warning in warnings):
        reasons.append("存在空间越界")
    if any(warning.warning_type == "OVERLAP" for warning in warnings):
        reasons.append("存在货物碰撞")
    if any(warning.warning_type == "INCOMPATIBLE" for warning in warnings):
        reasons.append("存在忌装违规")
    if any(warning.warning_type == "ISOLATION" for warning in warnings):
        reasons.append("存在隔离距离不足")
    if any(warning.warning_type == "UNPLACED" for warning in warnings):
        reasons.append("存在未能摆入货舱的货物")
    if gm < gm_min:
        reasons.append(f"GM={gm:.3f} 低于阈值 {gm_min:.3f}")
    if any(diff > adjacent_hold_diff_max for diff in adjacent_hold_diffs):
        reasons.append("相邻舱利用率差异超限")
    if ix > ix_max:
        reasons.append(f"Ix={ix:.3f} 超过阈值 {ix_max:.3f}")
    if any(summary.utilization > 1.0 + 1e-6 for summary in hold_summaries):
        reasons.append("存在舱容比超限")

    return ("PASS" if not reasons else "FAIL"), reasons


def build_empty_summary() -> PlanSummary:
    """Return an empty summary placeholder."""
    return PlanSummary(
        displacement=0.0,
        kg=0.0,
        lcg=0.0,
        tcg=0.0,
        gm=0.0,
        delta_gm=0.0,
        ix=0.0,
        compliance_status="FAIL",
        longitudinal_moment=0.0,
        transverse_moment=0.0,
        vertical_moment=0.0,
        hold_summaries=[],
        adjacent_hold_diffs=[],
    )

