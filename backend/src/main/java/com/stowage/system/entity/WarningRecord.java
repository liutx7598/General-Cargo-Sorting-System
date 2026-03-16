package com.stowage.system.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
@Table(name = "warning_record")
public class WarningRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long planId;

    private Long cargoId;
    private Long holdId;
    private String warningType;

    @Column(columnDefinition = "TEXT")
    private String warningMessage;

    private String severity;
    private Boolean resolved;
}

