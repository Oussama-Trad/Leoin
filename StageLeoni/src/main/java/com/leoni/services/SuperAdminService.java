package com.leoni.services;

import com.leoni.models.SuperAdmin;
import com.leoni.models.Admin;
import com.leoni.models.User;
import com.leoni.repositories.SuperAdminRepository;
import com.leoni.repositories.AdminRepository;
import com.leoni.repositories.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class SuperAdminService {
    
    private static final Logger logger = LoggerFactory.getLogger(SuperAdminService.class);
    
    @Autowired
    private SuperAdminRepository superAdminRepository;
    
    @Autowired
    private AdminRepository adminRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    /**
     * Create a new superadmin
     */
    public SuperAdmin createSuperAdmin(SuperAdmin superAdmin) {
        if (superAdminRepository.existsByUsername(superAdmin.getUsername())) {
            throw new RuntimeException("SuperAdmin with username '" + superAdmin.getUsername() + "' already exists");
        }
        
        superAdmin.setCreatedAt(LocalDateTime.now());
        superAdmin.setUpdatedAt(LocalDateTime.now());
        
        return superAdminRepository.save(superAdmin);
    }
    
    /**
     * Authenticate superadmin with logging and last login update
     */
    public Optional<SuperAdmin> authenticate(String username, String password) {
        try {
            System.out.println("SuperAdminService.authenticate called with username: " + username);
            
            // Try with findByUsername first (more lenient)
            Optional<SuperAdmin> superAdmin = superAdminRepository.findByUsername(username);
            System.out.println("Repository query result: " + (superAdmin.isPresent() ? "Found" : "Not found"));
            
            if (superAdmin.isPresent()) {
                SuperAdmin admin = superAdmin.get();
                System.out.println("SuperAdmin found: " + admin.getUsername() + ", active: " + admin.isActive());
                System.out.println("Expected password: " + admin.getPassword());
                System.out.println("Provided password: " + password);
                System.out.println("Password comparison: " + (admin.getPassword().equals(password) ? "MATCH" : "NO MATCH"));
                
                // Check if active and password matches
                if (admin.isActive() && admin.getPassword().equals(password)) {
                    admin.updateLastLogin();
                    superAdminRepository.save(admin);
                    logger.info("SuperAdmin {} authenticated successfully", username);
                    System.out.println("SuperAdmin authentication successful");
                    return superAdmin;
                } else {
                    if (!admin.isActive()) {
                        System.out.println("SuperAdmin account is inactive");
                    }
                    if (!admin.getPassword().equals(password)) {
                        System.out.println("Password mismatch");
                    }
                }
            } else {
                System.out.println("SuperAdmin not found in database for username: " + username);
                // Try to find all superadmins to debug
                List<SuperAdmin> allSuperAdmins = superAdminRepository.findAll();
                System.out.println("Total SuperAdmins in database: " + allSuperAdmins.size());
                for (SuperAdmin sa : allSuperAdmins) {
                    System.out.println("  - Username: " + sa.getUsername() + ", Active: " + sa.isActive());
                }
            }
            
            logger.warn("Failed authentication attempt for SuperAdmin: {}", username);
            System.out.println("SuperAdmin authentication failed");
            return Optional.empty();
        } catch (Exception e) {
            logger.error("Error during SuperAdmin authentication", e);
            System.out.println("Exception in SuperAdmin authentication: " + e.getMessage());
            e.printStackTrace();
            return Optional.empty();
        }
    }
    
    /**
     * Get all active superadmins
     */
    public List<SuperAdmin> getAllActiveSuperAdmins() {
        return superAdminRepository.findByActiveTrue();
    }
    
    /**
     * Find superadmin by ID
     */
    public Optional<SuperAdmin> findById(String id) {
        return superAdminRepository.findById(id);
    }
    
    /**
     * Find superadmin by username
     */
    public Optional<SuperAdmin> findByUsername(String username) {
        return superAdminRepository.findByUsernameAndActiveTrue(username);
    }
    
    /**
     * Update superadmin
     */
    public SuperAdmin updateSuperAdmin(SuperAdmin superAdmin) {
        superAdmin.setUpdatedAt(LocalDateTime.now());
        return superAdminRepository.save(superAdmin);
    }
    
    /**
     * Delete superadmin (soft delete)
     */
    public void deleteSuperAdmin(String id) {
        Optional<SuperAdmin> superAdmin = superAdminRepository.findById(id);
        if (superAdmin.isPresent()) {
            SuperAdmin superAdminToDelete = superAdmin.get();
            superAdminToDelete.setActive(false);
            superAdminToDelete.setUpdatedAt(LocalDateTime.now());
            superAdminRepository.save(superAdminToDelete);
        }
    }
    
    /**
     * Save superadmin
     */
    public SuperAdmin save(SuperAdmin superAdmin) {
        return superAdminRepository.save(superAdmin);
    }
    
    /**
     * Get all admins (SuperAdmin privilege)
     */
    public List<Admin> getAllAdmins() {
        return adminRepository.findAll();
    }
    
    /**
     * Get all employees (SuperAdmin privilege)
     */
    public List<User> getAllEmployees() {
        return userRepository.findAll();
    }
    
    /**
     * Get admins by department ID
     */
    public List<Admin> getAdminsByDepartment(String departmentId) {
        return adminRepository.findByDepartmentId(departmentId);
    }
    
    /**
     * Get active admins
     */
    public List<Admin> getActiveAdmins() {
        return adminRepository.findByActiveTrue();
    }
    
    /**
     * Create default SuperAdmin if none exists
     */
    public void createDefaultSuperAdminIfNeeded() {
        try {
            if (superAdminRepository.count() == 0) {
                SuperAdmin defaultSuperAdmin = new SuperAdmin(
                    "superadmin", 
                    "superadmin123", // In production, use encrypted password
                    "superadmin@leoni.com",
                    "Super",
                    "Admin"
                );
                
                superAdminRepository.save(defaultSuperAdmin);
                logger.info("Default SuperAdmin created: username=superadmin, password=superadmin123");
            }
        } catch (Exception e) {
            logger.error("Error creating default SuperAdmin", e);
        }
    }
}
