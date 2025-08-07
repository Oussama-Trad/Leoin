package com.leoni.models;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;

@Data
@Document(collection = "news")
public class News {
    @Id
    private String id;
    
    private String title;
    private String content;
    private String summary;
    private String category;
    private String priority; // normal, important, urgent
    
    // Image support
    private String imageUrl; // URL or path to the image
    private String imageName; // Original filename
    
    private Visibility visibility;
    
    // Backward compatibility with existing data
    private Boolean isActive; // For legacy data compatibility
    
    private String authorRef; // Reference to admin ID
    private String authorName; // Admin's username for display
    
    // Target fields - copied from admin's location and department
    private String targetLocation;
    private String targetDepartment;
    
    private LocalDateTime createdAt;
    private LocalDateTime publishedAt;
    private LocalDateTime updatedAt;
    
    // Constructors
    public News() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.visibility = new Visibility();
    }
    
    public News(String title, String content, String summary, String category, String priority) {
        this();
        this.title = title;
        this.content = content;
        this.summary = summary;
        this.category = category;
        this.priority = priority;
    }
    
    @Data
    public static class Visibility {
        private String status = "draft"; // draft, published, archived
        
        public Visibility() {}
        
        public Visibility(String status) {
            this.status = status;
        }
    }
    
    // Helper methods
    public boolean isPublished() {
        // Check new format first
        if (visibility != null && visibility.getStatus() != null) {
            return "published".equals(visibility.getStatus());
        }
        // Fallback to legacy format
        return Boolean.TRUE.equals(isActive);
    }
    
    public void publish() {
        this.visibility.setStatus("published");
        this.publishedAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
    
    public void archive() {
        this.visibility.setStatus("archived");
        this.updatedAt = LocalDateTime.now();
    }
}
