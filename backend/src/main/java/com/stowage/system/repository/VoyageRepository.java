package com.stowage.system.repository;

import com.stowage.system.entity.Voyage;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface VoyageRepository extends JpaRepository<Voyage, Long> {
    List<Voyage> findByShipIdOrderByIdDesc(Long shipId);
}

