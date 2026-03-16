package com.stowage.system.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public final class CargoDtos {

    private CargoDtos() {
    }

    public record CargoUpsertRequest(
        Long id,
        @NotBlank(message = "cargoCode 不能为空") String cargoCode,
        @NotBlank(message = "cargoName 不能为空") String cargoName,
        @NotBlank(message = "cargoCategory 不能为空") String cargoCategory,
        String dangerousClass,
        String incompatibleTags,
        @NotNull(message = "isolationLevel 不能为空") Double isolationLevel,
        @NotNull(message = "weight 不能为空") Double weight,
        @NotNull(message = "length 不能为空") Double length,
        @NotNull(message = "width 不能为空") Double width,
        @NotNull(message = "height 不能为空") Double height,
        @NotNull(message = "stackable 不能为空") Boolean stackable,
        @NotNull(message = "rotatable 不能为空") Boolean rotatable,
        Double centerOffsetX,
        Double centerOffsetY,
        Double centerOffsetZ,
        String remark
    ) {
    }
}

