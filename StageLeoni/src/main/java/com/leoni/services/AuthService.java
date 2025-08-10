package com.leoni.services;

import com.leoni.dto.AuthRequest;
import com.leoni.dto.AuthResponse;
import com.leoni.models.Admin;
import com.leoni.models.SuperAdmin;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Optional;
import java.util.UUID;
import jakarta.servlet.http.HttpServletRequest;

@Service
public class AuthService {
    
    @Autowired
    private AdminService adminService;
    
    @Autowired
    private SuperAdminService superAdminService;
    
    // Simple hardcoded admin credentials as fallback
    private static final String ADMIN_USERNAME = "admin";
    private static final String ADMIN_PASSWORD = "admin";
    
    /**
     * Authenticate user (admin or superadmin)
     * @param authRequest the authentication request
     * @return AuthResponse with authentication result and role information
     */
    public AuthResponse authenticate(AuthRequest authRequest) {
        if (authRequest == null || authRequest.getUsername() == null || authRequest.getPassword() == null) {
            return AuthResponse.failure("Nom d'utilisateur et mot de passe requis");
        }
        
        String username = authRequest.getUsername();
        String password = authRequest.getPassword();
        
        // First, try to authenticate as SuperAdmin
        System.out.println("Trying SuperAdmin authentication for username: " + username);
        Optional<SuperAdmin> superAdmin = superAdminService.authenticate(username, password);
        if (superAdmin.isPresent()) {
            System.out.println("SuperAdmin found: " + superAdmin.get().getUsername() + ", ID: " + superAdmin.get().getId());
            String token = generateToken("SUPERADMIN", superAdmin.get().getId());
            System.out.println("Generated token: " + token);
            AuthResponse response = AuthResponse.success(token, username);
            response.setRole("SUPERADMIN");
            response.setUserId(superAdmin.get().getId());
            System.out.println("SuperAdmin authenticated successfully");
            return response;
        } else {
            System.out.println("SuperAdmin not found or authentication failed");
        }
        
        // Then, try to authenticate as Admin
        Optional<Admin> admin = adminService.findByUsername(username);
        if (admin.isPresent() && admin.get().getPassword().equals(password) && admin.get().isActive()) {
            String token = generateToken("ADMIN", admin.get().getId());
            AuthResponse response = AuthResponse.success(token, username);
            response.setRole("ADMIN");
            response.setUserId(admin.get().getId());
            response.setLocation(admin.get().getLocation());
            response.setDepartment(admin.get().getDepartment());
            response.setDepartmentId(admin.get().getDepartmentId());
            
            System.out.println("Admin authenticated - ID: " + admin.get().getId() + 
                             ", Location: " + admin.get().getLocation() + 
                             ", Department: " + admin.get().getDepartment());
            return response;
        }
        
        // Fallback to hardcoded admin credentials
        if (ADMIN_USERNAME.equals(username) && ADMIN_PASSWORD.equals(password)) {
            String token = generateToken("ADMIN", "fallback-admin");
            AuthResponse response = AuthResponse.success(token, ADMIN_USERNAME);
            response.setRole("ADMIN");
            response.setUserId("fallback-admin");
            return response;
        }
        
        return AuthResponse.invalidCredentials();
    }
    
    /**
     * Validate authentication token
     * @param token the token to validate
     * @return true if token is valid
     */
    public boolean validateToken(String token) {
        // Simple token validation (in production, implement proper JWT validation)
        if (token == null) {
            return false;
        }
        
        // Check if it's a proper token format
        if (token.startsWith("admin-token-") || token.startsWith("superadmin-token-")) {
            return true;
        }
        
        // Backward compatibility - accept "authenticated" as a valid token for now
        // This should be removed in production
        if ("authenticated".equals(token)) {
            return true;
        }
        
        return false;
    }
    
    /**
     * Extract username from token
     * @param token the authentication token
     * @return username if token is valid, null otherwise
     */
    public String getUsernameFromToken(String token) {
        if (validateToken(token)) {
            // For backward compatibility with simple tokens
            if ("authenticated".equals(token)) {
                return "admin"; // Default admin username
            }
            
            // Extract user ID from token and find the corresponding username
            String userId = getUserIdFromToken(token);
            if (userId != null) {
                if (token.startsWith("admin-token-")) {
                    if ("fallback-admin".equals(userId)) {
                        return "admin";
                    } else {
                        // Try to find admin by ID
                        Optional<Admin> admin = adminService.findById(userId);
                        if (admin.isPresent()) {
                            return admin.get().getUsername();
                        }
                    }
                } else if (token.startsWith("superadmin-token-")) {
                    // Try to find superadmin by ID
                    Optional<SuperAdmin> superAdmin = superAdminService.findById(userId);
                    if (superAdmin.isPresent()) {
                        return superAdmin.get().getUsername();
                    }
                }
            }
            
            // Fallback to default based on token type
            if (token.startsWith("admin-token-")) {
                return "admin";
            } else if (token.startsWith("superadmin-token-")) {
                return "superadmin";
            }
            
            return "user-from-token";
        }
        return null;
    }
    
    /**
     * Extract role from token
     * @param token the authentication token
     * @return role if token is valid, null otherwise
     */
    public String getRoleFromToken(String token) {
        if (token != null) {
            if (token.startsWith("superadmin-token-")) {
                return "SUPERADMIN";
            } else if (token.startsWith("admin-token-")) {
                return "ADMIN";
            } else if ("authenticated".equals(token)) {
                // Backward compatibility - default to ADMIN role
                return "ADMIN";
            }
        }
        return null;
    }
    
    /**
     * Extract user ID from token
     * @param token the authentication token
     * @return user ID if token is valid, null otherwise
     */
    public String getUserIdFromToken(String token) {
        if (validateToken(token)) {
            // Extract ID from token format: "admin-token-{userId}-{uuid}" or "superadmin-token-{userId}-{uuid}"
            String[] parts = token.split("-");
            if (parts.length >= 3) {
                return parts[2];
            }
        }
        return null;
    }
    
    /**
     * Logout user (invalidate token)
     * @param token the token to invalidate
     * @return true if logout successful
     */
    public boolean logout(String token) {
        // In a real implementation, you would add the token to a blacklist
        // For this simple implementation, we just return true
        return validateToken(token);
    }
    
    /**
     * Check if user is admin
     * @param username the username to check
     * @return true if user is admin
     */
    public boolean isAdmin(String username) {
        return ADMIN_USERNAME.equals(username) || adminService.findByUsername(username).isPresent();
    }
    
    /**
     * Check if user is superadmin
     * @param username the username to check
     * @return true if user is superadmin
     */
    public boolean isSuperAdmin(String username) {
        return superAdminService.findByUsername(username).isPresent();
    }
    
    /**
     * Generate a simple authentication token
     * @param role the user role (ADMIN or SUPERADMIN)
     * @param userId the user ID
     * @return generated token
     */
    private String generateToken(String role, String userId) {
        String prefix = "SUPERADMIN".equals(role) ? "superadmin-token-" : "admin-token-";
        return prefix + userId + "-" + UUID.randomUUID().toString();
    }
    
    /**
     * Get admin username (for configuration purposes)
     * @return admin username
     */
    public String getAdminUsername() {
        return ADMIN_USERNAME;
    }
    
    /**
     * Get the authenticated admin ID from the current context
     * This method should be used to get the current admin's ID from security context
     * @return the authenticated admin's ID, or null if not authenticated
     */
    public String getAuthenticatedAdminId() {
        // For now, we'll return a fallback admin ID
        // In a real implementation, this would extract from SecurityContext or JWT token
        return "fallback-admin";
    }

    /**
     * Extract authenticated admin ID from the HTTP request Authorization header.
     * Supports Bearer tokens generated by this service. Returns null if missing/invalid.
     */
    public String getAuthenticatedAdminId(HttpServletRequest request) {
        if (request == null) {
            return null;
        }
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return null;
        }
        String token = authHeader.substring(7);
        if (!validateToken(token)) {
            return null;
        }
        String userId = getUserIdFromToken(token);
        // Fallback for legacy "authenticated" token without embedded user id
        if (userId == null && "authenticated".equals(token)) {
            return "fallback-admin";
        }
        return userId;
    }
    
    /**
     * Get admin information from token
     * @param token the authentication token
     * @return Admin object if found, null otherwise
     */
    public Admin getAdminFromToken(String token) {
        if (!validateToken(token)) {
            return null;
        }
        
        String role = getRoleFromToken(token);
        if (!"ADMIN".equals(role)) {
            return null;
        }
        
        String userId = getUserIdFromToken(token);
        if (userId != null && !"fallback-admin".equals(userId)) {
            Optional<Admin> admin = adminService.findById(userId);
            if (admin.isPresent()) {
                return admin.get();
            }
        }
        
        // Try to find admin by username for fallback cases
        String username = getUsernameFromToken(token);
        if (username != null) {
            Optional<Admin> admin = adminService.findByUsername(username);
            if (admin.isPresent()) {
                return admin.get();
            }
        }
        
        return null;
    }
    
    /**
     * Get admin location from token
     * @param token the authentication token
     * @return admin location if found, null otherwise
     */
    public String getAdminLocationFromToken(String token) {
        Admin admin = getAdminFromToken(token);
        return admin != null ? admin.getLocation() : null;
    }
    
    /**
     * Get admin department from token
     * @param token the authentication token
     * @return admin department if found, null otherwise
     */
    public String getAdminDepartmentFromToken(String token) {
        Admin admin = getAdminFromToken(token);
        return admin != null ? admin.getDepartment() : null;
    }
    
    /**
     * Check if user is super admin from token
     * @param token the authentication token
     * @return true if user has SUPERADMIN role
     */
    public boolean isSuperAdminFromToken(String token) {
        return "SUPERADMIN".equals(getRoleFromToken(token));
    }
}
