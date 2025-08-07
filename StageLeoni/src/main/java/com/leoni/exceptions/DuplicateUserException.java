package com.leoni.exceptions;

/**
 * Exception thrown when trying to create a user that already exists
 */
public class DuplicateUserException extends AdminServiceException {
    
    public DuplicateUserException(String field, String value) {
        super("Un utilisateur avec " + field + " '" + value + "' existe déjà", "DUPLICATE_USER");
    }
    
    public DuplicateUserException(String message) {
        super(message, "DUPLICATE_USER");
    }
}