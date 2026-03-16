package com.stowage.system.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
@Table(name = "rule_template")
public class RuleTemplate {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String ruleCode;

    @Column(nullable = false)
    private String ruleName;

    @Column(nullable = false)
    private String ruleType;

    @Column(columnDefinition = "TEXT")
    private String expressionJson;

    private String severity;
    private Boolean enabled;
}

