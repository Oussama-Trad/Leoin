package com.leoni.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.util.Date;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DocumentRequestDTO {
    
    private String id;
    private String userId;
    private List<String> documentTypes; // Changed from String to List<String>
    private String description;
    private StatusDTO status;
    
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date createdAt;
    
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date updatedAt;
    
    // User information for display purposes
    private String userFullName;
    private String userEmail;
    private String userEmployeeId;
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class StatusDTO {
        private String current;
        private List<ProgressStepDTO> progress;
    }
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ProgressStepDTO {
        private String step;
        
        @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
        private Date date;
        
        private boolean completed;
    }
    
    // Constructor without user details (for basic document request info)
    public DocumentRequestDTO(String id, String userId, List<String> documentTypes, 
                             String description, StatusDTO status, Date createdAt, Date updatedAt) {
        this.id = id;
        this.userId = userId;
        this.documentTypes = documentTypes;
        this.description = description;
        this.status = status;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
    
    // Helper method to get current status
    public String getCurrentStatus() {
        return status != null ? status.getCurrent() : "en attente";
    }
    
    // Helper method to check if document is completed
    public boolean isCompleted() {
        String currentStatus = getCurrentStatus();
        return "accepté".equals(currentStatus) || "refusé".equals(currentStatus);
    }
    
    // Helper method to check if document is pending
    public boolean isPending() {
        return "en attente".equals(getCurrentStatus());
    }
    
    // Helper method to check if document is in progress
    public boolean isInProgress() {
        return "en cours".equals(getCurrentStatus());
    }
}