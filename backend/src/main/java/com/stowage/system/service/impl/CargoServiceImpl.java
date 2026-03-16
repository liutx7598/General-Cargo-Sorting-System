package com.stowage.system.service.impl;

import com.stowage.system.dto.CargoDtos;
import com.stowage.system.entity.Cargo;
import com.stowage.system.exception.NotFoundException;
import com.stowage.system.repository.CargoRepository;
import com.stowage.system.service.CargoService;
import com.stowage.system.vo.ViewModels;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CargoServiceImpl implements CargoService {

    private final CargoRepository cargoRepository;

    @Override
    @Cacheable("cargos")
    public List<ViewModels.CargoVO> listCargos() {
        return cargoRepository.findAll().stream().map(EntityMapper::toCargoVO).toList();
    }

    @Override
    @Transactional
    @CacheEvict(value = "cargos", allEntries = true)
    public ViewModels.CargoVO saveCargo(CargoDtos.CargoUpsertRequest request) {
        Cargo cargo = request.id() == null ? new Cargo() : cargoRepository.findById(request.id())
            .orElseThrow(() -> new NotFoundException("货物不存在: " + request.id()));
        cargo.setCargoCode(request.cargoCode());
        cargo.setCargoName(request.cargoName());
        cargo.setCargoCategory(request.cargoCategory());
        cargo.setDangerousClass(request.dangerousClass());
        cargo.setIncompatibleTags(request.incompatibleTags());
        cargo.setIsolationLevel(request.isolationLevel());
        cargo.setWeight(request.weight());
        cargo.setLength(request.length());
        cargo.setWidth(request.width());
        cargo.setHeight(request.height());
        cargo.setStackable(request.stackable());
        cargo.setRotatable(request.rotatable());
        cargo.setCenterOffsetX(request.centerOffsetX() == null ? 0.0 : request.centerOffsetX());
        cargo.setCenterOffsetY(request.centerOffsetY() == null ? 0.0 : request.centerOffsetY());
        cargo.setCenterOffsetZ(request.centerOffsetZ() == null ? 0.0 : request.centerOffsetZ());
        cargo.setRemark(request.remark());
        return EntityMapper.toCargoVO(cargoRepository.save(cargo));
    }

    @Override
    public ViewModels.CargoVO getCargo(Long id) {
        return EntityMapper.toCargoVO(cargoRepository.findById(id)
            .orElseThrow(() -> new NotFoundException("货物不存在: " + id)));
    }
}

