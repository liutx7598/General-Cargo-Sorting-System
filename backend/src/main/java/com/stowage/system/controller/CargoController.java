package com.stowage.system.controller;

import com.stowage.system.common.ApiResponse;
import com.stowage.system.dto.CargoDtos;
import com.stowage.system.service.CargoService;
import com.stowage.system.vo.ViewModels;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/cargos")
@RequiredArgsConstructor
public class CargoController {

    private final CargoService cargoService;

    @GetMapping
    public ApiResponse<List<ViewModels.CargoVO>> listCargos() {
        return ApiResponse.success(cargoService.listCargos());
    }

    @PostMapping
    public ApiResponse<ViewModels.CargoVO> saveCargo(@Valid @RequestBody CargoDtos.CargoUpsertRequest request) {
        return ApiResponse.success("货物保存成功", cargoService.saveCargo(request));
    }

    @GetMapping("/{id}")
    public ApiResponse<ViewModels.CargoVO> getCargo(@PathVariable Long id) {
        return ApiResponse.success(cargoService.getCargo(id));
    }
}

