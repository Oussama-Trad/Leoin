package com.leoni.services;

import com.leoni.dto.AuthRequest;
import com.leoni.dto.AuthResponse;
import com.leoni.models.Admin;
import com.leoni.models.SuperAdmin;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Service
public class AuthService {
    
    @Autowired
    private AdminService adminService;
    
    @Autowired
    private SuperAdminService superAdminService;
    
    @Autowired
    private FlaskApiService flaskApiService;
    
    // Simple hardcoded admin credentials as fallback
    private static final String ADMIN_USERNAME = "admin";
    private static final String ADMIN_PASSWORD = "admin";
    
    // Clé secrète pour décoder les tokens JWT (doit être la même que Flask)
    private final String SECRET_KEY = "your-secret-key-must-be-at-least-32-characters-long-for-hs256";
    
    /**
     * Authenticate user via Flask API first, then fallback to local auth
     * @param authRequest the authentication request
     * @return AuthResponse with authentication result and role information
     */
    public AuthResponse authenticate(AuthRequest authRequest) {
        if (authRequest == null || authRequest.getUsername() == null || authRequest.getPassword() == null) {
            return AuthResponse.failure("Nom d'utilisateur et mot de passe requis");
        }
        
        String username = authRequest.getUsername();
        String password = authRequest.getPassword();
        
        // PRIORITÉ 1: Authentification via Flask API (backend commun)
        try {
            String flaskToken = flaskApiService.authenticateAdmin(username, password);
            if (flaskToken != null) {
                Admin admin = decodeAdminFromToken(flaskToken);
                if (admin != null) {
                    AuthResponse response = AuthResponse.success(flaskToken, username);
                    response.setRole(admin.getRole());
                    response.setUserId(admin.getUsername());
                    response.setLocation(admin.getLocation());
                    response.setDepartment(admin.getDepartment());
                    response.setFlaskToken(flaskToken); // Stocker le token Flask
                    return response;
                }
            }
        } catch (Exception e) {
            System.err.println("Erreur authentification Flask: " + e.getMessage());
            // Continue avec l'authentification locale en fallback
        }
        
        // PRIORITÉ 2: Authentification locale (fallback)
        // First, try to authenticate as SuperAdmin
        Optional<SuperAdmin> superAdmin = superAdminService.authenticate(username, password);
        if (superAdmin.isPresent()) {
            String token = generateToken("SUPERADMIN", superAdmin.get().getId());
            AuthResponse response = AuthResponse.success(token, username);
            response.setRole("SUPERADMIN");
            response.setUserId(superAdmin.get().getId());
            return response;
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
     * Décoder un token JWT Flask pour extraire les informations admin
     * @param token token JWT
     * @return Admin object ou null si erreur
     */
    public Admin decodeAdminFromToken(String token) {
        try {
            Claims claims = Jwts.parser()
                .setSigningKey(SECRET_KEY.getBytes())
                .parseClaimsJws(token)
                .getBody();

            Admin admin = new Admin();
            admin.setUsername(claims.get("username", String.class));
            admin.setRole(claims.get("role", String.class));
            admin.setDepartment(claims.get("department", String.class));
            admin.setLocation(claims.get("location", String.class));
            // Note: Admin model n'a pas de champ email, on ignore
            // admin.setEmail(claims.get("email", String.class));

            return admin;
        } catch (Exception e) {
            System.err.println("Erreur décodage token Flask: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Vérifier si un admin peut accéder à des données d'un département/location
     * @param admin admin qui fait la requête
     * @param targetDepartment département cible
     * @param targetLocation location cible
     * @return true si autorisé, false sinon
     */
    public boolean canAccessDepartmentLocation(Admin admin, String targetDepartment, String targetLocation) {
        if (admin == null) {
            return false;
        }

        // SUPERADMIN a accès à tout
        if ("SUPERADMIN".equals(admin.getRole())) {
            return true;
        }

        // ADMIN ne peut accéder qu'à son département et sa location
        if ("ADMIN".equals(admin.getRole())) {
            boolean departmentMatch = admin.getDepartment() != null && 
                                    admin.getDepartment().equals(targetDepartment);
            boolean locationMatch = admin.getLocation() != null && 
                                  admin.getLocation().equals(targetLocation);
            
            return departmentMatch && locationMatch;
        }

        return false;
    }
    
    /**
     * Obtenir les paramètres de filtrage pour un admin
     * @param admin admin connecté
     * @return map avec department et location pour le filtrage
     */
    public Map<String, String> getFilteringParams(Admin admin) {
        if (admin == null) {
            return Map.of();
        }

        // SUPERADMIN : pas de filtrage automatique
        if ("SUPERADMIN".equals(admin.getRole())) {
            return Map.of("role", "SUPERADMIN");
        }

        // ADMIN : filtrage par son département et location
        if ("ADMIN".equals(admin.getRole())) {
            return Map.of(
                "role", "ADMIN",
                "department", admin.getDepartment() != null ? admin.getDepartment() : "",
                "location", admin.getLocation() != null ? admin.getLocation() : ""
            );
        }

        return Map.of();
    }
    
    /**
     * Validate authentication token (Flask JWT ou token local)
     * @param token the token to validate
     * @return true if token is valid
     */
    public boolean validateToken(String token) {
        if (token == null) {
            return false;
        }
        
        // Vérifier si c'est un token JWT Flask
        try {
            Jwts.parser()
                .setSigningKey(SECRET_KEY.getBytes())
                .parseClaimsJws(token);
            return true;
        } catch (Exception e) {
            // Pas un token JWT valide, continuer avec la validation locale
        }
        
        // Validation des tokens locaux
        if (token.startsWith("admin-token-") || token.startsWith("superadmin-token-")) {
            return true;
        }
        
        // Backward compatibility - accept "authenticated" as a valid token for now
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
}