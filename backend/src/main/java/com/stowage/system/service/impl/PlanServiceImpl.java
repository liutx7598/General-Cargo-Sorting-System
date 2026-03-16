package com.stowage.system.service.impl;

import com.stowage.system.client.AlgorithmModels;
import com.stowage.system.client.AlgorithmServiceClient;
import com.stowage.system.dto.PlanDtos;
import com.stowage.system.entity.*;
import com.stowage.system.exception.NotFoundException;
import com.stowage.system.repository.*;
import com.stowage.system.service.PlanService;
import com.stowage.system.vo.ViewModels;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PlanServiceImpl implements PlanService {

    private final StowagePlanRepository planRepository;
    private final StowageItemRepository itemRepository;
    private final WarningRecordRepository warningRepository;
    private final VoyageRepository voyageRepository;
    private final ShipRepository shipRepository;
    private final HoldRepository holdRepository;
    private final ShipHydrostaticRepository hydrostaticRepository;
    private final CargoRepository cargoRepository;
    private final AlgorithmServiceClient algorithmServiceClient;

    @Override
    public List<ViewModels.PlanVO> listPlans() {
        return planRepository.findAll().stream()
            .sorted(Comparator.comparing(StowagePlan::getId).reversed())
            .map(plan -> EntityMapper.toPlanVO(plan, List.of(), List.of()))
            .toList();
    }

    @Override
    @Transactional
    public ViewModels.PlanVO createPlan(PlanDtos.PlanCreateRequest request) {
        voyageRepository.findById(request.voyageId()).orElseThrow(() -> new NotFoundException("航次不存在: " + request.voyageId()));
        StowagePlan plan = new StowagePlan();
        plan.setVoyageId(request.voyageId());
        plan.setPlanNo(request.planNo());
        plan.setVersion(1);
        plan.setStatus("DRAFT");
        plan.setComplianceStatus("PENDING");
        plan.setWarningCount(0);
        plan.setTotalCargoWeight(0.0);
        plan.setDisplacement(0.0);
        plan.setKg(0.0);
        plan.setLcg(0.0);
        plan.setTcg(0.0);
        plan.setGm(0.0);
        plan.setRemark(request.remark());
        return EntityMapper.toPlanVO(planRepository.save(plan), List.of(), List.of());
    }

    @Override
    public ViewModels.PlanDetailVO getPlanDetail(Long id) {
        StowagePlan plan = getPlanEntity(id);
        Voyage voyage = getVoyage(plan.getVoyageId());
        List<Hold> holds = holdRepository.findByShipIdOrderBySequenceNoAsc(voyage.getShipId());
        List<StowageItem> items = itemRepository.findByPlanIdOrderByIdAsc(id);
        List<WarningRecord> warnings = warningRepository.findByPlanIdOrderByIdAsc(id);
        return new ViewModels.PlanDetailVO(
            EntityMapper.toPlanVO(plan, buildHoldMetricsFromItems(items, holds), buildAdjacentDiffs(items, holds)),
            items.stream().map(EntityMapper::toStowageItemVO).toList(),
            warnings.stream().map(EntityMapper::toWarningVO).toList()
        );
    }

    @Override
    public List<ViewModels.StowageItemVO> listPlanItems(Long planId) {
        return itemRepository.findByPlanIdOrderByIdAsc(planId).stream().map(EntityMapper::toStowageItemVO).toList();
    }

    @Override
    public List<ViewModels.WarningVO> listPlanWarnings(Long planId) {
        return warningRepository.findByPlanIdOrderByIdAsc(planId).stream().map(EntityMapper::toWarningVO).toList();
    }

    @Override
    @Transactional
    public ViewModels.PlanDetailVO generatePlan(Long planId, PlanDtos.GeneratePlanCommand request) {
        StowagePlan plan = getPlanEntity(planId);
        Voyage voyage = getVoyage(plan.getVoyageId());
        Ship ship = shipRepository.findById(voyage.getShipId()).orElseThrow(() -> new NotFoundException("船舶不存在: " + voyage.getShipId()));
        List<Hold> holds = holdRepository.findByShipIdOrderBySequenceNoAsc(ship.getId());
        List<ShipHydrostatic> hydrostatics = hydrostaticRepository.findByShipIdOrderByDisplacementAsc(ship.getId());
        List<Cargo> cargos = cargoRepository.findAllById(request.cargoIds());
        if (cargos.size() != request.cargoIds().size()) {
            throw new NotFoundException("部分货物不存在");
        }

        AlgorithmModels.SolverResponse response = algorithmServiceClient.generatePlan(
            new AlgorithmModels.GeneratePlanPayload(
                ship.getId(),
                voyage.getId(),
                EntityMapper.toShipPayload(ship),
                holds.stream().map(EntityMapper::toHoldPayload).toList(),
                hydrostatics.stream().map(EntityMapper::toHydrostaticPayload).toList(),
                cargos.stream().map(EntityMapper::toCargoPayload).toList(),
                EntityMapper.toConfigPayload(request.config())
            )
        );

        persistPlanResult(plan, cargos, response);
        return buildDetailFromResponse(plan, response);
    }

    @Override
    @Transactional
    public ViewModels.PlanDetailVO validatePlan(Long planId, PlanDtos.ValidatePlanCommand request) {
        StowagePlan plan = getPlanEntity(planId);
        Voyage voyage = getVoyage(plan.getVoyageId());
        Ship ship = shipRepository.findById(voyage.getShipId()).orElseThrow(() -> new NotFoundException("船舶不存在: " + voyage.getShipId()));
        List<Hold> holds = holdRepository.findByShipIdOrderBySequenceNoAsc(ship.getId());
        List<ShipHydrostatic> hydrostatics = hydrostaticRepository.findByShipIdOrderByDisplacementAsc(ship.getId());
        List<StowageItem> items = itemRepository.findByPlanIdOrderByIdAsc(planId);
        List<Cargo> cargos = cargoRepository.findAllById(items.stream().map(StowageItem::getCargoId).toList());

        AlgorithmModels.SolverResponse response = algorithmServiceClient.validatePlan(
            new AlgorithmModels.ValidatePlanPayload(
                ship.getId(),
                voyage.getId(),
                EntityMapper.toShipPayload(ship),
                holds.stream().map(EntityMapper::toHoldPayload).toList(),
                hydrostatics.stream().map(EntityMapper::toHydrostaticPayload).toList(),
                cargos.stream().map(EntityMapper::toCargoPayload).toList(),
                items.stream().map(EntityMapper::toExistingPlacementPayload).toList(),
                EntityMapper.toConfigPayload(request.config())
            )
        );

        persistPlanResult(plan, cargos, response);
        return buildDetailFromResponse(plan, response);
    }

    private ViewModels.PlanDetailVO buildDetailFromResponse(StowagePlan plan, AlgorithmModels.SolverResponse response) {
        List<ViewModels.StowageItemVO> items = itemRepository.findByPlanIdOrderByIdAsc(plan.getId()).stream()
            .map(EntityMapper::toStowageItemVO)
            .toList();
        List<ViewModels.WarningVO> warnings = warningRepository.findByPlanIdOrderByIdAsc(plan.getId()).stream()
            .map(EntityMapper::toWarningVO)
            .toList();
        List<ViewModels.HoldMetricVO> holdMetrics = Optional.ofNullable(response.planSummary())
            .map(summary -> Optional.ofNullable(summary.holdSummaries()).orElse(List.of()).stream()
                .map(this::toHoldMetricVO)
                .toList())
            .orElse(List.of());
        List<Double> adjacentDiffs = response.planSummary() == null || response.planSummary().adjacentHoldDiffs() == null
            ? List.of()
            : response.planSummary().adjacentHoldDiffs();
        return new ViewModels.PlanDetailVO(
            EntityMapper.toPlanVO(plan, holdMetrics, adjacentDiffs),
            items,
            warnings
        );
    }

    private ViewModels.HoldMetricVO toHoldMetricVO(AlgorithmModels.HoldSummaryPayload payload) {
        return new ViewModels.HoldMetricVO(
            payload.holdId(), payload.holdNo(), payload.totalWeight(), payload.centroidX(), payload.centroidY(),
            payload.centroidZ(), payload.utilization(), payload.unitWeightPerVolume(), payload.totalVolume()
        );
    }

    private void persistPlanResult(StowagePlan plan, List<Cargo> cargos, AlgorithmModels.SolverResponse response) {
        plan.setStatus(Boolean.TRUE.equals(response.success()) ? "GENERATED" : "FAILED");
        plan.setTotalCargoWeight(cargos.stream().mapToDouble(Cargo::getWeight).sum());
        if (response.planSummary() != null) {
            plan.setDisplacement(response.planSummary().displacement());
            plan.setKg(response.planSummary().kg());
            plan.setLcg(response.planSummary().lcg());
            plan.setTcg(response.planSummary().tcg());
            plan.setGm(response.planSummary().gm());
            plan.setComplianceStatus(response.planSummary().complianceStatus());
        }
        plan.setWarningCount(response.warnings() == null ? 0 : response.warnings().size());
        planRepository.save(plan);

        itemRepository.deleteByPlanId(plan.getId());
        warningRepository.deleteByPlanId(plan.getId());

        List<StowageItem> items = Optional.ofNullable(response.items()).orElse(List.of()).stream()
            .map(payload -> {
                StowageItem item = new StowageItem();
                item.setPlanId(plan.getId());
                item.setCargoId(payload.cargoId());
                item.setHoldId(payload.holdId());
                item.setLayerNo(payload.layerNo());
                item.setOrientation(payload.orientation());
                item.setOriginX(payload.originX());
                item.setOriginY(payload.originY());
                item.setOriginZ(payload.originZ());
                item.setPlacedLength(payload.placedLength());
                item.setPlacedWidth(payload.placedWidth());
                item.setPlacedHeight(payload.placedHeight());
                item.setCentroidX(payload.centroidX());
                item.setCentroidY(payload.centroidY());
                item.setCentroidZ(payload.centroidZ());
                item.setStatus(payload.status());
                item.setViolationFlags(EntityMapper.joinCsv(payload.violationFlags()));
                return item;
            })
            .toList();
        itemRepository.saveAll(items);

        List<WarningRecord> warnings = Optional.ofNullable(response.warnings()).orElse(List.of()).stream()
            .map(payload -> {
                WarningRecord warning = new WarningRecord();
                warning.setPlanId(plan.getId());
                warning.setCargoId(payload.cargoId());
                warning.setHoldId(payload.holdId());
                warning.setWarningType(payload.warningType());
                warning.setWarningMessage(payload.warningMessage());
                warning.setSeverity(payload.severity());
                warning.setResolved(Boolean.TRUE.equals(payload.resolved()));
                return warning;
            })
            .toList();
        warningRepository.saveAll(warnings);
    }

    private List<ViewModels.HoldMetricVO> buildHoldMetricsFromItems(List<StowageItem> items, List<Hold> holds) {
        Map<Long, Double> cargoWeightMap = cargoRepository.findAllById(
                items.stream().map(StowageItem::getCargoId).distinct().toList()
            ).stream()
            .collect(Collectors.toMap(Cargo::getId, Cargo::getWeight));
        Map<Long, List<StowageItem>> grouped = items.stream().collect(Collectors.groupingBy(StowageItem::getHoldId));
        return holds.stream().map(hold -> {
            List<StowageItem> holdItems = grouped.getOrDefault(hold.getId(), List.of());
            double totalWeight = holdItems.stream()
                .mapToDouble(item -> cargoWeightMap.getOrDefault(item.getCargoId(), 0.0))
                .sum();
            double weightedX = 0.0;
            double weightedY = 0.0;
            double weightedZ = 0.0;
            double totalVolume = 0.0;
            for (StowageItem item : holdItems) {
                double weight = cargoWeightMap.getOrDefault(item.getCargoId(), 0.0);
                weightedX += weight * Optional.ofNullable(item.getCentroidX()).orElse(0.0);
                weightedY += weight * Optional.ofNullable(item.getCentroidY()).orElse(0.0);
                weightedZ += weight * Optional.ofNullable(item.getCentroidZ()).orElse(0.0);
                totalVolume += Optional.ofNullable(item.getPlacedLength()).orElse(0.0)
                    * Optional.ofNullable(item.getPlacedWidth()).orElse(0.0)
                    * Optional.ofNullable(item.getPlacedHeight()).orElse(0.0);
            }
            double centroidX = totalWeight == 0.0 ? 0.0 : weightedX / totalWeight;
            double centroidY = totalWeight == 0.0 ? 0.0 : weightedY / totalWeight;
            double centroidZ = totalWeight == 0.0 ? 0.0 : weightedZ / totalWeight;
            double utilization = hold.getVolume() == null || hold.getVolume() == 0.0 ? 0.0 : totalVolume / hold.getVolume();
            double unitWeightPerVolume = hold.getVolume() == null || hold.getVolume() == 0.0 ? 0.0 : totalWeight / hold.getVolume();
            return new ViewModels.HoldMetricVO(
                hold.getId(), hold.getHoldNo(), totalWeight, centroidX, centroidY, centroidZ, utilization, unitWeightPerVolume, totalVolume
            );
        }).toList();
    }

    private List<Double> buildAdjacentDiffs(List<StowageItem> items, List<Hold> holds) {
        List<ViewModels.HoldMetricVO> holdMetrics = buildHoldMetricsFromItems(items, holds);
        List<Double> result = new ArrayList<>();
        for (int index = 0; index < holdMetrics.size() - 1; index++) {
            result.add(Math.abs(holdMetrics.get(index).utilization() - holdMetrics.get(index + 1).utilization()));
        }
        return result;
    }

    private StowagePlan getPlanEntity(Long planId) {
        return planRepository.findById(planId).orElseThrow(() -> new NotFoundException("配载方案不存在: " + planId));
    }

    private Voyage getVoyage(Long voyageId) {
        return voyageRepository.findById(voyageId).orElseThrow(() -> new NotFoundException("航次不存在: " + voyageId));
    }
}
