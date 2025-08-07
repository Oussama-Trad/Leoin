package com.leoni.controllers;

import com.leoni.dto.UserDTO;
import com.leoni.models.Admin;
import com.leoni.models.Department;
import com.leoni.models.DocumentRequest;
import com.leoni.services.AdminService;
import com.leoni.services.AuthService;
import com.leoni.services.UserService;
import com.leoni.repositories.DepartmentRepository;
import com.leoni.repositories.DocumentRequestRepository;
import com.leoni.exceptions.UserNotFoundException;
import com.leoni.exceptions.DuplicateUserException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.ArrayList;
import java.util.Optional;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/admin/employees")
@CrossOrigin(origins = "*")
public class AdminEmployeeController {

    private static final Logger logger = LoggerFactory.getLogger(AdminEmployeeController.class);

    @Autowired
    private UserService userService;

    @Autowired
    private AdminService adminService;

    @Autowired
    private AuthService authService;

    @Autowired
    private DocumentRequestRepository documentRequestRepository;

    @Autowired
    private DepartmentRepository departmentRepository;

    /**
     * Create sample data for testing
     */
    @PostMapping("/create-sample-data")
    public ResponseEntity<Map<String, Object>> createSampleData() {
        try {
            // Create sample employees with location and department for filtering
            UserDTO employee1 = new UserDTO();
            employee1.setFirstName("John");
            employee1.setLastName("Doe");
            employee1.setAdresse1("john.doe@leoni.com");
            employee1.setEmployeeId("EMP001");
            employee1.setDepartmentId(null); // Will be set later from hierarchy
            employee1.setPosition("Software Engineer");
            employee1.setPhoneNumber("+1234567890");
            // Set location and department for filtering
            employee1.setLocation("Mateur");
            employee1.setDepartment("Production");
            
            UserDTO employee2 = new UserDTO();
            employee2.setFirstName("Jane");
            employee2.setLastName("Smith");
            employee2.setAdresse1("jane.smith@leoni.com");
            employee2.setEmployeeId("EMP002");
            employee2.setDepartmentId(null); // Will be set later from hierarchy
            employee2.setPosition("HR Manager");
            employee2.setPhoneNumber("+1234567891");
            // Set location and department for filtering
            employee2.setLocation("Mateur");
            employee2.setDepartment("Production");
            
            UserDTO employee3 = new UserDTO();
            employee3.setFirstName("Mike");
            employee3.setLastName("Johnson");
            employee3.setAdresse1("mike.johnson@leoni.com");
            employee3.setEmployeeId("EMP003");
            employee3.setDepartmentId(null); // Will be set later from hierarchy
            employee3.setPosition("Financial Analyst");
            employee3.setPhoneNumber("+1234567892");
            // Set location and department for filtering
            employee3.setLocation("Mateur");
            employee3.setDepartment("Production");
            
            // Save employees
            UserDTO created1 = userService.createUser(employee1);
            UserDTO created2 = userService.createUser(employee2);
            UserDTO created3 = userService.createUser(employee3);
            
            logger.info("Created sample employees with location/department: {}/{}, {}/{}, {}/{}", 
                       created1.getLocation(), created1.getDepartment(),
                       created2.getLocation(), created2.getDepartment(),
                       created3.getLocation(), created3.getDepartment());
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "Sample data created successfully with location and department information");
            response.put("employeesCreated", 3);
            response.put("location", "Mateur");
            response.put("department", "Production");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Failed to create sample data: " + e.getMessage());
            return ResponseEntity.status(500).body(error);
        }
    }

    /**
     * Get all employees with their documents for admin panel
     * Filtered by admin's department hierarchy or all employees for superadmin
     * @param adminId the admin ID for filtering (optional)
     * @param adminUsername the admin username for filtering (optional, alternative to adminId)
     * @param location location filter (optional, mainly for superadmin)
     * @param department department filter (optional, mainly for superadmin)
     * @param status status filter (optional)
     */
    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> getAllEmployees(
            @RequestParam(value = "adminId", required = false) String adminId,
            @RequestParam(value = "adminUsername", required = false) String adminUsername,
            @RequestParam(value = "location", required = false) String location,
            @RequestParam(value = "department", required = false) String department,
            @RequestParam(value = "status", required = false) String status,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {
        try {
            System.out.println("=== GET ALL EMPLOYEES REQUEST ===");
            System.out.println("AdminId parameter: " + adminId);
            System.out.println("AdminUsername parameter: " + adminUsername);
            System.out.println("Filters - Location: " + location + ", Department: " + department + ", Status: " + status);
            System.out.println("Authorization header: " + authHeader);
            
            List<UserDTO> users;
            String userRole = null;
            String userId = null;
            String actualAdminUsername = null;
            
            // Check if we have an authorization token
            if (authHeader != null && !authHeader.trim().isEmpty()) {
                String token = authHeader.startsWith("Bearer ") ? authHeader.substring(7) : authHeader;
                
                if (authService.validateToken(token)) {
                    userRole = authService.getRoleFromToken(token);
                    userId = authService.getUserIdFromToken(token);
                    System.out.println("Token validated - Role: " + userRole + ", UserId: " + userId);
                }
            }
            
            // If we have role information from token, use it
            if (userRole != null && userId != null) {
                users = userService.getUsersByRole(userRole, userId, location, department, status);
                System.out.println("Found " + users.size() + " employees using role-based filtering");
                
            } else {
                // Fallback to legacy method for backward compatibility
                
                // Determine which admin username to use
                if (adminUsername != null && !adminUsername.isEmpty()) {
                    actualAdminUsername = adminUsername;
                } else if (adminId != null && !adminId.isEmpty()) {
                    // Get admin by ID and extract username
                    Admin admin = adminService.getAdminById(adminId);
                    if (admin != null) {
                        actualAdminUsername = admin.getUsername();
                    }
                } else if (authHeader != null && !authHeader.trim().isEmpty()) {
                    // Try to extract admin info from Authorization header
                    String token = authHeader.startsWith("Bearer ") ? authHeader.substring(7) : authHeader;
                    System.out.println("Extracted token: " + token);
                    
                    // Try to find admin by token (assuming token is admin ID)
                    Admin admin = adminService.getAdminById(token);
                    if (admin != null) {
                        actualAdminUsername = admin.getUsername();
                        System.out.println("Found admin from token - Username: " + actualAdminUsername);
                    } else {
                        System.out.println("Admin not found by token ID, trying to validate token and extract username");
                        // If token is not admin ID, try to validate and get username from AuthService
                        if (authService.validateToken(token)) {
                            actualAdminUsername = authService.getUsernameFromToken(token);
                            if (actualAdminUsername != null) {
                                System.out.println("Found admin username from token: " + actualAdminUsername);
                            }
                        }
                    }
                }
                
                if (actualAdminUsername != null) {
                    System.out.println("Using admin username for filtering: " + actualAdminUsername);
                    // Use the existing method for admin filtering
                    users = userService.getFilteredUsersByAdminUsername(actualAdminUsername);
                    System.out.println("Found " + users.size() + " employees in admin's scope");
                } else if (adminId != null || adminUsername != null || authHeader != null) {
                    // Admin info provided but admin not found
                    System.out.println("Admin not found, returning empty list");
                    users = List.of();
                } else {
                    // No admin info provided, return all users (for backward compatibility)
                    users = userService.getAllUsers();
                }
            }
            
            List<Map<String, Object>> employeesWithDocuments = users.stream()
                .map(this::mapUserToAdminResponse)
                .collect(Collectors.toList());
            
            return ResponseEntity.ok(employeesWithDocuments);
        } catch (Exception e) {
            System.err.println("Error in getAllEmployees: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(null);
        }
    }

    /**
     * Get employee by ID with documents
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getEmployeeById(@PathVariable String id) {
        try {
            UserDTO user = userService.getUserById(id);
            return ResponseEntity.ok(mapUserToAdminResponse(user));
        } catch (UserNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.status(500).body(null);
        }
    }

    /**
     * Create new employee
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createEmployee(@RequestBody UserDTO userDTO) {
        try {
            UserDTO savedUser = userService.createUser(userDTO);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Employee created successfully");
            response.put("employee", mapUserToAdminResponse(savedUser));
            return ResponseEntity.ok(response);
        } catch (DuplicateUserException e) {
            return ResponseEntity.status(400).body(createErrorResponse(e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(500).body(createErrorResponse("Error creating employee: " + e.getMessage()));
        }
    }

    /**
     * Update employee
     */
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateEmployee(@PathVariable String id, @RequestBody UserDTO userDTO) {
        try {
            UserDTO updatedUser = userService.updateUser(id, userDTO);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Employee updated successfully");
            response.put("employee", mapUserToAdminResponse(updatedUser));
            return ResponseEntity.ok(response);
        } catch (UserNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.status(500).body(createErrorResponse("Error updating employee: " + e.getMessage()));
        }
    }

    /**
     * Delete employee
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteEmployee(@PathVariable String id) {
        try {
            userService.deleteUser(id);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Employee deleted successfully");
            return ResponseEntity.ok(response);
        } catch (UserNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.status(500).body(createErrorResponse("Error deleting employee: " + e.getMessage()));
        }
    }

    /**
     * Get employee's documents
     */
    @GetMapping("/{id}/documents")
    public ResponseEntity<List<DocumentRequest>> getEmployeeDocuments(@PathVariable String id) {
        try {
            List<DocumentRequest> documents = documentRequestRepository.findByUserIdOrderByCreatedAtDesc(id);
            return ResponseEntity.ok(documents);
        } catch (Exception e) {
            System.err.println("Error fetching documents for user " + id + ": " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(null);
        }
    }

    /**
     * Update document status
     */
    @PutMapping("/{userId}/documents/{documentId}/status")
    public ResponseEntity<Map<String, Object>> updateDocumentStatus(
            @PathVariable String userId,
            @PathVariable String documentId,
            @RequestBody Map<String, String> statusUpdate) {
        try {
            DocumentRequest document = documentRequestRepository.findById(documentId).orElse(null);
            if (document == null) {
                return ResponseEntity.notFound().build();
            }
            
            String newStatus = statusUpdate.get("status");
            if (newStatus != null) {
                document.getStatus().setCurrent(newStatus);
                document.setUpdatedAt(new java.util.Date());
                
                // Update progress steps
                document.getStatus().getProgress().forEach(step -> {
                    if (step.getStep().equals(newStatus)) {
                        step.setCompleted(true);
                        step.setDate(new java.util.Date());
                    }
                });
                
                documentRequestRepository.save(document);
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Document status updated successfully");
            response.put("document", document);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(createErrorResponse("Error updating document status: " + e.getMessage()));
        }
    }

    /**
     * Delete a document request
     */
    @DeleteMapping("/{userId}/documents/{documentId}")
    public ResponseEntity<Map<String, Object>> deleteDocument(
            @PathVariable String userId,
            @PathVariable String documentId) {
        try {
            // Find the document
            DocumentRequest document = documentRequestRepository.findById(documentId).orElse(null);
            if (document == null) {
                return ResponseEntity.notFound().build();
            }
            
            // Verify the document belongs to the user
            if (!document.getUserId().equals(userId)) {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "Document does not belong to this user");
                return ResponseEntity.status(403).body(response);
            }
            
            // Delete the document
            documentRequestRepository.deleteById(documentId);
            
            // Remove document ID from user's documentRequestIds list
            try {
                UserDTO user = userService.getUserById(userId);
                if (user.getDocumentRequestIds() != null) {
                    user.getDocumentRequestIds().remove(documentId);
                    userService.updateUser(userId, user);
                }
            } catch (Exception e) {
                System.err.println("Warning: Could not update user's document list: " + e.getMessage());
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Document deleted successfully");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(createErrorResponse("Error deleting document: " + e.getMessage()));
        }
    }

    /**
     * Get dashboard statistics
     */
    @GetMapping("/dashboard/stats")
    public ResponseEntity<Map<String, Object>> getDashboardStats() {
        try {
            List<UserDTO> users = userService.getAllUsers();
            List<DocumentRequest> allDocuments = documentRequestRepository.findAll();
            
            Map<String, Object> stats = new HashMap<>();
            stats.put("totalEmployees", users.size());
            stats.put("totalDocuments", allDocuments.size());
            
            // Count documents by status
            Map<String, Long> statusCounts = allDocuments.stream()
                .collect(Collectors.groupingBy(
                    doc -> doc.getStatus().getCurrent(),
                    Collectors.counting()
                ));
            
            stats.put("pendingDocuments", statusCounts.getOrDefault("en attente", 0L));
            stats.put("inProgressDocuments", statusCounts.getOrDefault("en cours", 0L));
            stats.put("acceptedDocuments", statusCounts.getOrDefault("accepté", 0L));
            stats.put("rejectedDocuments", statusCounts.getOrDefault("refusé", 0L));
            
            return ResponseEntity.ok(stats);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(createErrorResponse("Error fetching dashboard stats: " + e.getMessage()));
        }
    }

    // Helper methods
    private Map<String, Object> mapUserToAdminResponse(UserDTO user) {
        Map<String, Object> response = new HashMap<>();
        response.put("id", user.getId());
        response.put("firstName", user.getFirstName() != null ? user.getFirstName() : "");
        response.put("lastName", user.getLastName() != null ? user.getLastName() : "");
        response.put("fullName", (user.getFirstName() != null ? user.getFirstName() : "") + " " + (user.getLastName() != null ? user.getLastName() : ""));
        response.put("email", user.getEmail() != null ? user.getEmail() : (user.getAdresse1() != null ? user.getAdresse1() : ""));
        response.put("parentalEmail", user.getParentalEmail() != null ? user.getParentalEmail() : (user.getAdresse2() != null ? user.getAdresse2() : ""));
        
        // Add explicit adresse1 and adresse2 fields for backward compatibility
        response.put("adresse1", user.getAdresse1() != null ? user.getAdresse1() : "");
        response.put("adresse2", user.getAdresse2() != null ? user.getAdresse2() : "");
        
        response.put("phoneNumber", user.getPhoneNumber() != null ? user.getPhoneNumber() : "");
        response.put("employeeId", user.getEmployeeId() != null ? user.getEmployeeId() : "");
        response.put("department", user.getDepartmentName() != null ? user.getDepartmentName() : "");
        response.put("location", user.getLocationName() != null ? user.getLocationName() : "");
        response.put("position", user.getPosition() != null ? user.getPosition() : "");
        response.put("createdAt", user.getCreatedAt() != null ? user.getCreatedAt().getTime() : null);
        response.put("updatedAt", user.getUpdatedAt() != null ? user.getUpdatedAt().getTime() : null);
        
        // Get user's documents - handle null documentRequestIds
        List<DocumentRequest> rawDocuments = new ArrayList<>();
        try {
            if (user.getId() != null) {
                rawDocuments = documentRequestRepository.findByUserIdOrderByCreatedAtDesc(user.getId());
            }
        } catch (Exception e) {
            // Handle case where document repository fails
            rawDocuments = new ArrayList<>();
        }
        
        // Transform documents to include effective document types
        List<Map<String, Object>> documents = rawDocuments.stream().map(doc -> {
            Map<String, Object> docMap = new HashMap<>();
            docMap.put("id", doc.getId());
            docMap.put("userId", doc.getUserId());
            docMap.put("documentTypes", doc.getEffectiveDocumentTypes());
            docMap.put("description", doc.getDescription());
            docMap.put("status", doc.getStatus());
            docMap.put("createdAt", doc.getCreatedAt());
            docMap.put("updatedAt", doc.getUpdatedAt());
            return docMap;
        }).collect(Collectors.toList());
        
        response.put("documents", documents);
        response.put("documentCount", documents.size());
        response.put("documentRequestIds", user.getDocumentRequestIds() != null ? user.getDocumentRequestIds() : new ArrayList<>());
        
        // Count documents by status
        Map<String, Long> statusCounts = new HashMap<>();
        try {
            statusCounts = rawDocuments.stream()
                .filter(doc -> doc.getStatus() != null && doc.getStatus().getCurrent() != null)
                .collect(Collectors.groupingBy(
                    doc -> doc.getStatus().getCurrent(),
                    Collectors.counting()
                ));
        } catch (Exception e) {
            // Handle case where status counting fails
            statusCounts = new HashMap<>();
        }
        
        response.put("statusCounts", statusCounts);
        
        return response;
    }

    /**
     * Update document status - direct endpoint for admin
     */
    @PutMapping("/documents/{documentId}/status")
    public ResponseEntity<Map<String, Object>> updateDocumentStatusDirect(
            @PathVariable String documentId,
            @RequestBody Map<String, String> statusUpdate) {
        try {
            DocumentRequest document = documentRequestRepository.findById(documentId).orElse(null);
            if (document == null) {
                return ResponseEntity.notFound().build();
            }
            
            String newStatus = statusUpdate.get("newStatus");
            if (newStatus != null) {
                document.getStatus().setCurrent(newStatus);
                document.setUpdatedAt(new java.util.Date());
                
                // Update progress steps
                document.getStatus().getProgress().forEach(step -> {
                    if (step.getStep().equals(newStatus)) {
                        step.setCompleted(true);
                        step.setDate(new java.util.Date());
                    }
                });
                
                documentRequestRepository.save(document);
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Document status updated successfully");
            response.put("document", document);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            System.err.println("Error updating document status: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(createErrorResponse("Failed to update document status"));
        }
    }

    /**
     * Get all pending user requests
     */
    @GetMapping("/pending")
    public ResponseEntity<List<Map<String, Object>>> getPendingUsers() {
        try {
            List<UserDTO> pendingUsers = userService.getPendingUsers();
            List<Map<String, Object>> response = pendingUsers.stream()
                .map(this::mapUserToAdminResponse)
                .collect(Collectors.toList());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            System.err.println("Error getting pending users: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(new ArrayList<>());
        }
    }

    /**
     * Approve a pending user
     */
    @PostMapping("/{userId}/approve")
    public ResponseEntity<Map<String, Object>> approveUser(@PathVariable String userId) {
        try {
            UserDTO approvedUser = userService.approveUser(userId);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "User approved successfully");
            response.put("user", mapUserToAdminResponse(approvedUser));
            return ResponseEntity.ok(response);
        } catch (UserNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            System.err.println("Error approving user: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(createErrorResponse("Failed to approve user: " + e.getMessage()));
        }
    }

    /**
     * Reject a pending user (delete their account)
     */
    @DeleteMapping("/{userId}/reject")
    public ResponseEntity<Map<String, Object>> rejectUser(@PathVariable String userId) {
        try {
            userService.rejectUser(userId);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "User rejected and account deleted successfully");
            return ResponseEntity.ok(response);
        } catch (UserNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            System.err.println("Error rejecting user: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(createErrorResponse("Failed to reject user: " + e.getMessage()));
        }
    }

    /**
     * Update admin location and department for testing
     */
    @PostMapping("/update-admin-location")
    public ResponseEntity<Map<String, Object>> updateAdminLocation(
            @RequestParam String adminId,
            @RequestParam String location,
            @RequestParam String department) {
        try {
            Admin admin = adminService.getAdminById(adminId);
            if (admin != null) {
                admin.setLocation(location);
                admin.setDepartment(department);
                
                // Save the admin to persist the changes
                adminService.updateAdmin(admin);
                
                System.out.println("Updated and saved admin " + admin.getUsername() + " with location: " + location + ", department: " + department);
                
                Map<String, Object> response = new HashMap<>();
                response.put("success", true);
                response.put("message", "Admin location and department updated successfully");
                response.put("adminId", adminId);
                response.put("location", location);
                response.put("department", department);
                return ResponseEntity.ok(response);
            } else {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "Admin not found");
                return ResponseEntity.notFound().build();
            }
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "Error updating admin: " + e.getMessage());
            return ResponseEntity.internalServerError().body(response);
        }
    }
    
    /**
     * Create a simple admin for testing purposes
     */
    @PostMapping("/admin/create-simple")
    public ResponseEntity<?> createSimpleAdmin(@RequestBody Map<String, String> request) {
        try {
            String username = request.get("username");
            String password = request.get("password");
            String location = request.get("location");
            String department = request.get("department");
            
            if (username == null || password == null || location == null || department == null) {
                return ResponseEntity.badRequest().body(Map.of(
                    "error", "username, password, location, and department are required"
                ));
            }
            
            // Create admin with basic fields
            Admin admin = new Admin();
            admin.setId(username); // Use username as ID for simplicity
            admin.setUsername(username);
            admin.setPassword(password);
            admin.setLocation(location);
            admin.setDepartment(department);
            admin.setRole("ADMIN");
            admin.setCreatedAt(java.time.LocalDateTime.now());
            
            // Try to save
            adminService.save(admin);
            
            logger.info("Created simple admin {} with location: {} and department: {}", 
                username, location, department);
            
            return ResponseEntity.ok(Map.of(
                "message", "Simple admin created successfully",
                "admin", Map.of(
                    "id", admin.getId(),
                    "username", admin.getUsername(),
                    "location", admin.getLocation(),
                    "department", admin.getDepartment(),
                    "role", admin.getRole()
                )
            ));
        } catch (Exception e) {
            logger.error("Error creating simple admin: ", e);
            return ResponseEntity.status(500).body(Map.of(
                "error", "Failed to create simple admin: " + e.getMessage()
            ));
        }
    }

    private Map<String, Object> createErrorResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("message", message);
        return response;
    }
}
