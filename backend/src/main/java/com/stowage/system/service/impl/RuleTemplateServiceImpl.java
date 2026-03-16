package com.stowage.system.service.impl;

import com.stowage.system.dto.RuleTemplateDtos;
import com.stowage.system.entity.RuleTemplate;
import com.stowage.system.exception.NotFoundException;
import com.stowage.system.repository.RuleTemplateRepository;
import com.stowage.system.service.RuleTemplateService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class RuleTemplateServiceImpl implements RuleTemplateService {

    private final RuleTemplateRepository ruleTemplateRepository;

    @Override
    public List<RuleTemplateRecord> listRules() {
        return ruleTemplateRepository.findAll().stream()
            .map(rule -> new RuleTemplateRecord(
                rule.getId(),
                rule.getRuleCode(),
                rule.getRuleName(),
                rule.getRuleType(),
                rule.getExpressionJson(),
                rule.getSeverity(),
                rule.getEnabled()
            ))
            .toList();
    }

    @Override
    @Transactional
    public RuleTemplateRecord saveRule(RuleTemplateDtos.RuleTemplateUpsertRequest request) {
        RuleTemplate rule = request.id() == null ? new RuleTemplate() : ruleTemplateRepository.findById(request.id())
            .orElseThrow(() -> new NotFoundException("规则不存在: " + request.id()));
        rule.setRuleCode(request.ruleCode());
        rule.setRuleName(request.ruleName());
        rule.setRuleType(request.ruleType());
        rule.setExpressionJson(request.expressionJson());
        rule.setSeverity(request.severity());
        rule.setEnabled(request.enabled());
        RuleTemplate saved = ruleTemplateRepository.save(rule);
        return new RuleTemplateRecord(
            saved.getId(),
            saved.getRuleCode(),
            saved.getRuleName(),
            saved.getRuleType(),
            saved.getExpressionJson(),
            saved.getSeverity(),
            saved.getEnabled()
        );
    }
}

