package com.leoni.models;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.index.Indexed;

import java.time.LocalDateTime;

@Document(collection = "admins")
public class Admin {
    @Id
    private String id;
    
    @Indexed(unique = true)
    private String username;
    
    private String password;
    
    private String departmentId;
    
    // Add location and department fields for direct string comparison
    private String location;
    private String department;
    
    private String role = "ADMIN";
    
    private boolean active = true;
    
    private LocalDateTime createdAt;
    
    private LocalDateTime updatedAt;
    
    // Constructors
    public Admin() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
    
    public Admin(String username, String password, String departmentId) {
        this();
        this.username = username;
        this.password = password;
        this.departmentId = departmentId;
    }
    
    // Getters and Setters
    public String getId() {
        return id;
    }
    
    public void setId(String id) {
        this.id = id;
    }
    
    public String getUsername() {
        return username;
    }
    
    public void setUsername(String username) {
        this.username = username;
    }
    
    public String getPassword() {
        return password;
    }
    
    public void setPassword(String password) {
        this.password = password;
    }
    
    public String getDepartmentId() {
        return departmentId;
    }
    
    public void setDepartmentId(String departmentId) {
        this.departmentId = departmentId;
    }
    
    public String getLocation() {
        return location;
    }
    
    public void setLocation(String location) {
        this.location = location;
    }
    
    public String getDepartment() {
        return department;
    }
    
    public void setDepartment(String department) {
        this.department = department;
    }
    
    public String getRole() {
        return role;
    }
    
    public void setRole(String role) {
        this.role = role;
    }
    
    public boolean isActive() {
        return active;
    }
    
    public void setActive(boolean active) {
        this.active = active;
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    
    @Override
    public String toString() {
        return "Admin{" +
                "id='" + id + '\'' +
                ", username='" + username + '\'' +
                ", departmentId='" + departmentId + '\'' +
                ", role='" + role + '\'' +
                ", active=" + active +
                ", createdAt=" + createdAt +
                ", updatedAt=" + updatedAt +
                '}';
    }
}
