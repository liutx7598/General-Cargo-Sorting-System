package com.stowage.system.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
@Entity
@Table(name = "voyage")
public class Voyage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String voyageNo;

    @Column(nullable = false)
    private Long shipId;

    private String routeInfo;
    private String departurePort;
    private String arrivalPort;
    private LocalDateTime eta;
    private LocalDateTime etd;
    private String status;
}

