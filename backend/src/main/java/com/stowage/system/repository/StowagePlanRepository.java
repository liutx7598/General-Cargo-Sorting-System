package com.stowage.system.repository;

import com.stowage.system.entity.StowagePlan;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface StowagePlanRepository extends JpaRepository<StowagePlan, Long> {
    List<StowagePlan> findByVoyageIdOrderByIdDesc(Long voyageId);
}

