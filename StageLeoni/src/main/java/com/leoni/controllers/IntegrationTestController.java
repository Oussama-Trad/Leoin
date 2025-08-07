package com.leoni.controllers;

import com.leoni.dto.AuthRequest;
import com.leoni.dto.AuthResponse;
import com.leoni.models.Admin;
import com.leoni.services.AuthService;
import com.leoni.services.FlaskApiService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * Contrôleur pour la page de test du système de filtrage intégré
 * Permet de tester l'authentification Flask et le filtrage des employés
 */
@Controller
@RequestMapping("/test")
public class IntegrationTestController {

    @Autowired
    private AuthService authService;

    @Autowired
    private FlaskApiService flaskApiService;

    /**
     * Page de test principal
     */
    @GetMapping("/integration")
    public String testIntegrationPage(Model model) {
        model.addAttribute("pageTitle", "Test d'Intégration - Système de Filtrage");
        return "test/integration";
    }

    /**
     * Test d'authentification via Flask API
     */
    @PostMapping("/auth")
    @ResponseBody
    public Map<String, Object> testAuthentication(@RequestBody AuthRequest authRequest) {
        try {
            AuthResponse response = authService.authenticate(authRequest);
            
            if (response.isSuccess()) {
                return Map.of(
                    "success", true,
                    "message", "Authentification réussie",
                    "authResponse", response,
                    "flaskToken", response.getFlaskToken() != null ? "Token Flask présent" : "Token local uniquement"
                );
            } else {
                return Map.of(
                    "success", false,
                    "message", response.getMessage()
                );
            }
        } catch (Exception e) {
            return Map.of(
                "success", false,
                "message", "Erreur: " + e.getMessage()
            );
        }
    }

    /**
     * Test de récupération des employés filtrés
     */
    @PostMapping("/employees")
    @ResponseBody
    public Map<String, Object> testFilteredEmployees(@RequestBody Map<String, String> testRequest) {
        try {
            String token = testRequest.get("token");
            String department = testRequest.get("department");
            String location = testRequest.get("location");
            String role = testRequest.get("role");
            
            if (token == null || token.isEmpty()) {
                return Map.of(
                    "success", false,
                    "message", "Token requis"
                );
            }
            
            // Tester avec l'API Flask
            List<Map<String, Object>> employees = flaskApiService.getFilteredEmployees(token, department, location, role);
            
            return Map.of(
                "success", true,
                "message", "Employés récupérés avec succès",
                "employees", employees,
                "count", employees.size(),
                "testParams", Map.of(
                    "department", department != null ? department : "ALL",
                    "location", location != null ? location : "ALL",
                    "role", role != null ? role : "AUTO"
                )
            );
            
        } catch (Exception e) {
            return Map.of(
                "success", false,
                "message", "Erreur: " + e.getMessage()
            );
        }
    }

    /**
     * Test de récupération des départements et locations
     */
    @GetMapping("/departments-locations")
    @ResponseBody
    public Map<String, Object> testDepartmentsLocations() {
        try {
            Map<String, Object> result = flaskApiService.getDepartmentsAndLocations();
            
            return Map.of(
                "success", true,
                "message", "Départements et locations récupérés",
                "data", result
            );
            
        } catch (Exception e) {
            return Map.of(
                "success", false,
                "message", "Erreur: " + e.getMessage()
            );
        }
    }

    /**
     * Test de création d'actualité
     */
    @PostMapping("/news")
    @ResponseBody
    public Map<String, Object> testCreateNews(@RequestBody Map<String, Object> testRequest) {
        try {
            String token = (String) testRequest.get("token");
            String title = (String) testRequest.get("title");
            String content = (String) testRequest.get("content");
            @SuppressWarnings("unchecked")
            List<String> targetDepartments = (List<String>) testRequest.get("targetDepartments");
            @SuppressWarnings("unchecked")
            List<String> targetLocations = (List<String>) testRequest.get("targetLocations");
            
            if (token == null || token.isEmpty()) {
                return Map.of(
                    "success", false,
                    "message", "Token requis"
                );
            }
            
            boolean created = flaskApiService.createNews(token, title, content, targetDepartments, targetLocations);
            
            if (created) {
                return Map.of(
                    "success", true,
                    "message", "Actualité créée avec succès"
                );
            } else {
                return Map.of(
                    "success", false,
                    "message", "Échec de la création de l'actualité"
                );
            }
            
        } catch (Exception e) {
            return Map.of(
                "success", false,
                "message", "Erreur: " + e.getMessage()
            );
        }
    }

    /**
     * Test complet du système - Scénario admin
     */
    @PostMapping("/full-scenario")
    @ResponseBody
    public Map<String, Object> testFullScenario(@RequestBody AuthRequest authRequest) {
        try {
            // 1. Authentification
            AuthResponse authResponse = authService.authenticate(authRequest);
            if (!authResponse.isSuccess()) {
                return Map.of(
                    "success", false,
                    "step", "authentication",
                    "message", "Échec authentification: " + authResponse.getMessage()
                );
            }

            String token = authResponse.getFlaskToken() != null ? authResponse.getFlaskToken() : authResponse.getToken();
            
            // 2. Récupération des départements/locations
            Map<String, Object> deptLoc = flaskApiService.getDepartmentsAndLocations();
            
            // 3. Test filtrage employés (selon rôle)
            List<Map<String, Object>> employees = flaskApiService.getFilteredEmployees(
                token, 
                authResponse.getDepartment(), 
                authResponse.getLocation(), 
                authResponse.getRole()
            );
            
            // 4. Test documents (si implémenté)
            List<Map<String, Object>> documents = flaskApiService.getFilteredDocumentRequests(
                token,
                authResponse.getDepartment(),
                authResponse.getLocation(),
                authResponse.getRole()
            );

            return Map.of(
                "success", true,
                "message", "Scénario complet testé avec succès",
                "results", Map.of(
                    "authentication", Map.of(
                        "username", authResponse.getUsername(),
                        "role", authResponse.getRole(),
                        "department", authResponse.getDepartment() != null ? authResponse.getDepartment() : "N/A",
                        "location", authResponse.getLocation() != null ? authResponse.getLocation() : "N/A",
                        "tokenType", authResponse.getFlaskToken() != null ? "Flask JWT" : "Local Token"
                    ),
                    "departmentsLocations", deptLoc,
                    "employees", Map.of(
                        "count", employees.size(),
                        "data", employees.size() > 5 ? employees.subList(0, 5) : employees
                    ),
                    "documents", Map.of(
                        "count", documents.size(),
                        "data", documents.size() > 3 ? documents.subList(0, 3) : documents
                    )
                )
            );
            
        } catch (Exception e) {
            return Map.of(
                "success", false,
                "message", "Erreur dans le scénario complet: " + e.getMessage(),
                "error", e.getClass().getSimpleName()
            );
        }
    }
}
