package com.stowage.system.service.impl;

import com.stowage.system.dto.ShipDtos;
import com.stowage.system.entity.Hold;
import com.stowage.system.entity.Ship;
import com.stowage.system.exception.NotFoundException;
import com.stowage.system.repository.HoldRepository;
import com.stowage.system.repository.ShipRepository;
import com.stowage.system.service.ShipService;
import com.stowage.system.vo.ViewModels;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ShipServiceImpl implements ShipService {

    private final ShipRepository shipRepository;
    private final HoldRepository holdRepository;

    @Override
    @Cacheable("ships")
    public List<ViewModels.ShipVO> listShips() {
        return shipRepository.findAll().stream().map(EntityMapper::toShipVO).toList();
    }

    @Override
    public ViewModels.ShipVO getShip(Long id) {
        return EntityMapper.toShipVO(findShip(id));
    }

    @Override
    @Transactional
    @CacheEvict(value = "ships", allEntries = true)
    public ViewModels.ShipVO saveShip(ShipDtos.ShipUpsertRequest request) {
        Ship ship = request.id() == null ? new Ship() : findShip(request.id());
        ship.setShipCode(request.shipCode());
        ship.setShipName(request.shipName());
        ship.setShipType(request.shipType());
        ship.setLengthOverall(request.lengthOverall());
        ship.setLengthBetweenPerpendiculars(request.lengthBetweenPerpendiculars());
        ship.setBeam(request.beam());
        ship.setDepth(request.depth());
        ship.setLightshipWeight(request.lightshipWeight());
        ship.setLightshipKG(request.lightshipKG());
        ship.setLightshipLCG(request.lightshipLCG());
        ship.setLightshipTCG(request.lightshipTCG() == null ? 0.0 : request.lightshipTCG());
        ship.setDesignDisplacement(request.designDisplacement());
        ship.setDesignGM(request.designGM());
        ship.setRemark(request.remark());
        return EntityMapper.toShipVO(shipRepository.save(ship));
    }

    @Override
    public List<ViewModels.HoldVO> listHolds(Long shipId) {
        findShip(shipId);
        return holdRepository.findByShipIdOrderBySequenceNoAsc(shipId).stream().map(EntityMapper::toHoldVO).toList();
    }

    @Override
    @Transactional
    public ViewModels.HoldVO saveHold(Long shipId, ShipDtos.HoldCreateRequest request) {
        findShip(shipId);
        Hold hold = request.id() == null ? new Hold() : holdRepository.findById(request.id())
            .orElseThrow(() -> new NotFoundException("货舱不存在: " + request.id()));
        hold.setShipId(shipId);
        hold.setHoldNo(request.holdNo());
        hold.setLength(request.length());
        hold.setWidth(request.width());
        hold.setHeight(request.height());
        hold.setVolume(request.volume());
        hold.setLcg(request.lcg());
        hold.setTcg(request.tcg());
        hold.setVcg(request.vcg());
        hold.setMaxLoadWeight(request.maxLoadWeight());
        hold.setDeckStrengthLimit(request.deckStrengthLimit());
        hold.setSequenceNo(request.sequenceNo());
        hold.setRemark(request.remark());
        return EntityMapper.toHoldVO(holdRepository.save(hold));
    }

    private Ship findShip(Long id) {
        return shipRepository.findById(id).orElseThrow(() -> new NotFoundException("船舶不存在: " + id));
    }
}

