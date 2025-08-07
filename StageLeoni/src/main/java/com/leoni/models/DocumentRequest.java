package com.leoni.models;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import java.util.Date;
import java.util.List;

@Data
@Document(collection = "document_requests")
public class DocumentRequest {
    @Id
    private String id;
    
    // Stores reference to the user
    private String userId;
    
    private List<String> documentTypes; // Changed from String to List<String>
    private String documentType; // Keep for backward compatibility with old data
    private String description;
    
    private Status status;
    private Date createdAt;
    private Date updatedAt;
    
    // Helper method to get document types (handles both old and new format)
    public List<String> getEffectiveDocumentTypes() {
        if (documentTypes != null && !documentTypes.isEmpty()) {
            return documentTypes;
        } else if (documentType != null && !documentType.isEmpty()) {
            return List.of(documentType);
        } else {
            return List.of("Unknown Type");
        }
    }

    @Data
    public static class Status {
        private String current = "en attente"; // Default status
        private List<ProgressStep> progress;
        
        public Status() {
            // Initialize default progress steps
            this.progress = List.of(
                new ProgressStep("en attente"),
                new ProgressStep("en cours"),
                new ProgressStep("accepté"),
                new ProgressStep("refusé")
            );
        }
    }

    @Data
    public static class ProgressStep {
        private String step;
        private Date date;
        private boolean completed = false;
        
        public ProgressStep(String step) {
            this.step = step;
            if ("en attente".equals(step)) {
                this.completed = true; // First step is completed by default
            }
        }
    }
}