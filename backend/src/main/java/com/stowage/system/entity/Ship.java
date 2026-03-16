package com.stowage.system.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
@Table(name = "ship")
public class Ship {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "ship_code", nullable = false, unique = true)
    private String shipCode;

    @Column(name = "ship_name", nullable = false)
    private String shipName;

    @Column(name = "ship_type", nullable = false)
    private String shipType;

    @Column(name = "length_overall")
    private Double lengthOverall;

    @Column(name = "length_between_perpendiculars")
    private Double lengthBetweenPerpendiculars;

    private Double beam;
    private Double depth;

    @Column(name = "lightship_weight")
    private Double lightshipWeight;

    @Column(name = "lightship_kg")
    private Double lightshipKG;

    @Column(name = "lightship_lcg")
    private Double lightshipLCG;

    @Column(name = "lightship_tcg")
    private Double lightshipTCG;

    @Column(name = "design_displacement")
    private Double designDisplacement;

    @Column(name = "design_gm")
    private Double designGM;

    @Column(columnDefinition = "TEXT")
    private String remark;
}
