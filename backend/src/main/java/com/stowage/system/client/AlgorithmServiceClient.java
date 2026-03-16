package com.stowage.system.client;

import com.stowage.system.exception.BadRequestException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
@RequiredArgsConstructor
public class AlgorithmServiceClient {

    private final WebClient algorithmWebClient;

    public AlgorithmModels.SolverResponse generatePlan(AlgorithmModels.GeneratePlanPayload payload) {
        return algorithmWebClient.post()
            .uri("/api/solver/generate-plan")
            .bodyValue(payload)
            .retrieve()
            .bodyToMono(AlgorithmModels.SolverResponse.class)
            .blockOptional()
            .orElseThrow(() -> new BadRequestException("算法服务未返回生成结果"));
    }

    public AlgorithmModels.SolverResponse validatePlan(AlgorithmModels.ValidatePlanPayload payload) {
        return algorithmWebClient.post()
            .uri("/api/solver/validate-plan")
            .bodyValue(payload)
            .retrieve()
            .bodyToMono(AlgorithmModels.SolverResponse.class)
            .blockOptional()
            .orElseThrow(() -> new BadRequestException("算法服务未返回校验结果"));
    }
}

