package com.leoni.controllers;

import com.leoni.services.EmployeeService;
import com.leoni.services.AuthService;
import com.leoni.dto.UserDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin")
@CrossOrigin(origins = "*")
public class EmployeeController {
    
    @Autowired
    private EmployeeService employeeService;
    
    @Autowired
    private AuthService authService;
    
    @Autowired
    private RestTemplate restTemplate;
    
    // Base URL for Python backend
    private static final String PYTHON_BACKEND_URL = "http://localhost:5000";
    
    /**
     * Get filtered employees based on admin role and department/location
     * @param authHeader Authorization header with bearer token
     * @param department Optional department filter
     * @param location Optional location filter
     * @param role Admin role (ADMIN or SUPERADMIN)
     * @return List of filtered employees
     */
    @GetMapping("/employees/filtered")
    public ResponseEntity<?> getFilteredEmployees(
            @RequestHeader("Authorization") String authHeader,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) String location,
            @RequestParam(defaultValue = "ADMIN") String role) {
        
        System.out.println("=== GET FILTERED EMPLOYEES ===");
        System.out.println("Auth Header: " + authHeader);
        System.out.println("Department: " + department);
        System.out.println("Location: " + location);
        System.out.println("Role: " + role);
        
        try {
            // Validate token
            String token = authHeader.replace("Bearer ", "");
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of("success", false, "message", "Token invalide"));
            }
            
            // Build URL with parameters
            StringBuilder urlBuilder = new StringBuilder(PYTHON_BACKEND_URL + "/api/admin/employees/filtered");
            urlBuilder.append("?role=").append(role);
            
            if (department != null && !department.isEmpty()) {
                urlBuilder.append("&department=").append(department);
            }
            if (location != null && !location.isEmpty()) {
                urlBuilder.append("&location=").append(location);
            }
            
            String url = urlBuilder.toString();
            System.out.println("Calling Python backend: " + url);
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", authHeader);
            HttpEntity<String> entity = new HttpEntity<>(headers);
            
            // Call Python backend
            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            System.out.println("Response from Python backend: " + response.getStatusCode());
            
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            System.out.println("Error in getFilteredEmployees: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Erreur lors de la récupération des employés: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Get employee by ID
     * @param employeeId Employee ID
     * @param authHeader Authorization header
     * @return Employee details
     */
    @GetMapping("/employees/{employeeId}")
    public ResponseEntity<?> getEmployeeById(
            @PathVariable String employeeId,
            @RequestHeader("Authorization") String authHeader) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String url = PYTHON_BACKEND_URL + "/users/" + employeeId;
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", authHeader);
            HttpEntity<String> entity = new HttpEntity<>(headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            System.out.println("Error in getEmployeeById: " + e.getMessage());
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Erreur lors de la récupération de l'employé: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Get all departments and locations for admin filtering
     * @param authHeader Authorization header
     * @return Available departments and locations
     */
    @GetMapping("/departments-locations")
    public ResponseEntity<?> getDepartmentsAndLocations(@RequestHeader("Authorization") String authHeader) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of("success", false, "message", "Token invalide"));
            }
            
            // Get departments
            String deptUrl = PYTHON_BACKEND_URL + "/departments";
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", authHeader);
            HttpEntity<String> entity = new HttpEntity<>(headers);
            
            ResponseEntity<Map> deptResponse = restTemplate.exchange(
                deptUrl,
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            // Get locations
            String locUrl = PYTHON_BACKEND_URL + "/locations";
            ResponseEntity<Map> locResponse = restTemplate.exchange(
                locUrl,
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "departments", deptResponse.getBody().get("departments"),
                "locations", locResponse.getBody().get("locations")
            ));
            
        } catch (Exception e) {
            System.out.println("Error in getDepartmentsAndLocations: " + e.getMessage());
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Erreur lors de la récupération des données: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Get document requests filtered by department and location
     * @param authHeader Authorization header
     * @param department Optional department filter
     * @param location Optional location filter
     * @param role Admin role
     * @return Filtered document requests
     */
    @GetMapping("/document-requests/filtered")
    public ResponseEntity<?> getFilteredDocumentRequests(
            @RequestHeader("Authorization") String authHeader,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) String location,
            @RequestParam(defaultValue = "ADMIN") String role) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String url = PYTHON_BACKEND_URL + "/api/admin/document-requests/filtered";
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", authHeader);
            HttpEntity<String> entity = new HttpEntity<>(headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            System.out.println("Error in getFilteredDocumentRequests: " + e.getMessage());
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Erreur lors de la récupération des demandes: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Update document request status
     * @param authHeader Authorization header
     * @param updateRequest Update request containing requestId and newStatus
     * @return Update result
     */
    @PutMapping("/document-requests/update-status")
    public ResponseEntity<?> updateDocumentRequestStatus(
            @RequestHeader("Authorization") String authHeader,
            @RequestBody Map<String, String> updateRequest) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String url = PYTHON_BACKEND_URL + "/api/admin/document-requests/update-status";
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", authHeader);
            headers.set("Content-Type", "application/json");
            
            HttpEntity<Map<String, String>> entity = new HttpEntity<>(updateRequest, headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.PUT,
                entity,
                Map.class
            );
            
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            System.out.println("Error in updateDocumentRequestStatus: " + e.getMessage());
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Erreur lors de la mise à jour: " + e.getMessage()
            ));
        }
    }
}
