package com.leoni.controllers;

import com.leoni.dto.AuthRequest;
import com.leoni.dto.AuthResponse;
import com.leoni.models.Admin;
import com.leoni.services.AuthService;
import com.leoni.services.FlaskApiService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Contrôleur principal pour la gestion des employés avec filtrage par département/location
 * Utilise l'API Flask pour récupérer les données filtrées
 */
@RestController
@RequestMapping("/api/admin/flask-employees")
@CrossOrigin(origins = "*")
public class FilteredEmployeeController {

    @Autowired
    private AuthService authService;

    @Autowired
    private FlaskApiService flaskApiService;

    /**
     * Récupérer les employés filtrés selon les permissions de l'admin
     * @param authorization token d'authentification
     * @param department département à filtrer (optionnel pour SUPERADMIN)
     * @param location location à filtrer (optionnel pour SUPERADMIN)
     * @return liste des employés filtrés
     */
    @GetMapping("/filtered")
    public ResponseEntity<Map<String, Object>> getFilteredEmployees(
            @RequestHeader("Authorization") String authorization,
            @RequestParam(value = "department", required = false) String department,
            @RequestParam(value = "location", required = false) String location) {
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            // Extraire le token
            String token = authorization.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                response.put("success", false);
                response.put("message", "Token invalide");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
            }
            
            // Décoder les informations admin du token
            Admin admin = authService.decodeAdminFromToken(token);
            if (admin == null) {
                // Fallback pour les tokens locaux
                String username = authService.getUsernameFromToken(token);
                String role = authService.getRoleFromToken(token);
                
                admin = new Admin();
                admin.setUsername(username);
                admin.setRole(role);
                // Pour les tokens locaux, on ne peut pas déterminer le département/location
            }
            
            // Préparer les paramètres de filtrage
            Map<String, String> filterParams = authService.getFilteringParams(admin);
            
            // Pour SUPERADMIN, utiliser les paramètres optionnels fournis
            if ("SUPERADMIN".equals(admin.getRole())) {
                if (department != null && !department.isEmpty()) {
                    filterParams.put("department", department);
                }
                if (location != null && !location.isEmpty()) {
                    filterParams.put("location", location);
                }
            }
            
            // Appeler l'API Flask pour récupérer les employés filtrés
            List<Map<String, Object>> employees = flaskApiService.getFilteredEmployees(
                token.startsWith("admin-token-") || token.startsWith("superadmin-token-") ? null : token,
                filterParams.get("department"),
                filterParams.get("location"),
                filterParams.get("role")
            );
            
            response.put("success", true);
            response.put("employees", employees);
            response.put("count", employees.size());
            response.put("adminInfo", Map.of(
                "username", admin.getUsername(),
                "role", admin.getRole(),
                "department", admin.getDepartment() != null ? admin.getDepartment() : "N/A",
                "location", admin.getLocation() != null ? admin.getLocation() : "N/A"
            ));
            response.put("filterApplied", filterParams);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la récupération des employés: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    /**
     * Récupérer les départements et locations disponibles
     * @param authorization token d'authentification
     * @return liste des départements et locations
     */
    @GetMapping("/departments-locations")
    public ResponseEntity<Map<String, Object>> getDepartmentsAndLocations(
            @RequestHeader("Authorization") String authorization) {
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            String token = authorization.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                response.put("success", false);
                response.put("message", "Token invalide");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
            }
            
            // Récupérer les départements et locations via Flask
            Map<String, Object> departmentsLocations = flaskApiService.getDepartmentsAndLocations();
            
            response.put("success", true);
            response.putAll(departmentsLocations);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la récupération des départements/locations: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    /**
     * Récupérer les statistiques des employés par département/location
     * @param authorization token d'authentification
     * @return statistiques des employés
     */
    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getEmployeeStatistics(
            @RequestHeader("Authorization") String authorization) {
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            String token = authorization.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                response.put("success", false);
                response.put("message", "Token invalide");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
            }
            
            Admin admin = authService.decodeAdminFromToken(token);
            if (admin == null) {
                String username = authService.getUsernameFromToken(token);
                String role = authService.getRoleFromToken(token);
                admin = new Admin();
                admin.setUsername(username);
                admin.setRole(role);
            }
            
            Map<String, String> filterParams = authService.getFilteringParams(admin);
            
            // Récupérer tous les employés selon les permissions
            List<Map<String, Object>> employees = flaskApiService.getFilteredEmployees(
                token.startsWith("admin-token-") || token.startsWith("superadmin-token-") ? null : token,
                filterParams.get("department"),
                filterParams.get("location"),
                filterParams.get("role")
            );
            
            // Calculer les statistiques
            Map<String, Integer> departmentStats = new HashMap<>();
            Map<String, Integer> locationStats = new HashMap<>();
            int totalEmployees = employees.size();
            
            for (Map<String, Object> employee : employees) {
                String dept = (String) employee.get("department");
                String loc = (String) employee.get("location");
                
                if (dept != null) {
                    departmentStats.put(dept, departmentStats.getOrDefault(dept, 0) + 1);
                }
                if (loc != null) {
                    locationStats.put(loc, locationStats.getOrDefault(loc, 0) + 1);
                }
            }
            
            response.put("success", true);
            response.put("totalEmployees", totalEmployees);
            response.put("departmentStatistics", departmentStats);
            response.put("locationStatistics", locationStats);
            response.put("adminScope", Map.of(
                "role", admin.getRole(),
                "department", admin.getDepartment() != null ? admin.getDepartment() : "ALL",
                "location", admin.getLocation() != null ? admin.getLocation() : "ALL"
            ));
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors du calcul des statistiques: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    /**
     * Rechercher des employés par nom avec filtrage
     * @param authorization token d'authentification
     * @param query terme de recherche
     * @return employés correspondant à la recherche
     */
    @GetMapping("/search")
    public ResponseEntity<Map<String, Object>> searchEmployees(
            @RequestHeader("Authorization") String authorization,
            @RequestParam("query") String query) {
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            String token = authorization.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                response.put("success", false);
                response.put("message", "Token invalide");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
            }
            
            Admin admin = authService.decodeAdminFromToken(token);
            if (admin == null) {
                String username = authService.getUsernameFromToken(token);
                String role = authService.getRoleFromToken(token);
                admin = new Admin();
                admin.setUsername(username);
                admin.setRole(role);
            }
            
            Map<String, String> filterParams = authService.getFilteringParams(admin);
            
            // Récupérer tous les employés selon les permissions
            List<Map<String, Object>> allEmployees = flaskApiService.getFilteredEmployees(
                token.startsWith("admin-token-") || token.startsWith("superadmin-token-") ? null : token,
                filterParams.get("department"),
                filterParams.get("location"),
                filterParams.get("role")
            );
            
            // Filtrer par le terme de recherche
            List<Map<String, Object>> filteredEmployees = allEmployees.stream()
                .filter(employee -> {
                    String firstName = (String) employee.get("firstName");
                    String lastName = (String) employee.get("lastName");
                    String email = (String) employee.get("email");
                    String fullName = (firstName != null ? firstName : "") + " " + (lastName != null ? lastName : "");
                    
                    return fullName.toLowerCase().contains(query.toLowerCase()) ||
                           (email != null && email.toLowerCase().contains(query.toLowerCase()));
                })
                .toList();
            
            response.put("success", true);
            response.put("employees", filteredEmployees);
            response.put("count", filteredEmployees.size());
            response.put("searchQuery", query);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la recherche: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
}
