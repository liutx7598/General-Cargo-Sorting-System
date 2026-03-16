package com.stowage.system.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDateTime;

public final class VoyageDtos {

    private VoyageDtos() {
    }

    public record VoyageUpsertRequest(
        Long id,
        @NotBlank(message = "voyageNo 不能为空") String voyageNo,
        @NotNull(message = "shipId 不能为空") Long shipId,
        String routeInfo,
        String departurePort,
        String arrivalPort,
        LocalDateTime eta,
        LocalDateTime etd,
        @NotBlank(message = "status 不能为空") String status
    ) {
    }
}

