package com.stowage.system.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public final class ShipDtos {

    private ShipDtos() {
    }

    public record ShipUpsertRequest(
        Long id,
        @NotBlank(message = "shipCode 不能为空") String shipCode,
        @NotBlank(message = "shipName 不能为空") String shipName,
        @NotBlank(message = "shipType 不能为空") String shipType,
        @NotNull(message = "lengthOverall 不能为空") Double lengthOverall,
        @NotNull(message = "lengthBetweenPerpendiculars 不能为空") Double lengthBetweenPerpendiculars,
        @NotNull(message = "beam 不能为空") Double beam,
        @NotNull(message = "depth 不能为空") Double depth,
        @NotNull(message = "lightshipWeight 不能为空") Double lightshipWeight,
        @NotNull(message = "lightshipKG 不能为空") Double lightshipKG,
        @NotNull(message = "lightshipLCG 不能为空") Double lightshipLCG,
        Double lightshipTCG,
        Double designDisplacement,
        Double designGM,
        String remark
    ) {
    }

    public record HoldCreateRequest(
        Long id,
        @NotBlank(message = "holdNo 不能为空") String holdNo,
        @NotNull(message = "length 不能为空") Double length,
        @NotNull(message = "width 不能为空") Double width,
        @NotNull(message = "height 不能为空") Double height,
        @NotNull(message = "volume 不能为空") Double volume,
        @NotNull(message = "lcg 不能为空") Double lcg,
        @NotNull(message = "tcg 不能为空") Double tcg,
        @NotNull(message = "vcg 不能为空") Double vcg,
        @NotNull(message = "maxLoadWeight 不能为空") Double maxLoadWeight,
        @NotNull(message = "deckStrengthLimit 不能为空") Double deckStrengthLimit,
        @NotNull(message = "sequenceNo 不能为空") Integer sequenceNo,
        String remark
    ) {
    }
}

