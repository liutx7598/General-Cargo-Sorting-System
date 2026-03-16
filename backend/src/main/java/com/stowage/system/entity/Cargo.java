package com.stowage.system.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
@Table(name = "cargo")
public class Cargo {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "cargo_code", nullable = false, unique = true)
    private String cargoCode;

    @Column(name = "cargo_name", nullable = false)
    private String cargoName;

    @Column(name = "cargo_category", nullable = false)
    private String cargoCategory;

    @Column(name = "dangerous_class")
    private String dangerousClass;

    @Column(name = "incompatible_tags")
    private String incompatibleTags;

    @Column(name = "isolation_level")
    private Double isolationLevel;

    @Column(name = "segregation_code")
    private Integer segregationCode;

    private Double weight;
    private Double length;
    private Double width;
    private Double height;
    private Boolean stackable;
    private Boolean rotatable;
    @Column(name = "center_offset_x")
    private Double centerOffsetX;

    @Column(name = "center_offset_y")
    private Double centerOffsetY;

    @Column(name = "center_offset_z")
    private Double centerOffsetZ;

    @Column(columnDefinition = "TEXT")
    private String remark;
}
