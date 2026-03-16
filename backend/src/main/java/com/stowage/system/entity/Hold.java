package com.stowage.system.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
@Table(name = "hold")
public class Hold {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long shipId;

    @Column(nullable = false)
    private String holdNo;

    private Double length;
    private Double width;
    private Double height;
    private Double volume;
    private Double lcg;
    private Double tcg;
    private Double vcg;
    private Double maxLoadWeight;
    private Double deckStrengthLimit;
    private Integer sequenceNo;

    @Column(columnDefinition = "TEXT")
    private String remark;
}

