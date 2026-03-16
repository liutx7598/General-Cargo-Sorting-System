package com.stowage.system.repository;

import com.stowage.system.entity.ShipHydrostatic;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ShipHydrostaticRepository extends JpaRepository<ShipHydrostatic, Long> {
    List<ShipHydrostatic> findByShipIdOrderByDisplacementAsc(Long shipId);
}

