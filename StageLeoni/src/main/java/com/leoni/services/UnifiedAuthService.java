package com.leoni.services;

import com.leoni.dto.LoginRequest;
import com.leoni.dto.AuthResponse;
import com.leoni.models.Admin;
import com.leoni.models.SuperAdmin;
import com.leoni.security.JwtUtil;
import com.leoni.repositories.AdminRepository;
import com.leoni.repositories.SuperAdminRepository;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class UnifiedAuthService {
    
    private static final Logger logger = LoggerFactory.getLogger(UnifiedAuthService.class);
    
    @Autowired
    private AdminRepository adminRepository;
    
    @Autowired
    private SuperAdminRepository superAdminRepository;
    
    @Autowired
    private JwtUtil jwtUtil;
    
    @Autowired(required = false)
    private PasswordEncoder passwordEncoder;
    
    /**
     * Unified authentication method for both Admin and SuperAdmin
     */
    public AuthResponse authenticate(LoginRequest request) {
        logger.info("Authentication attempt for username: {}", request.getUsername());
        
        try {
            // Validate input
            if (request.getUsername() == null || request.getPassword() == null || 
                request.getUsername().trim().isEmpty() || request.getPassword().trim().isEmpty()) {
                return AuthResponse.failure("Nom d'utilisateur et mot de passe requis");
            }
            
            String username = request.getUsername().trim();
            String password = request.getPassword().trim();
            
            // Try to authenticate as SuperAdmin first
            Optional<SuperAdmin> superAdmin = authenticateSuperAdmin(username, password);
            if (superAdmin.isPresent()) {
                return createAuthResponse(superAdmin.get());
            }
            
            // Try to authenticate as Admin
            Optional<Admin> admin = authenticateAdmin(username, password);
            if (admin.isPresent()) {
                return createAuthResponse(admin.get());
            }
            
            logger.warn("Authentication failed for username: {}", username);
            return AuthResponse.failure("Identifiants invalides");
            
        } catch (Exception e) {
            logger.error("Error during authentication for username: {}", request.getUsername(), e);
            return AuthResponse.failure("Erreur d'authentification");
        }
    }
    
    /**
     * Authenticate SuperAdmin
     */
    private Optional<SuperAdmin> authenticateSuperAdmin(String username, String password) {
        try {
            Optional<SuperAdmin> superAdminOpt = superAdminRepository.findByUsername(username);
            if (superAdminOpt.isPresent()) {
                SuperAdmin superAdmin = superAdminOpt.get();
                if (superAdmin.isActive() && verifyPassword(password, superAdmin.getPassword())) {
                    logger.info("SuperAdmin authenticated successfully: {}", username);
                    return superAdminOpt;
                }
            }
        } catch (Exception e) {
            logger.error("Error authenticating SuperAdmin: {}", username, e);
        }
        return Optional.empty();
    }
    
    /**
     * Authenticate Admin
     */
    private Optional<Admin> authenticateAdmin(String username, String password) {
        try {
            Optional<Admin> adminOpt = adminRepository.findByUsernameAndActiveTrue(username);
            if (adminOpt.isPresent()) {
                Admin admin = adminOpt.get();
                if (verifyPassword(password, admin.getPassword())) {
                    logger.info("Admin authenticated successfully: {}", username);
                    return adminOpt;
                }
            }
        } catch (Exception e) {
            logger.error("Error authenticating Admin: {}", username, e);
        }
        return Optional.empty();
    }
    
    /**
     * Verify password (with support for both hashed and plain passwords)
     */
    private boolean verifyPassword(String rawPassword, String encodedPassword) {
        if (passwordEncoder != null) {
            try {
                return passwordEncoder.matches(rawPassword, encodedPassword);
            } catch (Exception e) {
                logger.debug("Password encoder failed, trying plain text comparison");
            }
        }
        // Fallback to plain text comparison for existing data
        return rawPassword.equals(encodedPassword);
    }
    
    /**
     * Create AuthResponse for SuperAdmin
     */
    private AuthResponse createAuthResponse(SuperAdmin superAdmin) {
        String token = jwtUtil.generateToken(
            superAdmin.getId(),
            superAdmin.getUsername(),
            "SUPERADMIN",
            null,  // SuperAdmin has no specific department
            null   // SuperAdmin has no specific location
        );
        
        AuthResponse response = AuthResponse.success(token, superAdmin.getUsername());
        response.setUserId(superAdmin.getId());
        response.setRole("SUPERADMIN");
        response.setDepartment(null);
        response.setLocation(null);
        
        return response;
    }
    
    /**
     * Create AuthResponse for Admin
     */
    private AuthResponse createAuthResponse(Admin admin) {
        String token = jwtUtil.generateToken(
            admin.getId(),
            admin.getUsername(),
            admin.getRole() != null ? admin.getRole() : "ADMIN",
            admin.getDepartment(),
            admin.getLocation()
        );
        
        AuthResponse response = AuthResponse.success(token, admin.getUsername());
        response.setUserId(admin.getId());
        response.setRole(admin.getRole() != null ? admin.getRole() : "ADMIN");
        response.setDepartment(admin.getDepartment());
        response.setLocation(admin.getLocation());
        response.setDepartmentId(admin.getDepartmentId());
        
        return response;
    }
    
    /**
     * Validate JWT token
     */
    public boolean validateToken(String token) {
        if (token == null || token.trim().isEmpty()) {
            return false;
        }
        return jwtUtil.validateToken(token.trim());
    }
    
    /**
     * Extract username from token
     */
    public String getUsernameFromToken(String token) {
        if (token == null || token.trim().isEmpty()) {
            return null;
        }
        try {
            return jwtUtil.getUsernameFromToken(token.trim());
        } catch (Exception e) {
            logger.debug("Error extracting username from token", e);
            return null;
        }
    }
    
    /**
     * Extract user ID from token
     */
    public String getUserIdFromToken(String token) {
        if (token == null || token.trim().isEmpty()) {
            return null;
        }
        try {
            return jwtUtil.getUserIdFromToken(token.trim());
        } catch (Exception e) {
            logger.debug("Error extracting user ID from token", e);
            return null;
        }
    }
    
    /**
     * Extract role from token
     */
    public String getRoleFromToken(String token) {
        if (token == null || token.trim().isEmpty()) {
            return null;
        }
        try {
            return jwtUtil.getRoleFromToken(token.trim());
        } catch (Exception e) {
            logger.debug("Error extracting role from token", e);
            return null;
        }
    }
    
    /**
     * Extract department from token
     */
    public String getDepartmentFromToken(String token) {
        if (token == null || token.trim().isEmpty()) {
            return null;
        }
        try {
            return jwtUtil.getDepartmentFromToken(token.trim());
        } catch (Exception e) {
            logger.debug("Error extracting department from token", e);
            return null;
        }
    }
    
    /**
     * Extract location from token
     */
    public String getLocationFromToken(String token) {
        if (token == null || token.trim().isEmpty()) {
            return null;
        }
        try {
            return jwtUtil.getLocationFromToken(token.trim());
        } catch (Exception e) {
            logger.debug("Error extracting location from token", e);
            return null;
        }
    }
    
    /**
     * Logout user (with JWT, we just rely on expiration)
     */
    public boolean logout(String token) {
        // With JWT, we don't need to invalidate tokens server-side
        // In production, you might want to maintain a blacklist
        logger.info("Logout requested for token");
        return true;
    }
    
    /**
     * Check if user is SuperAdmin
     */
    public boolean isSuperAdmin(String token) {
        String role = getRoleFromToken(token);
        return "SUPERADMIN".equals(role);
    }
    
    /**
     * Get token expiration time
     */
    public long getTokenExpirationInMinutes(String token) {
        if (token == null || token.trim().isEmpty()) {
            return -1;
        }
        try {
            return jwtUtil.getTokenExpirationInMinutes(token.trim());
        } catch (Exception e) {
            logger.debug("Error getting token expiration", e);
            return -1;
        }
    }
}
