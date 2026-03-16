package com.stowage.system.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
@Table(name = "stowage_item")
public class StowageItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long planId;

    @Column(nullable = false)
    private Long cargoId;

    @Column(nullable = false)
    private Long holdId;

    private Integer layerNo;
    private String orientation;
    private Double originX;
    private Double originY;
    private Double originZ;
    private Double placedLength;
    private Double placedWidth;
    private Double placedHeight;
    private Double centroidX;
    private Double centroidY;
    private Double centroidZ;
    private String status;

    @Column(columnDefinition = "TEXT")
    private String violationFlags;
}

