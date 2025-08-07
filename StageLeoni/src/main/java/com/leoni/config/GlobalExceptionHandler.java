package com.leoni.config;

import com.leoni.exceptions.AdminServiceException;
import com.leoni.exceptions.DocumentRequestNotFoundException;
import com.leoni.exceptions.DuplicateUserException;
import com.leoni.exceptions.InvalidStatusException;
import com.leoni.exceptions.UserNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {
    
    /**
     * Handle UserNotFoundException
     */
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleUserNotFoundException(
            UserNotFoundException ex, WebRequest request) {
        
        Map<String, Object> errorDetails = createErrorResponse(
            HttpStatus.NOT_FOUND.value(),
            ex.getMessage(),
            ex.getErrorCode(),
            request.getDescription(false)
        );
        
        return new ResponseEntity<>(errorDetails, HttpStatus.NOT_FOUND);
    }
    
    /**
     * Handle DocumentRequestNotFoundException
     */
    @ExceptionHandler(DocumentRequestNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleDocumentRequestNotFoundException(
            DocumentRequestNotFoundException ex, WebRequest request) {
        
        Map<String, Object> errorDetails = createErrorResponse(
            HttpStatus.NOT_FOUND.value(),
            ex.getMessage(),
            ex.getErrorCode(),
            request.getDescription(false)
        );
        
        return new ResponseEntity<>(errorDetails, HttpStatus.NOT_FOUND);
    }
    
    /**
     * Handle DuplicateUserException
     */
    @ExceptionHandler(DuplicateUserException.class)
    public ResponseEntity<Map<String, Object>> handleDuplicateUserException(
            DuplicateUserException ex, WebRequest request) {
        
        Map<String, Object> errorDetails = createErrorResponse(
            HttpStatus.CONFLICT.value(),
            ex.getMessage(),
            ex.getErrorCode(),
            request.getDescription(false)
        );
        
        return new ResponseEntity<>(errorDetails, HttpStatus.CONFLICT);
    }
    
    /**
     * Handle InvalidStatusException
     */
    @ExceptionHandler(InvalidStatusException.class)
    public ResponseEntity<Map<String, Object>> handleInvalidStatusException(
            InvalidStatusException ex, WebRequest request) {
        
        Map<String, Object> errorDetails = createErrorResponse(
            HttpStatus.BAD_REQUEST.value(),
            ex.getMessage(),
            ex.getErrorCode(),
            request.getDescription(false)
        );
        
        return new ResponseEntity<>(errorDetails, HttpStatus.BAD_REQUEST);
    }
    
    /**
     * Handle general AdminServiceException
     */
    @ExceptionHandler(AdminServiceException.class)
    public ResponseEntity<Map<String, Object>> handleAdminServiceException(
            AdminServiceException ex, WebRequest request) {
        
        Map<String, Object> errorDetails = createErrorResponse(
            HttpStatus.INTERNAL_SERVER_ERROR.value(),
            ex.getMessage(),
            ex.getErrorCode(),
            request.getDescription(false)
        );
        
        return new ResponseEntity<>(errorDetails, HttpStatus.INTERNAL_SERVER_ERROR);
    }
    
    /**
     * Handle IllegalArgumentException
     */
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> handleIllegalArgumentException(
            IllegalArgumentException ex, WebRequest request) {
        
        Map<String, Object> errorDetails = createErrorResponse(
            HttpStatus.BAD_REQUEST.value(),
            "Paramètre invalide: " + ex.getMessage(),
            "INVALID_ARGUMENT",
            request.getDescription(false)
        );
        
        return new ResponseEntity<>(errorDetails, HttpStatus.BAD_REQUEST);
    }
    
    /**
     * Handle NullPointerException
     */
    @ExceptionHandler(NullPointerException.class)
    public ResponseEntity<Map<String, Object>> handleNullPointerException(
            NullPointerException ex, WebRequest request) {
        
        Map<String, Object> errorDetails = createErrorResponse(
            HttpStatus.INTERNAL_SERVER_ERROR.value(),
            "Erreur interne: référence nulle",
            "NULL_POINTER_ERROR",
            request.getDescription(false)
        );
        
        return new ResponseEntity<>(errorDetails, HttpStatus.INTERNAL_SERVER_ERROR);
    }
    
    /**
     * Handle all other exceptions
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGlobalException(
            Exception ex, WebRequest request) {
        
        Map<String, Object> errorDetails = createErrorResponse(
            HttpStatus.INTERNAL_SERVER_ERROR.value(),
            "Erreur interne du serveur: " + ex.getMessage(),
            "INTERNAL_SERVER_ERROR",
            request.getDescription(false)
        );
        
        return new ResponseEntity<>(errorDetails, HttpStatus.INTERNAL_SERVER_ERROR);
    }
    
    /**
     * Create standardized error response
     */
    private Map<String, Object> createErrorResponse(int status, String message, 
                                                   String errorCode, String path) {
        Map<String, Object> errorDetails = new HashMap<>();
        errorDetails.put("timestamp", new Date());
        errorDetails.put("status", status);
        errorDetails.put("error", getStatusText(status));
        errorDetails.put("message", message);
        errorDetails.put("errorCode", errorCode);
        errorDetails.put("path", path);
        errorDetails.put("success", false);
        
        return errorDetails;
    }
    
    /**
     * Get status text from HTTP status code
     */
    private String getStatusText(int status) {
        switch (status) {
            case 400: return "Bad Request";
            case 401: return "Unauthorized";
            case 403: return "Forbidden";
            case 404: return "Not Found";
            case 409: return "Conflict";
            case 500: return "Internal Server Error";
            default: return "Unknown Error";
        }
    }
}