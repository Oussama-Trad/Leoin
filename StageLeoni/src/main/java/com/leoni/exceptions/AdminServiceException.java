package com.leoni.exceptions;

/**
 * Base exception class for the admin service
 */
public class AdminServiceException extends RuntimeException {
    
    private final String errorCode;
    
    public AdminServiceException(String message) {
        super(message);
        this.errorCode = "ADMIN_SERVICE_ERROR";
    }
    
    public AdminServiceException(String message, String errorCode) {
        super(message);
        this.errorCode = errorCode;
    }
    
    public AdminServiceException(String message, Throwable cause) {
        super(message, cause);
        this.errorCode = "ADMIN_SERVICE_ERROR";
    }
    
    public AdminServiceException(String message, String errorCode, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
    }
    
    public String getErrorCode() {
        return errorCode;
    }
}