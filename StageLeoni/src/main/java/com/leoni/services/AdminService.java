package com.leoni.services;

import com.leoni.models.Admin;
import com.leoni.models.Department;
import com.leoni.repositories.AdminRepository;
import com.leoni.repositories.DepartmentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class AdminService {
    
    @Autowired
    private AdminRepository adminRepository;
    
    @Autowired
    private DepartmentRepository departmentRepository;
    
    public Admin createAdmin(String username, String password, String departmentId) {
        // Check if username already exists
        if (adminRepository.existsByUsername(username)) {
            throw new RuntimeException("Username already exists");
        }
        
        // Validate department exists
        Optional<Department> department = departmentRepository.findById(departmentId);
        if (!department.isPresent()) {
            throw new RuntimeException("Department not found");
        }
        
        Admin admin = new Admin(username, password, departmentId);
        return adminRepository.save(admin);
    }
    
    /**
     * Create admin with location and department (new simplified structure)
     */
    public Admin createAdminWithLocation(String username, String password, String location, String department) {
        // Check if username already exists
        if (adminRepository.existsByUsername(username)) {
            throw new RuntimeException("Username already exists");
        }
        
        Admin admin = new Admin();
        admin.setUsername(username);
        admin.setPassword(password);
        admin.setLocation(location);
        admin.setDepartment(department);
        admin.setRole("ADMIN");
        admin.setActive(true);
        admin.setCreatedAt(LocalDateTime.now());
        admin.setUpdatedAt(LocalDateTime.now());
        
        return adminRepository.save(admin);
    }
    
    public Optional<Admin> authenticateAdmin(String username, String password) {
        Optional<Admin> admin = adminRepository.findByUsernameAndActiveTrue(username);
        if (admin.isPresent() && password.equals(admin.get().getPassword())) {
            return admin;
        }
        return Optional.empty();
    }
    
    public List<Admin> getAllActiveAdmins() {
        return adminRepository.findByActiveTrue();
    }
    
    public Optional<Admin> findById(String id) {
        return adminRepository.findById(id);
    }
    
    public Admin getAdminById(String id) {
        return adminRepository.findById(id).orElse(null);
    }
    
    public Optional<Admin> findByUsername(String username) {
        return adminRepository.findByUsernameAndActiveTrue(username);
    }
    
    public Admin updateAdmin(Admin admin) {
        admin.setUpdatedAt(LocalDateTime.now());
        return adminRepository.save(admin);
    }
    
    public Admin save(Admin admin) {
        return adminRepository.save(admin);
    }
    
    public void deleteAdmin(String id) {
        Optional<Admin> admin = adminRepository.findById(id);
        if (admin.isPresent()) {
            Admin adminToDelete = admin.get();
            adminToDelete.setActive(false);
            adminToDelete.setUpdatedAt(LocalDateTime.now());
            adminRepository.save(adminToDelete);
        }
    }
    
    public List<Admin> getAdminsByDepartment(String departmentId) {
        return adminRepository.findByDepartmentIdAndActiveTrue(departmentId);
    }
}
