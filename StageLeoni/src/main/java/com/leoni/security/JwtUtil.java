package com.leoni.security;

import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Base64;

@Component
public class JwtUtil {
    
    private static final int TOKEN_VALIDITY_MINUTES = 24 * 60; // 24 hours
    
    // Simple in-memory token storage (for demonstration)
    private final Map<String, TokenInfo> activeTokens = new ConcurrentHashMap<>();
    
    // Generate token for user
    public String generateToken(String userId, String username, String role, String department, String location) {
        // Create a simple token with encoded data
        String tokenData = userId + "|" + username + "|" + role + "|" + 
                          (department != null ? department : "") + "|" + 
                          (location != null ? location : "") + "|" + 
                          System.currentTimeMillis();
        
        String token = "leoni_" + Base64.getEncoder().encodeToString(tokenData.getBytes()).replace("=", "") + "_" + UUID.randomUUID().toString().substring(0, 8);
        
        // Store token info
        TokenInfo tokenInfo = new TokenInfo(userId, username, role, department, location, LocalDateTime.now());
        activeTokens.put(token, tokenInfo);
        
        return token;
    }
    
    // Validate token
    public Boolean validateToken(String token) {
        if (token == null || token.trim().isEmpty()) {
            return false;
        }
        
        TokenInfo tokenInfo = activeTokens.get(token);
        if (tokenInfo == null) {
            return false;
        }
        
        // Check if token has expired
        if (tokenInfo.getCreatedAt().isBefore(LocalDateTime.now().minusMinutes(TOKEN_VALIDITY_MINUTES))) {
            activeTokens.remove(token);
            return false;
        }
        
        return true;
    }
    
    // Extract username from token
    public String getUsernameFromToken(String token) {
        TokenInfo tokenInfo = activeTokens.get(token);
        return tokenInfo != null ? tokenInfo.getUsername() : null;
    }
    
    // Extract user ID from token
    public String getUserIdFromToken(String token) {
        TokenInfo tokenInfo = activeTokens.get(token);
        return tokenInfo != null ? tokenInfo.getUserId() : null;
    }
    
    // Extract role from token
    public String getRoleFromToken(String token) {
        TokenInfo tokenInfo = activeTokens.get(token);
        return tokenInfo != null ? tokenInfo.getRole() : null;
    }
    
    // Extract department from token
    public String getDepartmentFromToken(String token) {
        TokenInfo tokenInfo = activeTokens.get(token);
        return tokenInfo != null ? tokenInfo.getDepartment() : null;
    }
    
    // Extract location from token
    public String getLocationFromToken(String token) {
        TokenInfo tokenInfo = activeTokens.get(token);
        return tokenInfo != null ? tokenInfo.getLocation() : null;
    }
    
    // Get token expiration time in minutes
    public long getTokenExpirationInMinutes(String token) {
        TokenInfo tokenInfo = activeTokens.get(token);
        if (tokenInfo == null) {
            return -1;
        }
        
        LocalDateTime expirationTime = tokenInfo.getCreatedAt().plusMinutes(TOKEN_VALIDITY_MINUTES);
        LocalDateTime now = LocalDateTime.now();
        
        if (now.isAfter(expirationTime)) {
            return 0; // Token expired
        }
        
        // Calculate remaining minutes
        return java.time.Duration.between(now, expirationTime).toMinutes();
    }
    
    // Refresh token (extend expiration)
    public String refreshToken(String token) {
        TokenInfo tokenInfo = activeTokens.get(token);
        if (tokenInfo == null) {
            return null;
        }
        
        // Remove old token
        activeTokens.remove(token);
        
        // Create new token with same data
        return generateToken(
            tokenInfo.getUserId(),
            tokenInfo.getUsername(),
            tokenInfo.getRole(),
            tokenInfo.getDepartment(),
            tokenInfo.getLocation()
        );
    }
    
    // Remove token (logout)
    public void removeToken(String token) {
        activeTokens.remove(token);
    }
    
    // Inner class to store token information
    private static class TokenInfo {
        private final String userId;
        private final String username;
        private final String role;
        private final String department;
        private final String location;
        private final LocalDateTime createdAt;
        
        public TokenInfo(String userId, String username, String role, String department, String location, LocalDateTime createdAt) {
            this.userId = userId;
            this.username = username;
            this.role = role;
            this.department = department;
            this.location = location;
            this.createdAt = createdAt;
        }
        
        public String getUserId() {
            return userId;
        }
        
        public String getUsername() {
            return username;
        }
        
        public String getRole() {
            return role;
        }
        
        public String getDepartment() {
            return department;
        }
        
        public String getLocation() {
            return location;
        }
        
        public LocalDateTime getCreatedAt() {
            return createdAt;
        }
    }
}
