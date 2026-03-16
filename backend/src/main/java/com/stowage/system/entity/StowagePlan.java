package com.stowage.system.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
@Table(name = "stowage_plan")
public class StowagePlan {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long voyageId;

    @Column(nullable = false, unique = true)
    private String planNo;

    @Column(name = "plan_version", nullable = false)
    private Integer version;

    private String status;
    private Double totalCargoWeight;
    private Double displacement;
    private Double kg;
    private Double lcg;
    private Double tcg;
    private Double gm;
    private String complianceStatus;
    private Integer warningCount;

    @Column(columnDefinition = "TEXT")
    private String remark;
}

