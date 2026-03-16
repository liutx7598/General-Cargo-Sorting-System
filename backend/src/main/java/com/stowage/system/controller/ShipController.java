package com.stowage.system.controller;

import com.stowage.system.common.ApiResponse;
import com.stowage.system.dto.ShipDtos;
import com.stowage.system.service.ShipService;
import com.stowage.system.vo.ViewModels;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/ships")
@RequiredArgsConstructor
public class ShipController {

    private final ShipService shipService;

    @GetMapping
    public ApiResponse<List<ViewModels.ShipVO>> listShips() {
        return ApiResponse.success(shipService.listShips());
    }

    @PostMapping
    public ApiResponse<ViewModels.ShipVO> saveShip(@Valid @RequestBody ShipDtos.ShipUpsertRequest request) {
        return ApiResponse.success("船舶保存成功", shipService.saveShip(request));
    }

    @GetMapping("/{id}")
    public ApiResponse<ViewModels.ShipVO> getShip(@PathVariable Long id) {
        return ApiResponse.success(shipService.getShip(id));
    }

    @GetMapping("/{id}/holds")
    public ApiResponse<List<ViewModels.HoldVO>> listHolds(@PathVariable Long id) {
        return ApiResponse.success(shipService.listHolds(id));
    }

    @PostMapping("/{id}/holds")
    public ApiResponse<ViewModels.HoldVO> saveHold(
        @PathVariable Long id,
        @Valid @RequestBody ShipDtos.HoldCreateRequest request
    ) {
        return ApiResponse.success("货舱保存成功", shipService.saveHold(id, request));
    }
}

