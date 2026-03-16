package com.stowage.system.service;

import com.stowage.system.dto.ShipDtos;
import com.stowage.system.vo.ViewModels;

import java.util.List;

public interface ShipService {
    List<ViewModels.ShipVO> listShips();
    ViewModels.ShipVO getShip(Long id);
    ViewModels.ShipVO saveShip(ShipDtos.ShipUpsertRequest request);
    List<ViewModels.HoldVO> listHolds(Long shipId);
    ViewModels.HoldVO saveHold(Long shipId, ShipDtos.HoldCreateRequest request);
}

