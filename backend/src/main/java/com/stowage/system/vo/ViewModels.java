package com.stowage.system.vo;

import java.time.LocalDateTime;
import java.util.List;

public final class ViewModels {

    private ViewModels() {
    }

    public record HoldVO(
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

    public record ShipVO(
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

    public record CargoVO(
        Long id,
        String cargoCode,
        String cargoName,
        String cargoCategory,
        String dangerousClass,
        String incompatibleTags,
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

    public record VoyageVO(
        Long id,
        String voyageNo,
        Long shipId,
        String routeInfo,
        String departurePort,
        String arrivalPort,
        LocalDateTime eta,
        LocalDateTime etd,
        String status
    ) {
    }

    public record WarningVO(
        Long id,
        Long planId,
        Long cargoId,
        Long holdId,
        String warningType,
        String warningMessage,
        String severity,
        Boolean resolved
    ) {
    }

    public record StowageItemVO(
        Long id,
        Long planId,
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

    public record HoldMetricVO(
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

    public record PlanVO(
        Long id,
        Long voyageId,
        String planNo,
        Integer version,
        String status,
        Double totalCargoWeight,
        Double displacement,
        Double kg,
        Double lcg,
        Double tcg,
        Double gm,
        String complianceStatus,
        Integer warningCount,
        String remark,
        List<HoldMetricVO> holdSummaries,
        List<Double> adjacentHoldDiffs
    ) {
    }

    public record PlanDetailVO(
        PlanVO plan,
        List<StowageItemVO> items,
        List<WarningVO> warnings
    ) {
    }
}
