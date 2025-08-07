package com.leoni.exceptions;

/**
 * Exception thrown when a user is not found
 */
public class UserNotFoundException extends AdminServiceException {
    
    public UserNotFoundException(String userId) {
        super("Utilisateur non trouvé avec l'ID: " + userId, "USER_NOT_FOUND");
    }
    
    public UserNotFoundException(String field, String value) {
        super("Utilisateur non trouvé avec " + field + ": " + value, "USER_NOT_FOUND");
    }
}