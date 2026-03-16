package com.stowage.system.service.impl;

import com.stowage.system.client.AlgorithmModels;
import com.stowage.system.dto.PlanDtos;
import com.stowage.system.entity.*;
import com.stowage.system.vo.ViewModels;

import java.util.*;
import java.util.stream.Collectors;

final class EntityMapper {

    private EntityMapper() {
    }

    static ViewModels.ShipVO toShipVO(Ship ship) {
        return new ViewModels.ShipVO(
            ship.getId(), ship.getShipCode(), ship.getShipName(), ship.getShipType(),
            ship.getLengthOverall(), ship.getLengthBetweenPerpendiculars(), ship.getBeam(), ship.getDepth(),
            ship.getLightshipWeight(), ship.getLightshipKG(), ship.getLightshipLCG(), ship.getLightshipTCG(),
            ship.getDesignDisplacement(), ship.getDesignGM(), ship.getRemark()
        );
    }

    static ViewModels.HoldVO toHoldVO(Hold hold) {
        return new ViewModels.HoldVO(
            hold.getId(), hold.getShipId(), hold.getHoldNo(), hold.getLength(), hold.getWidth(), hold.getHeight(),
            hold.getVolume(), hold.getLcg(), hold.getTcg(), hold.getVcg(), hold.getMaxLoadWeight(),
            hold.getDeckStrengthLimit(), hold.getSequenceNo(), hold.getRemark()
        );
    }

    static ViewModels.CargoVO toCargoVO(Cargo cargo) {
        return new ViewModels.CargoVO(
            cargo.getId(), cargo.getCargoCode(), cargo.getCargoName(), cargo.getCargoCategory(),
            cargo.getDangerousClass(), cargo.getIncompatibleTags(), cargo.getIsolationLevel(), cargo.getSegregationCode(), cargo.getWeight(),
            cargo.getLength(), cargo.getWidth(), cargo.getHeight(), cargo.getStackable(), cargo.getRotatable(),
            cargo.getCenterOffsetX(), cargo.getCenterOffsetY(), cargo.getCenterOffsetZ(), cargo.getRemark()
        );
    }

    static ViewModels.VoyageVO toVoyageVO(Voyage voyage) {
        return new ViewModels.VoyageVO(
            voyage.getId(), voyage.getVoyageNo(), voyage.getShipId(), voyage.getRouteInfo(),
            voyage.getDeparturePort(), voyage.getArrivalPort(), voyage.getEta(), voyage.getEtd(), voyage.getStatus()
        );
    }

    static ViewModels.WarningVO toWarningVO(WarningRecord warning) {
        return new ViewModels.WarningVO(
            warning.getId(), warning.getPlanId(), warning.getCargoId(), warning.getHoldId(),
            warning.getWarningType(), warning.getWarningMessage(), warning.getSeverity(), warning.getResolved()
        );
    }

    static ViewModels.StowageItemVO toStowageItemVO(StowageItem item) {
        return new ViewModels.StowageItemVO(
            item.getId(), item.getPlanId(), item.getCargoId(), item.getHoldId(), item.getLayerNo(), item.getOrientation(),
            item.getOriginX(), item.getOriginY(), item.getOriginZ(), item.getPlacedLength(), item.getPlacedWidth(),
            item.getPlacedHeight(), item.getCentroidX(), item.getCentroidY(), item.getCentroidZ(), item.getStatus(),
            splitCsv(item.getViolationFlags())
        );
    }

    static ViewModels.PlanVO toPlanVO(StowagePlan plan, List<ViewModels.HoldMetricVO> holdMetrics, List<Double> adjacentDiffs) {
        return new ViewModels.PlanVO(
            plan.getId(), plan.getVoyageId(), plan.getPlanNo(), plan.getVersion(), plan.getStatus(), plan.getTotalCargoWeight(),
            plan.getDisplacement(), plan.getKg(), plan.getLcg(), plan.getTcg(), plan.getGm(), plan.getComplianceStatus(),
            plan.getWarningCount(), plan.getRemark(), holdMetrics, adjacentDiffs
        );
    }

    static AlgorithmModels.ShipPayload toShipPayload(Ship ship) {
        return new AlgorithmModels.ShipPayload(
            ship.getId(), ship.getShipCode(), ship.getShipName(), ship.getShipType(), ship.getLengthOverall(),
            ship.getLengthBetweenPerpendiculars(), ship.getBeam(), ship.getDepth(), ship.getLightshipWeight(),
            ship.getLightshipKG(), ship.getLightshipLCG(), ship.getLightshipTCG(), ship.getDesignDisplacement(),
            ship.getDesignGM(), ship.getRemark()
        );
    }

    static AlgorithmModels.HoldPayload toHoldPayload(Hold hold) {
        return new AlgorithmModels.HoldPayload(
            hold.getId(), hold.getShipId(), hold.getHoldNo(), hold.getLength(), hold.getWidth(), hold.getHeight(),
            hold.getVolume(), hold.getLcg(), hold.getTcg(), hold.getVcg(), hold.getMaxLoadWeight(),
            hold.getDeckStrengthLimit(), hold.getSequenceNo(), hold.getRemark()
        );
    }

    static AlgorithmModels.CargoPayload toCargoPayload(Cargo cargo) {
        return new AlgorithmModels.CargoPayload(
            cargo.getId(), cargo.getCargoCode(), cargo.getCargoName(), cargo.getCargoCategory(), cargo.getDangerousClass(),
            splitCsv(cargo.getIncompatibleTags()), cargo.getIsolationLevel(), cargo.getSegregationCode(), cargo.getWeight(), cargo.getLength(),
            cargo.getWidth(), cargo.getHeight(), cargo.getStackable(), cargo.getRotatable(), cargo.getCenterOffsetX(),
            cargo.getCenterOffsetY(), cargo.getCenterOffsetZ(), cargo.getRemark()
        );
    }

    static AlgorithmModels.HydrostaticPayload toHydrostaticPayload(ShipHydrostatic hydrostatic) {
        return new AlgorithmModels.HydrostaticPayload(
            hydrostatic.getDisplacement(), hydrostatic.getKmValue(), hydrostatic.getDraft(), hydrostatic.getNote()
        );
    }

    static AlgorithmModels.ExistingPlacementPayload toExistingPlacementPayload(StowageItem item) {
        return new AlgorithmModels.ExistingPlacementPayload(
            item.getCargoId(), item.getHoldId(), item.getLayerNo(), item.getOrientation(), item.getOriginX(),
            item.getOriginY(), item.getOriginZ(), item.getPlacedLength(), item.getPlacedWidth(), item.getPlacedHeight(),
            item.getCentroidX(), item.getCentroidY(), item.getCentroidZ(), item.getStatus(), splitCsv(item.getViolationFlags())
        );
    }

    static AlgorithmModels.SolverConfigPayload toConfigPayload(PlanDtos.SolverConfigDTO config) {
        return new AlgorithmModels.SolverConfigPayload(
            config.gmMin(), config.adjacentHoldDiffMax(), config.ixMax(), config.solverTimeLimitSeconds(),
            defaultValue(config.fsc(), 0.0), defaultValue(config.defaultIsolationDistance(), 1.0),
            config.maxIterations() == null ? 3 : config.maxIterations()
        );
    }

    static List<String> splitCsv(String raw) {
        if (raw == null || raw.isBlank()) {
            return List.of();
        }
        return Arrays.stream(raw.split(","))
            .map(String::trim)
            .filter(value -> !value.isBlank())
            .toList();
    }

    static String joinCsv(List<String> values) {
        if (values == null || values.isEmpty()) {
            return "";
        }
        return values.stream().filter(Objects::nonNull).collect(Collectors.joining(","));
    }

    private static Double defaultValue(Double value, Double fallback) {
        return value == null ? fallback : value;
    }
}
