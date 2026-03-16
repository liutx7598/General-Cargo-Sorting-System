package com.stowage.system.controller;

import com.stowage.system.common.ApiResponse;
import com.stowage.system.dto.VoyageDtos;
import com.stowage.system.service.VoyageService;
import com.stowage.system.vo.ViewModels;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/voyages")
@RequiredArgsConstructor
public class VoyageController {

    private final VoyageService voyageService;

    @GetMapping
    public ApiResponse<List<ViewModels.VoyageVO>> listVoyages() {
        return ApiResponse.success(voyageService.listVoyages());
    }

    @PostMapping
    public ApiResponse<ViewModels.VoyageVO> saveVoyage(@Valid @RequestBody VoyageDtos.VoyageUpsertRequest request) {
        return ApiResponse.success("航次保存成功", voyageService.saveVoyage(request));
    }

    @GetMapping("/{id}")
    public ApiResponse<ViewModels.VoyageVO> getVoyage(@PathVariable Long id) {
        return ApiResponse.success(voyageService.getVoyage(id));
    }
}

