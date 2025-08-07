package com.leoni.controllers;

import com.leoni.models.Admin;
import com.leoni.repositories.AdminRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class SimpleAuthController {
    
    @Autowired
    private AdminRepository adminRepository;
    
    /**
     * Simple authentication endpoint that checks against database users
     */
    @PostMapping("/simple-login")
    public ResponseEntity<Map<String, Object>> simpleLogin(@RequestBody Map<String, String> credentials) {
        System.out.println("=== SIMPLE AUTH ENDPOINT CALLED ===");
        System.out.println("Received credentials: " + credentials);
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            String username = credentials.get("username");
            String password = credentials.get("password");
            
            System.out.println("Username: " + username);
            System.out.println("Password: " + password);
            
            // Check if user exists in database
            Admin admin = adminRepository.findByUsername(username).orElse(null);
            if (admin != null && admin.getPassword().equals(password)) {
                String token = "admin-token-" + UUID.randomUUID().toString();
                
                response.put("success", true);
                response.put("message", "Authentication successful");
                response.put("token", token);
                response.put("username", username);
                response.put("location", admin.getLocation());
                response.put("department", admin.getDepartment());
                
                System.out.println("Authentication successful for user: " + username);
                return ResponseEntity.ok(response);
            } else {
                response.put("success", false);
                response.put("message", "Invalid credentials - user not found or wrong password");
                
                System.out.println("Authentication failed for user: " + username);
                return ResponseEntity.status(401).body(response);
            }
        } catch (Exception e) {
            System.out.println("Exception in simple login: " + e.getMessage());
            e.printStackTrace();
            
            response.put("success", false);
            response.put("message", "Internal server error: " + e.getMessage());
            
            return ResponseEntity.status(500).body(response);
        }
    }
}