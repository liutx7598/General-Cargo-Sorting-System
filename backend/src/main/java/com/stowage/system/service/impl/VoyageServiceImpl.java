package com.stowage.system.service.impl;

import com.stowage.system.dto.VoyageDtos;
import com.stowage.system.entity.Voyage;
import com.stowage.system.exception.NotFoundException;
import com.stowage.system.repository.ShipRepository;
import com.stowage.system.repository.VoyageRepository;
import com.stowage.system.service.VoyageService;
import com.stowage.system.vo.ViewModels;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class VoyageServiceImpl implements VoyageService {

    private final VoyageRepository voyageRepository;
    private final ShipRepository shipRepository;

    @Override
    public List<ViewModels.VoyageVO> listVoyages() {
        return voyageRepository.findAll().stream().map(EntityMapper::toVoyageVO).toList();
    }

    @Override
    @Transactional
    public ViewModels.VoyageVO saveVoyage(VoyageDtos.VoyageUpsertRequest request) {
        shipRepository.findById(request.shipId()).orElseThrow(() -> new NotFoundException("船舶不存在: " + request.shipId()));
        Voyage voyage = request.id() == null ? new Voyage() : voyageRepository.findById(request.id())
            .orElseThrow(() -> new NotFoundException("航次不存在: " + request.id()));
        voyage.setVoyageNo(request.voyageNo());
        voyage.setShipId(request.shipId());
        voyage.setRouteInfo(request.routeInfo());
        voyage.setDeparturePort(request.departurePort());
        voyage.setArrivalPort(request.arrivalPort());
        voyage.setEta(request.eta());
        voyage.setEtd(request.etd());
        voyage.setStatus(request.status());
        return EntityMapper.toVoyageVO(voyageRepository.save(voyage));
    }

    @Override
    public ViewModels.VoyageVO getVoyage(Long id) {
        return EntityMapper.toVoyageVO(voyageRepository.findById(id)
            .orElseThrow(() -> new NotFoundException("航次不存在: " + id)));
    }
}

