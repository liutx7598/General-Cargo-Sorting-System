package com.stowage.system.repository;

import com.stowage.system.entity.StowageItem;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface StowageItemRepository extends JpaRepository<StowageItem, Long> {
    List<StowageItem> findByPlanIdOrderByIdAsc(Long planId);
    void deleteByPlanId(Long planId);
}

