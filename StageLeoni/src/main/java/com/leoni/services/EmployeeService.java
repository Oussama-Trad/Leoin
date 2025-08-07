package com.leoni.services;

import com.leoni.dto.UserDTO;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;

import java.util.List;
import java.util.Map;

@Service
public class EmployeeService {
    
    @Autowired
    private RestTemplate restTemplate;
    
    // Base URL for Python backend
    private static final String PYTHON_BACKEND_URL = "http://localhost:5000";
    
    /**
     * Get all employees from Python backend
     * @param authToken Authentication token
     * @return List of employees
     */
    public List<UserDTO> getAllEmployees(String authToken) {
        try {
            String url = PYTHON_BACKEND_URL + "/users";
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", "Bearer " + authToken);
            HttpEntity<String> entity = new HttpEntity<>(headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            Map<String, Object> responseBody = response.getBody();
            if (responseBody != null && responseBody.containsKey("users")) {
                // Convert response to UserDTO list
                // This would need proper mapping logic
                return null; // Placeholder
            }
            
            return null;
            
        } catch (Exception e) {
            System.out.println("Error getting employees: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Get filtered employees by department and location
     * @param authToken Authentication token
     * @param department Department filter
     * @param location Location filter
     * @param role Admin role
     * @return List of filtered employees
     */
    public Map<String, Object> getFilteredEmployees(String authToken, String department, String location, String role) {
        try {
            StringBuilder urlBuilder = new StringBuilder(PYTHON_BACKEND_URL + "/api/admin/employees/filtered");
            urlBuilder.append("?role=").append(role);
            
            if (department != null && !department.isEmpty()) {
                urlBuilder.append("&department=").append(department);
            }
            if (location != null && !location.isEmpty()) {
                urlBuilder.append("&location=").append(location);
            }
            
            String url = urlBuilder.toString();
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", "Bearer " + authToken);
            HttpEntity<String> entity = new HttpEntity<>(headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            return response.getBody();
            
        } catch (Exception e) {
            System.out.println("Error getting filtered employees: " + e.getMessage());
            return Map.of("success", false, "message", "Erreur lors de la récupération des employés");
        }
    }
    
    /**
     * Get employee by ID
     * @param employeeId Employee ID
     * @param authToken Authentication token
     * @return Employee details
     */
    public Map<String, Object> getEmployeeById(String employeeId, String authToken) {
        try {
            String url = PYTHON_BACKEND_URL + "/users/" + employeeId;
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", "Bearer " + authToken);
            HttpEntity<String> entity = new HttpEntity<>(headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            return response.getBody();
            
        } catch (Exception e) {
            System.out.println("Error getting employee by ID: " + e.getMessage());
            return Map.of("success", false, "message", "Erreur lors de la récupération de l'employé");
        }
    }
}
