package com.stowage.system.repository;

import com.stowage.system.entity.Hold;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface HoldRepository extends JpaRepository<Hold, Long> {
    List<Hold> findByShipIdOrderBySequenceNoAsc(Long shipId);
}

