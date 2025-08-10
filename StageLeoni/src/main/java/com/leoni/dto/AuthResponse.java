package com.leoni.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;

public class AuthResponse {
    
    private boolean success;
    private String message;
    private String token;
    private String username;
    private String role; // ADMIN or SUPERADMIN
    private String userId; // ID of the admin or superadmin
    private String location; // For admin users
    private String department; // For admin users
    private String departmentId; // For admin users - department ID
    private Long tokenExpirationMinutes; // Minutes until token expires
    
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date loginTime;
    
    // Constructeurs
    public AuthResponse() {
        this.loginTime = new Date();
    }
    
    public AuthResponse(boolean success, String message, String token, String username) {
        this.success = success;
        this.message = message;
        this.token = token;
        this.username = username;
        this.loginTime = new Date();
    }
    
    public AuthResponse(boolean success, String message) {
        this.success = success;
        this.message = message;
        this.loginTime = new Date();
    }
    
    // Getters et Setters
    public boolean isSuccess() {
        return success;
    }
    
    public void setSuccess(boolean success) {
        this.success = success;
    }
    
    public String getMessage() {
        return message;
    }
    
    public void setMessage(String message) {
        this.message = message;
    }
    
    public String getToken() {
        return token;
    }
    
    public void setToken(String token) {
        this.token = token;
    }
    
    public String getUsername() {
        return username;
    }
    
    public void setUsername(String username) {
        this.username = username;
    }
    
    public String getRole() {
        return role;
    }
    
    public void setRole(String role) {
        this.role = role;
    }
    
    public String getUserId() {
        return userId;
    }
    
    public void setUserId(String userId) {
        this.userId = userId;
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
    
    public String getDepartmentId() {
        return departmentId;
    }
    
    public void setDepartmentId(String departmentId) {
        this.departmentId = departmentId;
    }
    
    public Long getTokenExpirationMinutes() {
        return tokenExpirationMinutes;
    }
    
    public void setTokenExpirationMinutes(Long tokenExpirationMinutes) {
        this.tokenExpirationMinutes = tokenExpirationMinutes;
    }
    
    public Date getLoginTime() {
        return loginTime;
    }
    
    public void setLoginTime(Date loginTime) {
        this.loginTime = loginTime;
    }
    
    // Static factory methods for common responses
    public static AuthResponse success(String token, String username) {
        return new AuthResponse(true, "Authentification réussie", token, username);
    }
    
    public static AuthResponse success(String message) {
        return new AuthResponse(true, message);
    }
    
    public static AuthResponse failure(String message) {
        return new AuthResponse(false, message);
    }
    
    public static AuthResponse invalidCredentials() {
        return new AuthResponse(false, "Nom d'utilisateur ou mot de passe incorrect");
    }
}
