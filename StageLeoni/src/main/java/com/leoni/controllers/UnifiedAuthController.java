package com.leoni.controllers;

import com.leoni.dto.LoginRequest;
import com.leoni.dto.AuthResponse;
import com.leoni.services.UnifiedAuthService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class UnifiedAuthController {
    
    private static final Logger logger = LoggerFactory.getLogger(UnifiedAuthController.class);
    
    @Autowired
    private UnifiedAuthService unifiedAuthService;
    
    /**
     * Login endpoint for both Admin and SuperAdmin
     */
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        logger.info("Login attempt for username: {}", request.getUsername());
        
        try {
            AuthResponse response = unifiedAuthService.authenticate(request);
            
            if (response.isSuccess()) {
                logger.info("Login successful for username: {} with role: {}", 
                    request.getUsername(), response.getRole());
                return ResponseEntity.ok(response);
            } else {
                logger.warn("Login failed for username: {}", request.getUsername());
                return ResponseEntity.status(401).body(response);
            }
            
        } catch (Exception e) {
            logger.error("Login error for username: {}", request.getUsername(), e);
            return ResponseEntity.status(500).body(
                AuthResponse.failure("Erreur interne du serveur")
            );
        }
    }
    
    /**
     * Validate token endpoint
     */
    @PostMapping("/validate")
    public ResponseEntity<Map<String, Object>> validateToken(@RequestParam String token) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            boolean isValid = unifiedAuthService.validateToken(token);
            
            if (isValid) {
                String username = unifiedAuthService.getUsernameFromToken(token);
                String role = unifiedAuthService.getRoleFromToken(token);
                String userId = unifiedAuthService.getUserIdFromToken(token);
                String department = unifiedAuthService.getDepartmentFromToken(token);
                String location = unifiedAuthService.getLocationFromToken(token);
                long expiresIn = unifiedAuthService.getTokenExpirationInMinutes(token);
                
                response.put("success", true);
                response.put("message", "Token valide");
                response.put("username", username);
                response.put("role", role);
                response.put("userId", userId);
                response.put("department", department);
                response.put("location", location);
                response.put("expiresInMinutes", expiresIn);
                
                return ResponseEntity.ok(response);
            } else {
                response.put("success", false);
                response.put("message", "Token invalide ou expiré");
                return ResponseEntity.status(401).body(response);
            }
            
        } catch (Exception e) {
            logger.error("Token validation error", e);
            response.put("success", false);
            response.put("message", "Erreur lors de la validation du token");
            return ResponseEntity.status(500).body(response);
        }
    }
    
    /**
     * Get current user info from token
     */
    @GetMapping("/me")
    public ResponseEntity<Map<String, Object>> getCurrentUser(
            @RequestHeader("Authorization") String authHeader) {
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            // Extract token from Bearer header
            String token = authHeader.replace("Bearer ", "");
            
            if (!unifiedAuthService.validateToken(token)) {
                response.put("success", false);
                response.put("message", "Token invalide");
                return ResponseEntity.status(401).body(response);
            }
            
            String username = unifiedAuthService.getUsernameFromToken(token);
            String role = unifiedAuthService.getRoleFromToken(token);
            String userId = unifiedAuthService.getUserIdFromToken(token);
            String department = unifiedAuthService.getDepartmentFromToken(token);
            String location = unifiedAuthService.getLocationFromToken(token);
            long expiresIn = unifiedAuthService.getTokenExpirationInMinutes(token);
            
            response.put("success", true);
            response.put("username", username);
            response.put("role", role);
            response.put("userId", userId);
            response.put("department", department);
            response.put("location", location);
            response.put("isSuperAdmin", "SUPERADMIN".equals(role));
            response.put("expiresInMinutes", expiresIn);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Error getting current user info", e);
            response.put("success", false);
            response.put("message", "Erreur lors de la récupération des informations utilisateur");
            return ResponseEntity.status(500).body(response);
        }
    }
    
    /**
     * Logout endpoint
     */
    @PostMapping("/logout")
    public ResponseEntity<Map<String, Object>> logout(
            @RequestHeader(value = "Authorization", required = false) String authHeader) {
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            String token = null;
            if (authHeader != null && authHeader.startsWith("Bearer ")) {
                token = authHeader.replace("Bearer ", "");
            }
            
            boolean success = unifiedAuthService.logout(token);
            
            response.put("success", success);
            response.put("message", success ? "Déconnexion réussie" : "Échec de la déconnexion");
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Logout error", e);
            response.put("success", false);
            response.put("message", "Erreur lors de la déconnexion");
            return ResponseEntity.status(500).body(response);
        }
    }
    
    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "Service d'authentification opérationnel");
        response.put("service", "UnifiedAuthController");
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.ok(response);
    }
    
    /**
     * Get authentication stats (for debugging)
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getAuthStats(
            @RequestHeader("Authorization") String authHeader) {
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!unifiedAuthService.validateToken(token)) {
                response.put("success", false);
                response.put("message", "Token invalide");
                return ResponseEntity.status(401).body(response);
            }
            
            // Only SuperAdmins can access stats
            if (!unifiedAuthService.isSuperAdmin(token)) {
                response.put("success", false);
                response.put("message", "Accès refusé - SuperAdmin requis");
                return ResponseEntity.status(403).body(response);
            }
            
            response.put("success", true);
            response.put("service", "UnifiedAuthService");
            response.put("tokenValidation", "JWT with 24h expiration");
            response.put("supportedRoles", new String[]{"ADMIN", "SUPERADMIN"});
            response.put("passwordSupport", "Plain text + BCrypt");
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Error getting auth stats", e);
            response.put("success", false);
            response.put("message", "Erreur lors de la récupération des statistiques");
            return ResponseEntity.status(500).body(response);
        }
    }
}
