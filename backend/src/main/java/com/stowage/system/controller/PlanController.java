package com.stowage.system.controller;

import com.stowage.system.common.ApiResponse;
import com.stowage.system.dto.PlanDtos;
import com.stowage.system.service.PlanService;
import com.stowage.system.vo.ViewModels;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/plans")
@RequiredArgsConstructor
public class PlanController {

    private final PlanService planService;

    @GetMapping
    public ApiResponse<List<ViewModels.PlanVO>> listPlans() {
        return ApiResponse.success(planService.listPlans());
    }

    @PostMapping
    public ApiResponse<ViewModels.PlanVO> createPlan(@Valid @RequestBody PlanDtos.PlanCreateRequest request) {
        return ApiResponse.success("配载方案创建成功", planService.createPlan(request));
    }

    @GetMapping("/{id}")
    public ApiResponse<ViewModels.PlanDetailVO> getPlan(@PathVariable Long id) {
        return ApiResponse.success(planService.getPlanDetail(id));
    }

    @GetMapping("/{id}/items")
    public ApiResponse<List<ViewModels.StowageItemVO>> getItems(@PathVariable Long id) {
        return ApiResponse.success(planService.listPlanItems(id));
    }

    @GetMapping("/{id}/warnings")
    public ApiResponse<List<ViewModels.WarningVO>> getWarnings(@PathVariable Long id) {
        return ApiResponse.success(planService.listPlanWarnings(id));
    }

    @PostMapping("/{id}/generate")
    public ApiResponse<ViewModels.PlanDetailVO> generatePlan(
        @PathVariable Long id,
        @Valid @RequestBody PlanDtos.GeneratePlanCommand request
    ) {
        return ApiResponse.success("配载方案生成完成", planService.generatePlan(id, request));
    }

    @PostMapping("/{id}/validate")
    public ApiResponse<ViewModels.PlanDetailVO> validatePlan(
        @PathVariable Long id,
        @Valid @RequestBody PlanDtos.ValidatePlanCommand request
    ) {
        return ApiResponse.success("配载方案校验完成", planService.validatePlan(id, request));
    }
}

