package com.leoni.exceptions;

/**
 * Exception thrown when an invalid status update is attempted
 */
public class InvalidStatusException extends AdminServiceException {
    
    public InvalidStatusException(String message) {
        super(message, "INVALID_STATUS");
    }
    
    public static InvalidStatusException invalidTransition(String currentStatus, String newStatus) {
        return new InvalidStatusException("Impossible de changer le statut de '" + currentStatus + "' vers '" + newStatus + "'");
    }
    
    public static InvalidStatusException invalidStatus(String status) {
        return new InvalidStatusException("Statut invalide: " + status);
    }
}