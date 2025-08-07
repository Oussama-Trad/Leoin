package com.leoni.models;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.DBRef;
import org.springframework.data.mongodb.core.mapping.Document;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

@Data
@Document(collection = "users")
public class User {
    @Id
    private String id;
    
    private String firstName;
    private String lastName;
    private String email; // Primary email address (matching MongoDB field)
    private String parentalEmail; // Parental email address (matching MongoDB field)
    private String adresse1; // Alternative email field (backward compatibility)
    private String adresse2; // Alternative parental email field (backward compatibility)
    private String phoneNumber;
    private String parentalPhoneNumber;
    private String password;
    private String employeeId;
    private String department; // Department name as string
    private String departmentRef; // Reference to Department ObjectId
    private String departmentId; // Department ID field
    private String location; // Location name as string
    private String locationRef; // Reference to Location ObjectId
    private String position = "Non spécifié";
    private String status = "approved"; // Default status for existing users
    
    // This creates a reference to the user's documents
    // We'll use manual references instead of DBRef for better control
    private List<String> documentRequestIds = new ArrayList<>();
    
    private Date createdAt;
    private Date updatedAt;
    
    // Helper method to add a document reference
    public void addDocumentRequest(String docId) {
        if (this.documentRequestIds == null) {
            this.documentRequestIds = new ArrayList<>();
        }
        this.documentRequestIds.add(docId);
    }
    
    // Helper method for department name (for backward compatibility)
    public String getDepartmentName() {
        return this.department;
    }
    
    // Helper method for location name
    public String getLocationName() {
        return this.location;
    }
    
    // Getters and setters for backward compatibility
    public String getAdresse1() {
        return adresse1 != null ? adresse1 : email;
    }
    
    public void setAdresse1(String adresse1) {
        this.adresse1 = adresse1;
    }
    
    public String getAdresse2() {
        return adresse2 != null ? adresse2 : parentalEmail;
    }
    
    public void setAdresse2(String adresse2) {
        this.adresse2 = adresse2;
    }
    
    public String getDepartmentId() {
        return departmentId != null ? departmentId : departmentRef;
    }
    
    public void setDepartmentId(String departmentId) {
        this.departmentId = departmentId;
    }
}