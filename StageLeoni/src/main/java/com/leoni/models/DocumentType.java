package com.leoni.models;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import java.util.Date;

@Data
@Document(collection = "document_types")
public class DocumentType {
    @Id
    private String id;
    
    private String name;
    private String description;
    private boolean active = true; // To enable/disable document types
    private Date createdAt;
    private Date updatedAt;
    
    public DocumentType() {
        this.createdAt = new Date();
        this.updatedAt = new Date();
    }
    
    public DocumentType(String name, String description) {
        this.name = name;
        this.description = description;
        this.createdAt = new Date();
        this.updatedAt = new Date();
    }
}
