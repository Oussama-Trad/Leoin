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
            Optional<SuperAdmin> superAdmin = superAdminRepository.findByUsernameAndActiveTrue(username);
            
            if (superAdmin.isPresent() && superAdmin.get().getPassword().equals(password)) {
                SuperAdmin admin = superAdmin.get();
                admin.updateLastLogin();
                superAdminRepository.save(admin);
                logger.info("SuperAdmin {} authenticated successfully", username);
                return superAdmin;
            }
            
            logger.warn("Failed authentication attempt for SuperAdmin: {}", username);
            return Optional.empty();
        } catch (Exception e) {
            logger.error("Error during SuperAdmin authentication", e);
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
