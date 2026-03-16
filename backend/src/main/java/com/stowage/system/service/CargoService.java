package com.stowage.system.service;

import com.stowage.system.dto.CargoDtos;
import com.stowage.system.vo.ViewModels;

import java.util.List;

public interface CargoService {
    List<ViewModels.CargoVO> listCargos();
    ViewModels.CargoVO saveCargo(CargoDtos.CargoUpsertRequest request);
    ViewModels.CargoVO getCargo(Long id);
}

