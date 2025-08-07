package com.leoni.controllers;

import com.leoni.models.SuperAdmin;
import com.leoni.models.Admin;
import com.leoni.models.User;
import com.leoni.models.News;
import com.leoni.services.SuperAdminService;
import com.leoni.services.NewsService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.Optional;

@RestController
@RequestMapping("/api/superadmin")
@CrossOrigin(origins = "*")
public class SuperAdminController {
    
    private static final Logger logger = LoggerFactory.getLogger(SuperAdminController.class);
    
    @Autowired
    private SuperAdminService superAdminService;
    
    @Autowired
    private NewsService newsService;
    
    /**
     * SuperAdmin login
     */
    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody Map<String, String> credentials) {
        try {
            String username = credentials.get("username");
            String password = credentials.get("password");
            
            Optional<SuperAdmin> superAdmin = superAdminService.authenticate(username, password);
            
            Map<String, Object> response = new HashMap<>();
            
            if (superAdmin.isPresent()) {
                response.put("success", true);
                response.put("message", "SuperAdmin login successful");
                response.put("superadmin", superAdmin.get());
                response.put("role", "SUPERADMIN");
                return ResponseEntity.ok(response);
            } else {
                response.put("success", false);
                response.put("message", "Invalid credentials");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
            }
            
        } catch (Exception e) {
            logger.error("Error during SuperAdmin login", e);
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "Login error: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
    
    /**
     * Get all admins (SuperAdmin privilege)
     */
    @GetMapping("/admins")
    public ResponseEntity<List<Admin>> getAllAdmins() {
        try {
            List<Admin> admins = superAdminService.getAllAdmins();
            return ResponseEntity.ok(admins);
        } catch (Exception e) {
            logger.error("Error retrieving admins", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }
    }
    
    /**
     * Get all employees (SuperAdmin privilege)
     */
    @GetMapping("/employees")
    public ResponseEntity<List<User>> getAllEmployees() {
        try {
            List<User> employees = superAdminService.getAllEmployees();
            return ResponseEntity.ok(employees);
        } catch (Exception e) {
            logger.error("Error retrieving employees", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }
    }
    
    /**
     * Get system statistics (SuperAdmin privilege)
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getSystemStats() {
        try {
            Map<String, Object> stats = new HashMap<>();
            
            // Count admins and employees
            stats.put("totalAdmins", superAdminService.getAllAdmins().size());
            stats.put("activeAdmins", superAdminService.getActiveAdmins().size());
            stats.put("totalEmployees", superAdminService.getAllEmployees().size());
            stats.put("totalNews", newsService.getAllNews().size());
            
            return ResponseEntity.ok(stats);
            
        } catch (Exception e) {
            logger.error("Error retrieving system stats", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }
    }
}
