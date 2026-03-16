package com.stowage.system.exception;

import com.stowage.system.common.ApiResponse;
import jakarta.validation.ConstraintViolationException;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.orm.jpa.JpaSystemException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Locale;
import java.util.Optional;
import java.util.stream.Collectors;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NotFoundException.class)
    public ResponseEntity<ApiResponse<Void>> handleNotFound(NotFoundException exception) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(ApiResponse.failure(exception.getMessage(), null));
    }

    @ExceptionHandler(BadRequestException.class)
    public ResponseEntity<ApiResponse<Void>> handleBadRequest(BadRequestException exception) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(ApiResponse.failure(exception.getMessage(), null));
    }

    @ExceptionHandler({
        DataIntegrityViolationException.class,
        JpaSystemException.class,
        org.hibernate.exception.ConstraintViolationException.class
    })
    public ResponseEntity<ApiResponse<Void>> handlePersistenceConflict(Exception exception) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
            .body(ApiResponse.failure(mapConstraintMessage(extractDeepestMessage(exception)), null));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<String>> handleValidation(MethodArgumentNotValidException exception) {
        String message = exception.getBindingResult()
            .getFieldErrors()
            .stream()
            .map(FieldError::getDefaultMessage)
            .collect(Collectors.joining("; "));
        return ResponseEntity.badRequest().body(ApiResponse.failure(message, null));
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ApiResponse<Void>> handleConstraintViolation(ConstraintViolationException exception) {
        return ResponseEntity.badRequest().body(ApiResponse.failure(exception.getMessage(), null));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGeneric(Exception exception) {
        String rawMessage = extractDeepestMessage(exception);
        if (looksLikeConstraintViolation(rawMessage)) {
            return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(ApiResponse.failure(mapConstraintMessage(rawMessage), null));
        }
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(ApiResponse.failure(rawMessage, null));
    }

    private String extractDeepestMessage(Throwable throwable) {
        Throwable current = throwable;
        String fallback = Optional.ofNullable(throwable)
            .map(Throwable::getMessage)
            .orElse("Request failed");
        while (current != null) {
            if (current.getMessage() != null && !current.getMessage().isBlank()) {
                fallback = current.getMessage();
            }
            current = current.getCause();
        }
        return fallback;
    }

    private boolean looksLikeConstraintViolation(String rawMessage) {
        String lower = rawMessage == null ? "" : rawMessage.toLowerCase(Locale.ROOT);
        return lower.contains("unique index or primary key violation")
            || lower.contains("duplicate key")
            || lower.contains("primary key")
            || lower.contains("unique constraint")
            || lower.contains("constraint [")
            || lower.contains("23505");
    }

    private String mapConstraintMessage(String rawMessage) {
        String lower = rawMessage == null ? "" : rawMessage.toLowerCase(Locale.ROOT);
        if (lower.contains("ship_code")) {
            return "Ship code already exists. Please use a different shipCode.";
        }
        if (lower.contains("cargo_code")) {
            return "Cargo code already exists. Please use a different cargoCode.";
        }
        if (lower.contains("voyage_no")) {
            return "Voyage number already exists. Please use a different voyageNo.";
        }
        if (lower.contains("plan_no")) {
            return "Plan number already exists. Please use a different planNo.";
        }
        if (lower.contains("uk_hold_ship_no") || (lower.contains("hold_no") && lower.contains("ship_id"))) {
            return "Hold number already exists for this ship. Please use a different holdNo.";
        }
        if (lower.contains("stowage_plan") && lower.contains("primary key")) {
            return "Demo plan primary key collided. Restart the demo backend once and it will self-heal.";
        }
        return "Save failed because a unique key already exists.";
    }
}
