package com.leoni.controllers;

import com.leoni.dto.AuthRequest;
import com.leoni.dto.AuthResponse;
import com.leoni.models.Admin;
import com.leoni.models.SuperAdmin;
import com.leoni.services.AuthService;
import com.leoni.services.AdminService;
import com.leoni.services.SuperAdminService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class AuthController {
    
    @Autowired
    private AuthService authService;
    
    @Autowired
    private AdminService adminService;
    
    @Autowired
    private SuperAdminService superAdminService;
    
    /**
     * Admin login endpoint for React frontend
     * @param authRequest the authentication request
     * @return AuthResponse with authentication result
     */
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@RequestBody AuthRequest authRequest) {
        System.out.println("=== ADMIN LOGIN ENDPOINT CALLED ===");
        System.out.println("AuthRequest received: " + authRequest);
        System.out.println("Username: " + (authRequest != null ? authRequest.getUsername() : "null"));
        
        try {
            // Simple admin authentication
            if (authRequest == null || authRequest.getUsername() == null || authRequest.getPassword() == null) {
                return ResponseEntity.status(400).body(
                    AuthResponse.failure("Username and password are required")
                );
            }
            
            // Try to authenticate with AdminService first
            Optional<Admin> admin = adminService.authenticateAdmin(authRequest.getUsername(), authRequest.getPassword());
            if (admin.isPresent()) {
                // Use AuthService to properly authenticate and get a valid token
                AuthResponse response = authService.authenticate(authRequest);
                System.out.println("Admin authenticated, returning: " + response);
                return ResponseEntity.ok(response);
            }
            
            // Try to authenticate as SuperAdmin
            Optional<SuperAdmin> superAdmin = superAdminService.authenticate(authRequest.getUsername(), authRequest.getPassword());
            if (superAdmin.isPresent()) {
                // Create response for SuperAdmin
                AuthResponse response = new AuthResponse(
                    true,
                    "Authentication successful",
                    "superadmin-token-" + System.currentTimeMillis(),
                    authRequest.getUsername()
                );
                response.setRole("SUPERADMIN");
                response.setUserId(superAdmin.get().getId());
                System.out.println("SuperAdmin authenticated, returning: " + response);
                return ResponseEntity.ok(response);
            }
            
            // Fallback to hardcoded admin credentials for backward compatibility
            if ("admin".equals(authRequest.getUsername()) && "admin".equals(authRequest.getPassword())) {
                // Use AuthService for consistent token generation
                AuthResponse response = authService.authenticate(authRequest);
                System.out.println("Fallback admin authenticated, returning: " + response);
                return ResponseEntity.ok(response);
            } else {
                return ResponseEntity.status(401).body(
                    AuthResponse.failure("Invalid credentials")
                );
            }
        } catch (Exception e) {
            System.out.println("Exception in login: " + e.getClass().getSimpleName() + " - " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(
                AuthResponse.failure("Erreur interne du serveur: " + e.getMessage())
            );
        }
    }
    
    /**
     * Validate token endpoint
     * @param token the token to validate
     * @return validation result
     */
    @PostMapping("/validate")
    public ResponseEntity<AuthResponse> validateToken(@RequestParam String token) {
        try {
            boolean isValid = authService.validateToken(token);
            
            if (isValid) {
                String username = authService.getUsernameFromToken(token);
                return ResponseEntity.ok(
                    new AuthResponse(true, "Token valide", token, username)
                );
            } else {
                return ResponseEntity.status(401).body(
                    AuthResponse.failure("Token invalide ou expiré")
                );
            }
        } catch (Exception e) {
            return ResponseEntity.status(500).body(
                AuthResponse.failure("Erreur lors de la validation du token: " + e.getMessage())
            );
        }
    }
    
    /**
     * Logout endpoint
     * @param token the token to invalidate
     * @return logout result
     */
    @PostMapping("/logout")
    public ResponseEntity<AuthResponse> logout(@RequestParam String token) {
        try {
            boolean logoutSuccess = authService.logout(token);
            
            if (logoutSuccess) {
                return ResponseEntity.ok(
                    new AuthResponse(true, "Déconnexion réussie")
                );
            } else {
                return ResponseEntity.status(400).body(
                    AuthResponse.failure("Échec de la déconnexion")
                );
            }
        } catch (Exception e) {
            return ResponseEntity.status(500).body(
                AuthResponse.failure("Erreur lors de la déconnexion: " + e.getMessage())
            );
        }
    }
    
    /**
     * Get current user info
     * @param token the authentication token
     * @return user information
     */
    @GetMapping("/me")
    public ResponseEntity<AuthResponse> getCurrentUser(@RequestParam String token) {
        try {
            String username = authService.getUsernameFromToken(token);
            
            if (username != null) {
                return ResponseEntity.ok(
                    new AuthResponse(true, "Utilisateur authentifié", token, username)
                );
            } else {
                return ResponseEntity.status(401).body(
                    AuthResponse.failure("Token invalide")
                );
            }
        } catch (Exception e) {
            return ResponseEntity.status(500).body(
                AuthResponse.failure("Erreur lors de la récupération des informations utilisateur: " + e.getMessage())
            );
        }
    }
    
    /**
     * Get current user info with role
     */
    @GetMapping("/user-info")
    public ResponseEntity<AuthResponse> getUserInfo(@RequestHeader("Authorization") String authHeader) {
        try {
            String token = authHeader.replace("Bearer ", "");
            String username = authService.getUsernameFromToken(token);
            String role = authService.getRoleFromToken(token);
            
            if (username != null && role != null) {
                AuthResponse response = new AuthResponse(true, "Informations utilisateur récupérées", token, username);
                response.setRole(role);
                return ResponseEntity.ok(response);
            } else {
                return ResponseEntity.status(401).body(
                    AuthResponse.failure("Token invalide")
                );
            }
        } catch (Exception e) {
            return ResponseEntity.status(500).body(
                AuthResponse.failure("Erreur lors de la récupération des informations utilisateur: " + e.getMessage())
            );
        }
    }
    
    /**
     * Health check endpoint
     * @return service status
     */
    @GetMapping("/health")
    public ResponseEntity<AuthResponse> healthCheck() {
        return ResponseEntity.ok(
            new AuthResponse(true, "Service d'authentification opérationnel")
        );
    }
    
    /**
     * Test endpoint for JSON deserialization
     */
    @PostMapping("/test")
    public ResponseEntity<String> testJson(@RequestBody AuthRequest authRequest) {
        System.out.println("=== TEST ENDPOINT CALLED ===");
        System.out.println("AuthRequest: " + authRequest);
        System.out.println("Username: " + (authRequest != null ? authRequest.getUsername() : "null"));
        System.out.println("Password: " + (authRequest != null ? authRequest.getPassword() : "null"));
        
        return ResponseEntity.ok("Test successful - Username: " +
            (authRequest != null ? authRequest.getUsername() : "null"));
    }
    
    /**
     * Test endpoint with simple DTO (no Lombok)
     */
    @PostMapping("/test-simple")
    public ResponseEntity<String> testSimpleJson(@RequestBody com.leoni.dto.SimpleAuthRequest authRequest) {
        System.out.println("=== SIMPLE TEST ENDPOINT CALLED ===");
        System.out.println("SimpleAuthRequest: " + authRequest);
        System.out.println("Username: " + (authRequest != null ? authRequest.getUsername() : "null"));
        System.out.println("Password: " + (authRequest != null ? authRequest.getPassword() : "null"));
        
        return ResponseEntity.ok("Simple test successful - Username: " +
            (authRequest != null ? authRequest.getUsername() : "null"));
    }
}