package com.stowage.system.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public final class RuleTemplateDtos {

    private RuleTemplateDtos() {
    }

    public record RuleTemplateUpsertRequest(
        Long id,
        @NotBlank(message = "ruleCode 不能为空") String ruleCode,
        @NotBlank(message = "ruleName 不能为空") String ruleName,
        @NotBlank(message = "ruleType 不能为空") String ruleType,
        @NotBlank(message = "expressionJson 不能为空") String expressionJson,
        @NotBlank(message = "severity 不能为空") String severity,
        @NotNull(message = "enabled 不能为空") Boolean enabled
    ) {
    }
}

