package com.leoni.models;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.index.Indexed;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Document(collection = "superadmins")
public class SuperAdmin {
    @Id
    private String id;
    
    @Indexed(unique = true)
    private String username;
    
    private String password;
    private String email;
    private String firstName;
    private String lastName;
    
    private String role = "SUPERADMIN";
    
    // SuperAdmin permissions
    private List<String> permissions; // ALL_ADMINS, ALL_EMPLOYEES, ALL_NEWS, etc.
    
    private boolean active = true;
    
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private LocalDateTime lastLoginAt;
    
    // Constructors
    public SuperAdmin() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
    
    public SuperAdmin(String username, String password) {
        this();
        this.username = username;
        this.password = password;
    }
    
    public SuperAdmin(String username, String password, String email, String firstName, String lastName) {
        this();
        this.username = username;
        this.password = password;
        this.email = email;
        this.firstName = firstName;
        this.lastName = lastName;
    }
    
    // Helper methods
    public String getFullName() {
        return (firstName != null ? firstName : "") + " " + (lastName != null ? lastName : "");
    }
    
    public void updateLastLogin() {
        this.lastLoginAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
}
