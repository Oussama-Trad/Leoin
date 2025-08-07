package com.leoni.exceptions;

/**
 * Exception thrown when a document request is not found
 */
public class DocumentRequestNotFoundException extends AdminServiceException {
    
    public DocumentRequestNotFoundException(String documentId) {
        super("Demande de document non trouvée avec l'ID: " + documentId, "DOCUMENT_NOT_FOUND");
    }
    
    public DocumentRequestNotFoundException(String userId, String documentType) {
        super("Aucune demande de document de type '" + documentType + "' trouvée pour l'utilisateur: " + userId, "DOCUMENT_NOT_FOUND");
    }
}