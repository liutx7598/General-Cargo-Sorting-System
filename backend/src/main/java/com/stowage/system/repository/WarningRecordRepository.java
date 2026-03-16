package com.stowage.system.repository;

import com.stowage.system.entity.WarningRecord;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface WarningRecordRepository extends JpaRepository<WarningRecord, Long> {
    List<WarningRecord> findByPlanIdOrderByIdAsc(Long planId);
    void deleteByPlanId(Long planId);
}

