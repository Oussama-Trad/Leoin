package com.leoni.controllers;

import com.leoni.models.Admin;
import com.leoni.models.Department;
import com.leoni.repositories.DepartmentRepository;
import com.leoni.services.AdminService;
import com.leoni.services.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/admin")
@CrossOrigin(origins = "*")
public class AdminController {
    
    @Autowired
    private AdminService adminService;
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private DepartmentRepository departmentRepository;
    
    @PostMapping("/create")
    public ResponseEntity<?> createAdmin(@RequestBody Map<String, String> request) {
        try {
            String username = request.get("username");
            String password = request.get("password");
            String location = request.get("location");
            String department = request.get("department");
            
            if (username == null || password == null || location == null || department == null) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Username, password, location, and department are required")
                );
            }
            
            Admin admin = adminService.createAdminWithLocation(username, password, location, department);
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "Admin created successfully",
                "admin", Map.of(
                    "id", admin.getId(),
                    "username", admin.getUsername(),
                    "location", admin.getLocation(),
                    "department", admin.getDepartment()
                )
            ));
            
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(
                Map.of("success", false, "message", e.getMessage())
            );
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                Map.of("success", false, "message", "Internal server error: " + e.getMessage())
            );
        }
    }
    
    @PostMapping("/authenticate")
    public ResponseEntity<?> authenticateAdmin(@RequestBody Map<String, String> request) {
        try {
            String username = request.get("username");
            String password = request.get("password");
            
            if (username == null || password == null) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Username and password are required")
                );
            }
            
            Optional<Admin> admin = adminService.authenticateAdmin(username, password);
            
            if (admin.isPresent()) {
                Admin authenticatedAdmin = admin.get();
                return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", "Authentication successful",
                    "admin", Map.of(
                        "id", authenticatedAdmin.getId(),
                        "username", authenticatedAdmin.getUsername(),
                        "departmentId", authenticatedAdmin.getDepartmentId(),
                        "role", authenticatedAdmin.getRole()
                    )
                ));
            } else {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Invalid credentials")
                );
            }
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", "Authentication failed: " + e.getMessage())
            );
        }
    }
    
    @GetMapping("/all")
    public ResponseEntity<List<Admin>> getAllAdmins() {
        List<Admin> admins = adminService.getAllActiveAdmins();
        return ResponseEntity.ok(admins);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<?> getAdminById(@PathVariable String id) {
        Optional<Admin> admin = adminService.findById(id);
        if (admin.isPresent()) {
            return ResponseEntity.ok(admin.get());
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    @GetMapping("/by-department/{departmentId}")
    public ResponseEntity<List<Admin>> getAdminsByDepartment(@PathVariable String departmentId) {
        List<Admin> admins = adminService.getAdminsByDepartment(departmentId);
        return ResponseEntity.ok(admins);
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteAdmin(@PathVariable String id) {
        try {
            adminService.deleteAdmin(id);
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "Admin deleted successfully"
            ));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(
                Map.of("success", false, "message", e.getMessage())
            );
        }
    }
    
    /**
     * Create admin with location and department (new simplified structure)
     */
    @PostMapping("/create-with-location")
    public ResponseEntity<?> createAdminWithLocation(@RequestBody Map<String, String> request) {
        try {
            String username = request.get("username");
            String password = request.get("password");
            String location = request.get("location");
            String department = request.get("department");
            
            if (username == null || password == null || location == null || department == null) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Username, password, location, and department are required")
                );
            }
            
            // Create admin with location and department
            Admin admin = adminService.createAdminWithLocation(username, password, location, department);
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "Admin created successfully with location and department",
                "admin", Map.of(
                    "id", admin.getId(),
                    "username", admin.getUsername(),
                    "location", admin.getLocation(),
                    "department", admin.getDepartment(),
                    "role", admin.getRole(),
                    "createdAt", admin.getCreatedAt()
                )
            ));
            
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(
                Map.of("success", false, "message", e.getMessage())
            );
        }
    }
    
    /**
     * Get available locations and departments for admin creation
     */
    @GetMapping("/creation-options")
    public ResponseEntity<?> getAdminCreationOptions() {
        try {
            // Get all unique locations
            List<String> locations = departmentRepository.findAll().stream()
                    .map(Department::getLocation)
                    .filter(location -> location != null && !location.trim().isEmpty())
                    .distinct()
                    .sorted()
                    .collect(Collectors.toList());
            
            // Get departments grouped by location
            Map<String, List<String>> departmentsByLocation = new HashMap<>();
            for (String location : locations) {
                List<String> departments = departmentRepository.findByLocation(location).stream()
                        .map(Department::getName)
                        .filter(name -> name != null && !name.trim().isEmpty())
                        .distinct()
                        .sorted()
                        .collect(Collectors.toList());
                departmentsByLocation.put(location, departments);
            }
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "locations", locations,
                "departmentsByLocation", departmentsByLocation
            ));
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                Map.of("success", false, "message", "Error fetching creation options: " + e.getMessage())
            );
        }
    }
}
