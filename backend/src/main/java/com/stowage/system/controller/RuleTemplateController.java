package com.stowage.system.controller;

import com.stowage.system.common.ApiResponse;
import com.stowage.system.dto.RuleTemplateDtos;
import com.stowage.system.service.RuleTemplateService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/rules")
@RequiredArgsConstructor
public class RuleTemplateController {

    private final RuleTemplateService ruleTemplateService;

    @GetMapping
    public ApiResponse<List<RuleTemplateService.RuleTemplateRecord>> listRules() {
        return ApiResponse.success(ruleTemplateService.listRules());
    }

    @PostMapping
    public ApiResponse<RuleTemplateService.RuleTemplateRecord> saveRule(
        @Valid @RequestBody RuleTemplateDtos.RuleTemplateUpsertRequest request
    ) {
        return ApiResponse.success("规则保存成功", ruleTemplateService.saveRule(request));
    }
}

