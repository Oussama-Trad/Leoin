package com.leoni.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.util.Date;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AuthResponse {
    
    private boolean success;
    private String message;
    private String token;
    private String username;
    private String role; // ADMIN or SUPERADMIN
    private String userId; // ID of the admin or superadmin
    private String location; // For admin users
    private String department; // For admin users
    
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date loginTime;
    
    // Constructor for successful authentication
    public AuthResponse(boolean success, String message, String token, String username) {
        this.success = success;
        this.message = message;
        this.token = token;
        this.username = username;
        this.loginTime = new Date();
    }
    
    // Constructor for failed authentication
    public AuthResponse(boolean success, String message) {
        this.success = success;
        this.message = message;
        this.loginTime = new Date();
    }
    
    // Static factory methods for common responses
    public static AuthResponse success(String token, String username) {
        return new AuthResponse(true, "Authentification réussie", token, username);
    }
    
    public static AuthResponse success(String message) {
        AuthResponse response = new AuthResponse(true, message);
        return response;
    }
    
    public static AuthResponse failure(String message) {
        return new AuthResponse(false, message);
    }
    
    public static AuthResponse invalidCredentials() {
        return new AuthResponse(false, "Nom d'utilisateur ou mot de passe incorrect");
    }
}