package com.leoni.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdateStatusRequest {
    
    private String documentId;
    private String newStatus;
    private String comment; // Optional comment for status change
    
    // Constructor without comment
    public UpdateStatusRequest(String documentId, String newStatus) {
        this.documentId = documentId;
        this.newStatus = newStatus;
    }
    
    // Validation method to check if status is valid
    public boolean isValidStatus() {
        if (newStatus == null) {
            return false;
        }
        
        return newStatus.equals("en attente") || 
               newStatus.equals("en cours") || 
               newStatus.equals("accepté") || 
               newStatus.equals("refusé");
    }
    
    // Helper method to check if status is final
    public boolean isFinalStatus() {
        return "accepté".equals(newStatus) || "refusé".equals(newStatus);
    }
}