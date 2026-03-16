package com.stowage.system.repository;

import com.stowage.system.entity.Ship;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ShipRepository extends JpaRepository<Ship, Long> {
    Optional<Ship> findByShipCode(String shipCode);
}

