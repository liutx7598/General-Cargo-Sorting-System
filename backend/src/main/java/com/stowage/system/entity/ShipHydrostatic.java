package com.stowage.system.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
@Table(name = "ship_hydrostatic")
public class ShipHydrostatic {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long shipId;

    private Double displacement;
    private Double kmValue;
    private Double draft;

    @Column(columnDefinition = "TEXT")
    private String note;
}

