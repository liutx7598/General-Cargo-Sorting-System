package com.stowage.system.service;

import com.stowage.system.dto.VoyageDtos;
import com.stowage.system.vo.ViewModels;

import java.util.List;

public interface VoyageService {
    List<ViewModels.VoyageVO> listVoyages();
    ViewModels.VoyageVO saveVoyage(VoyageDtos.VoyageUpsertRequest request);
    ViewModels.VoyageVO getVoyage(Long id);
}

