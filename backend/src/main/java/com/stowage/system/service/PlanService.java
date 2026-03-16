package com.stowage.system.service;

import com.stowage.system.dto.PlanDtos;
import com.stowage.system.vo.ViewModels;

import java.util.List;

public interface PlanService {
    List<ViewModels.PlanVO> listPlans();
    ViewModels.PlanVO createPlan(PlanDtos.PlanCreateRequest request);
    ViewModels.PlanDetailVO getPlanDetail(Long id);
    List<ViewModels.StowageItemVO> listPlanItems(Long planId);
    List<ViewModels.WarningVO> listPlanWarnings(Long planId);
    ViewModels.PlanDetailVO generatePlan(Long planId, PlanDtos.GeneratePlanCommand request);
    ViewModels.PlanDetailVO validatePlan(Long planId, PlanDtos.ValidatePlanCommand request);
}

