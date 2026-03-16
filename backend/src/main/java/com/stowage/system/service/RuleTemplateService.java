package com.stowage.system.service;

import com.stowage.system.dto.RuleTemplateDtos;
import com.stowage.system.vo.ViewModels;

import java.util.List;

public interface RuleTemplateService {
    List<RuleTemplateRecord> listRules();
    RuleTemplateRecord saveRule(RuleTemplateDtos.RuleTemplateUpsertRequest request);

    record RuleTemplateRecord(
        Long id,
        String ruleCode,
        String ruleName,
        String ruleType,
        String expressionJson,
        String severity,
        Boolean enabled
    ) {
    }
}
