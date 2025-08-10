package com.leoni.controllers;

import com.leoni.models.User;
import com.leoni.repositories.UserRepository;
import com.leoni.services.UnifiedAuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.util.*;

@RestController
@RequestMapping("/dashboard/api/employees")
public class EmployeeManagementController {
    
    private static final Logger logger = LoggerFactory.getLogger(EmployeeManagementController.class);
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private UnifiedAuthService authService;
    
    @Autowired
    private MongoTemplate mongoTemplate;
    
    /**
     * Get employees with pagination and filters
     */
    @GetMapping
    public ResponseEntity<Map<String, Object>> getEmployees(
            @RequestHeader("Authorization") String authHeader,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) String location,
            @RequestParam(required = false) String status) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String role = authService.getRoleFromToken(token);
            String adminDepartment = authService.getDepartmentFromToken(token);
            String adminLocation = authService.getLocationFromToken(token);
            boolean isSuperAdmin = "SUPERADMIN".equals(role);
            
            // Build query criteria
            Criteria criteria = new Criteria();
            List<Criteria> conditions = new ArrayList<>();
            
            // Filter by admin's scope if not superadmin
            if (!isSuperAdmin) {
                if (adminDepartment != null) {
                    conditions.add(Criteria.where("department").is(adminDepartment));
                }
                if (adminLocation != null) {
                    conditions.add(Criteria.where("location").is(adminLocation));
                }
            }
            
            // Apply additional filters
            if (search != null && !search.trim().isEmpty()) {
                conditions.add(new Criteria().orOperator(
                    Criteria.where("firstName").regex(search, "i"),
                    Criteria.where("lastName").regex(search, "i"),
                    Criteria.where("email").regex(search, "i"),
                    Criteria.where("employeeId").regex(search, "i")
                ));
            }
            
            if (department != null && !department.trim().isEmpty() && !department.equals("all")) {
                conditions.add(Criteria.where("department").is(department));
            }
            
            if (location != null && !location.trim().isEmpty() && !location.equals("all")) {
                conditions.add(Criteria.where("location").is(location));
            }
            
            if (status != null && !status.trim().isEmpty() && !status.equals("all")) {
                conditions.add(Criteria.where("status").is(status));
            }
            
            if (!conditions.isEmpty()) {
                criteria = criteria.andOperator(conditions.toArray(new Criteria[0]));
            }
            
            // Create pageable
            Sort sort = Sort.by(Sort.Direction.DESC, "createdAt");
            Pageable pageable = PageRequest.of(page, size, sort);
            
            // Execute query
            Query query = Query.query(criteria).with(pageable);
            List<User> employees = mongoTemplate.find(query, User.class);
            long totalElements = mongoTemplate.count(Query.query(criteria), User.class);
            
            // Build response
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("employees", employees);
            response.put("totalElements", totalElements);
            response.put("totalPages", (int) Math.ceil((double) totalElements / size));
            response.put("currentPage", page);
            response.put("size", size);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Error fetching employees", e);
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la récupération des employés"));
        }
    }
    
    /**
     * Get employee by ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getEmployeeById(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable String id) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            Optional<User> employee = userRepository.findById(id);
            
            if (!employee.isPresent()) {
                return ResponseEntity.status(404)
                    .body(Map.of("success", false, "message", "Employé non trouvé"));
            }
            
            return ResponseEntity.ok(Map.of("success", true, "employee", employee.get()));
            
        } catch (Exception e) {
            logger.error("Error fetching employee by ID", e);
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la récupération de l'employé"));
        }
    }
    
    /**
     * Create new employee
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createEmployee(
            @RequestHeader("Authorization") String authHeader,
            @RequestBody User employee) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            // Validate required fields
            if (employee.getFirstName() == null || employee.getLastName() == null || 
                employee.getEmail() == null) {
                return ResponseEntity.badRequest()
                    .body(Map.of("success", false, "message", "Prénom, nom et email sont obligatoires"));
            }
            
            // Check if email already exists
            Query existingQuery = Query.query(Criteria.where("email").is(employee.getEmail()));
            if (mongoTemplate.exists(existingQuery, User.class)) {
                return ResponseEntity.badRequest()
                    .body(Map.of("success", false, "message", "Un employé avec cet email existe déjà"));
            }
            
            // Set defaults
            employee.setCreatedAt(new Date());
            employee.setUpdatedAt(new Date());
            if (employee.getStatus() == null) {
                employee.setStatus("approved");
            }
            if (employee.getPosition() == null) {
                employee.setPosition("Non spécifié");
            }
            
            User savedEmployee = userRepository.save(employee);
            
            return ResponseEntity.ok(Map.of("success", true, "employee", savedEmployee));
            
        } catch (Exception e) {
            logger.error("Error creating employee", e);
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la création de l'employé"));
        }
    }
    
    /**
     * Update employee
     */
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateEmployee(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable String id,
            @RequestBody User updatedEmployee) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            Optional<User> existingEmployee = userRepository.findById(id);
            if (!existingEmployee.isPresent()) {
                return ResponseEntity.status(404)
                    .body(Map.of("success", false, "message", "Employé non trouvé"));
            }
            
            User employee = existingEmployee.get();
            
            // Update fields
            if (updatedEmployee.getFirstName() != null) {
                employee.setFirstName(updatedEmployee.getFirstName());
            }
            if (updatedEmployee.getLastName() != null) {
                employee.setLastName(updatedEmployee.getLastName());
            }
            if (updatedEmployee.getEmail() != null) {
                employee.setEmail(updatedEmployee.getEmail());
            }
            if (updatedEmployee.getPhoneNumber() != null) {
                employee.setPhoneNumber(updatedEmployee.getPhoneNumber());
            }
            if (updatedEmployee.getDepartment() != null) {
                employee.setDepartment(updatedEmployee.getDepartment());
            }
            if (updatedEmployee.getLocation() != null) {
                employee.setLocation(updatedEmployee.getLocation());
            }
            if (updatedEmployee.getPosition() != null) {
                employee.setPosition(updatedEmployee.getPosition());
            }
            if (updatedEmployee.getStatus() != null) {
                employee.setStatus(updatedEmployee.getStatus());
            }
            
            employee.setUpdatedAt(new Date());
            
            User savedEmployee = userRepository.save(employee);
            
            return ResponseEntity.ok(Map.of("success", true, "employee", savedEmployee));
            
        } catch (Exception e) {
            logger.error("Error updating employee", e);
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la mise à jour de l'employé"));
        }
    }
    
    /**
     * Delete employee
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteEmployee(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable String id) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            if (!userRepository.existsById(id)) {
                return ResponseEntity.status(404)
                    .body(Map.of("success", false, "message", "Employé non trouvé"));
            }
            
            userRepository.deleteById(id);
            
            return ResponseEntity.ok(Map.of("success", true, "message", "Employé supprimé avec succès"));
            
        } catch (Exception e) {
            logger.error("Error deleting employee", e);
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la suppression de l'employé"));
        }
    }
    
    /**
     * Get employee statistics
     */
    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getStatistics(
            @RequestHeader("Authorization") String authHeader) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String role = authService.getRoleFromToken(token);
            String adminDepartment = authService.getDepartmentFromToken(token);
            String adminLocation = authService.getLocationFromToken(token);
            boolean isSuperAdmin = "SUPERADMIN".equals(role);
            
            // Build base query for admin scope
            final Criteria baseCriteria;
            if (!isSuperAdmin) {
                List<Criteria> conditions = new ArrayList<>();
                if (adminDepartment != null) {
                    conditions.add(Criteria.where("department").is(adminDepartment));
                }
                if (adminLocation != null) {
                    conditions.add(Criteria.where("location").is(adminLocation));
                }
                if (!conditions.isEmpty()) {
                    baseCriteria = new Criteria().andOperator(conditions.toArray(new Criteria[0]));
                } else {
                    baseCriteria = new Criteria();
                }
            } else {
                baseCriteria = new Criteria();
            }
            
            Map<String, Object> stats = new HashMap<>();
            
            // Total employees
            long totalEmployees = mongoTemplate.count(Query.query(baseCriteria), User.class);
            stats.put("totalEmployees", totalEmployees);
            
            // By status
            Arrays.asList("approved", "pending", "rejected").forEach(status -> {
                Criteria statusCriteria = new Criteria().andOperator(
                    baseCriteria, Criteria.where("status").is(status)
                );
                long count = mongoTemplate.count(Query.query(statusCriteria), User.class);
                stats.put("status_" + status, count);
            });
            
            // By department (if superadmin)
            if (isSuperAdmin) {
                List<Map> departmentStatsRaw = mongoTemplate.aggregate(
                    org.springframework.data.mongodb.core.aggregation.Aggregation.newAggregation(
                        org.springframework.data.mongodb.core.aggregation.Aggregation.match(baseCriteria),
                        org.springframework.data.mongodb.core.aggregation.Aggregation.group("department").count().as("count"),
                        org.springframework.data.mongodb.core.aggregation.Aggregation.project("count").and("_id").as("department")
                    ), User.class, Map.class
                ).getMappedResults();
                
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> departmentStats = (List<Map<String, Object>>) (List<?>) departmentStatsRaw;
                
                stats.put("departmentStats", departmentStats);
            }
            
            return ResponseEntity.ok(Map.of("success", true, "statistics", stats));
            
        } catch (Exception e) {
            logger.error("Error fetching employee statistics", e);
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la récupération des statistiques"));
        }
    }
    
    /**
     * Get distinct departments and locations for filters
     */
    @GetMapping("/filters")
    public ResponseEntity<Map<String, Object>> getFilters(
            @RequestHeader("Authorization") String authHeader) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String role = authService.getRoleFromToken(token);
            boolean isSuperAdmin = "SUPERADMIN".equals(role);
            
            Map<String, Object> filters = new HashMap<>();
            
            if (isSuperAdmin) {
                List<String> departments = mongoTemplate.findDistinct("department", User.class, String.class);
                List<String> locations = mongoTemplate.findDistinct("location", User.class, String.class);
                
                filters.put("departments", departments);
                filters.put("locations", locations);
            } else {
                // For regular admins, they can only see their own department/location
                String adminDepartment = authService.getDepartmentFromToken(token);
                String adminLocation = authService.getLocationFromToken(token);
                
                filters.put("departments", adminDepartment != null ? List.of(adminDepartment) : List.of());
                filters.put("locations", adminLocation != null ? List.of(adminLocation) : List.of());
            }
            
            List<String> statuses = Arrays.asList("approved", "pending", "rejected");
            filters.put("statuses", statuses);
            
            return ResponseEntity.ok(Map.of("success", true, "filters", filters));
            
        } catch (Exception e) {
            logger.error("Error fetching filters", e);
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la récupération des filtres"));
        }
    }
}
