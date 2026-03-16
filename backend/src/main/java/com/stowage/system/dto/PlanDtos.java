package com.stowage.system.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

import java.util.List;

public final class PlanDtos {

    private PlanDtos() {
    }

    public record PlanCreateRequest(
        @NotNull(message = "voyageId 不能为空") Long voyageId,
        @NotBlank(message = "planNo 不能为空") String planNo,
        String remark
    ) {
    }

    public record SolverConfigDTO(
        @NotNull(message = "gmMin 不能为空") Double gmMin,
        @NotNull(message = "adjacentHoldDiffMax 不能为空") Double adjacentHoldDiffMax,
        @NotNull(message = "ixMax 不能为空") Double ixMax,
        @NotNull(message = "solverTimeLimitSeconds 不能为空") Integer solverTimeLimitSeconds,
        Double fsc,
        Double defaultIsolationDistance,
        Integer maxIterations
    ) {
    }

    public record GeneratePlanCommand(
        @NotEmpty(message = "cargoIds 不能为空") List<Long> cargoIds,
        @NotNull(message = "config 不能为空") SolverConfigDTO config
    ) {
    }

    public record ValidatePlanCommand(
        @NotNull(message = "config 不能为空") SolverConfigDTO config
    ) {
    }
}

