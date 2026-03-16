package com.stowage.system.client;

import java.util.List;

public final class AlgorithmModels {

    private AlgorithmModels() {
    }

    public record ShipPayload(
        Long id,
        String shipCode,
        String shipName,
        String shipType,
        Double lengthOverall,
        Double lengthBetweenPerpendiculars,
        Double beam,
        Double depth,
        Double lightshipWeight,
        Double lightshipKG,
        Double lightshipLCG,
        Double lightshipTCG,
        Double designDisplacement,
        Double designGM,
        String remark
    ) {
    }

    public record HoldPayload(
        Long id,
        Long shipId,
        String holdNo,
        Double length,
        Double width,
        Double height,
        Double volume,
        Double lcg,
        Double tcg,
        Double vcg,
        Double maxLoadWeight,
        Double deckStrengthLimit,
        Integer sequenceNo,
        String remark
    ) {
    }

    public record CargoPayload(
        Long cargoId,
        String cargoCode,
        String cargoName,
        String cargoCategory,
        String dangerousClass,
        List<String> incompatibleTags,
        Double isolationLevel,
        Integer segregationCode,
        Double weight,
        Double length,
        Double width,
        Double height,
        Boolean stackable,
        Boolean rotatable,
        Double centerOffsetX,
        Double centerOffsetY,
        Double centerOffsetZ,
        String remark
    ) {
    }

    public record HydrostaticPayload(
        Double displacement,
        Double kmValue,
        Double draft,
        String note
    ) {
    }

    public record SolverConfigPayload(
        Double gmMin,
        Double adjacentHoldDiffMax,
        Double ixMax,
        Integer solverTimeLimitSeconds,
        Double fsc,
        Double defaultIsolationDistance,
        Integer maxIterations
    ) {
    }

    public record ExistingPlacementPayload(
        Long cargoId,
        Long holdId,
        Integer layerNo,
        String orientation,
        Double originX,
        Double originY,
        Double originZ,
        Double placedLength,
        Double placedWidth,
        Double placedHeight,
        Double centroidX,
        Double centroidY,
        Double centroidZ,
        String status,
        List<String> violationFlags
    ) {
    }

    public record GeneratePlanPayload(
        Long shipId,
        Long voyageId,
        ShipPayload ship,
        List<HoldPayload> holds,
        List<HydrostaticPayload> hydrostaticTable,
        List<CargoPayload> cargoList,
        SolverConfigPayload config
    ) {
    }

    public record ValidatePlanPayload(
        Long shipId,
        Long voyageId,
        ShipPayload ship,
        List<HoldPayload> holds,
        List<HydrostaticPayload> hydrostaticTable,
        List<CargoPayload> cargoList,
        List<ExistingPlacementPayload> items,
        SolverConfigPayload config
    ) {
    }

    public record HoldSummaryPayload(
        Long holdId,
        String holdNo,
        Double totalWeight,
        Double centroidX,
        Double centroidY,
        Double centroidZ,
        Double utilization,
        Double unitWeightPerVolume,
        Double totalVolume
    ) {
    }

    public record PlanSummaryPayload(
        Double displacement,
        Double kg,
        Double lcg,
        Double tcg,
        Double gm,
        Double deltaGM,
        Double ix,
        String complianceStatus,
        Double longitudinalMoment,
        Double transverseMoment,
        Double verticalMoment,
        List<HoldSummaryPayload> holdSummaries,
        List<Double> adjacentHoldDiffs
    ) {
    }

    public record SolverItemPayload(
        Long cargoId,
        String cargoCode,
        String cargoName,
        Long holdId,
        String holdNo,
        Integer layerNo,
        String orientation,
        Double originX,
        Double originY,
        Double originZ,
        Double placedLength,
        Double placedWidth,
        Double placedHeight,
        Double centroidX,
        Double centroidY,
        Double centroidZ,
        Double weight,
        String cargoCategory,
        String dangerousClass,
        String status,
        List<String> violationFlags
    ) {
    }

    public record WarningPayload(
        Long planId,
        Long cargoId,
        Long holdId,
        String warningType,
        String warningMessage,
        String severity,
        Boolean resolved
    ) {
    }

    public record SolverMetricsPayload(
        Integer solveTimeMs,
        Integer iterationCount,
        String solverStatus,
        List<String> logs
    ) {
    }

    public record SolverResponse(
        Boolean success,
        PlanSummaryPayload planSummary,
        List<SolverItemPayload> items,
        List<WarningPayload> warnings,
        SolverMetricsPayload metrics,
        List<String> reasonList
    ) {
    }
}
