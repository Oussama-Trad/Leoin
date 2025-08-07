package com.leoni.controllers;

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
import java.util.Arrays;

/**
 * Contrôleur pour la gestion des actualités avec ciblage par département/location
 * Utilise l'API Flask pour créer et gérer les actualités avec ciblage avancé
 */
@RestController
@RequestMapping("/api/admin/flask-news")
@CrossOrigin(origins = "*")
public class FilteredNewsController {

    @Autowired
    private AuthService authService;

    @Autowired
    private FlaskApiService flaskApiService;

    /**
     * Créer une nouvelle actualité avec ciblage par département/location
     * @param authorization token d'authentification
     * @param requestBody données de l'actualité
     * @return résultat de la création
     */
    @PostMapping("/create")
    public ResponseEntity<Map<String, Object>> createNews(
            @RequestHeader("Authorization") String authorization,
            @RequestBody Map<String, Object> requestBody) {
        
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
            
            // Extraire les données de l'actualité
            String title = (String) requestBody.get("title");
            String content = (String) requestBody.get("content");
            @SuppressWarnings("unchecked")
            List<String> targetDepartments = (List<String>) requestBody.get("targetDepartments");
            @SuppressWarnings("unchecked")
            List<String> targetLocations = (List<String>) requestBody.get("targetLocations");
            
            // Validation des données requises
            if (title == null || title.trim().isEmpty()) {
                response.put("success", false);
                response.put("message", "Titre requis");
                return ResponseEntity.badRequest().body(response);
            }
            
            if (content == null || content.trim().isEmpty()) {
                response.put("success", false);
                response.put("message", "Contenu requis");
                return ResponseEntity.badRequest().body(response);
            }
            
            // Pour les ADMIN, limiter le ciblage à leur département/location
            if ("ADMIN".equals(admin.getRole())) {
                if (admin.getDepartment() != null) {
                    targetDepartments = Arrays.asList(admin.getDepartment());
                }
                if (admin.getLocation() != null) {
                    targetLocations = Arrays.asList(admin.getLocation());
                }
            }
            
            // Créer l'actualité via Flask API
            boolean created = flaskApiService.createNews(
                token.startsWith("admin-token-") || token.startsWith("superadmin-token-") ? null : token,
                title.trim(),
                content.trim(),
                targetDepartments != null ? targetDepartments : Arrays.asList(),
                targetLocations != null ? targetLocations : Arrays.asList()
            );
            
            if (created) {
                response.put("success", true);
                response.put("message", "Actualité créée avec succès");
                response.put("newsData", Map.of(
                    "title", title.trim(),
                    "targetDepartments", targetDepartments != null ? targetDepartments : Arrays.asList(),
                    "targetLocations", targetLocations != null ? targetLocations : Arrays.asList(),
                    "authorRole", admin.getRole()
                ));
            } else {
                response.put("success", false);
                response.put("message", "Échec de la création de l'actualité");
            }
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la création de l'actualité: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    /**
     * Récupérer les options de ciblage disponibles pour l'admin connecté
     * @param authorization token d'authentification
     * @return départements et locations disponibles pour le ciblage
     */
    @GetMapping("/targeting-options")
    public ResponseEntity<Map<String, Object>> getTargetingOptions(
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
            
            // Récupérer tous les départements et locations via Flask
            Map<String, Object> allOptions = flaskApiService.getDepartmentsAndLocations();
            
            if ("SUPERADMIN".equals(admin.getRole())) {
                // SUPERADMIN peut cibler n'importe quel département/location
                response.put("success", true);
                response.put("availableDepartments", allOptions.get("departments"));
                response.put("availableLocations", allOptions.get("locations"));
                response.put("canTargetAll", true);
            } else if ("ADMIN".equals(admin.getRole())) {
                // ADMIN ne peut cibler que son département/location
                response.put("success", true);
                response.put("availableDepartments", admin.getDepartment() != null ? 
                    Arrays.asList(admin.getDepartment()) : Arrays.asList());
                response.put("availableLocations", admin.getLocation() != null ? 
                    Arrays.asList(admin.getLocation()) : Arrays.asList());
                response.put("canTargetAll", false);
                response.put("restrictedTo", Map.of(
                    "department", admin.getDepartment() != null ? admin.getDepartment() : "N/A",
                    "location", admin.getLocation() != null ? admin.getLocation() : "N/A"
                ));
            }
            
            response.put("adminRole", admin.getRole());
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la récupération des options: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    /**
     * Prévisualiser le nombre d'employés qui recevront l'actualité
     * @param authorization token d'authentification
     * @param requestBody critères de ciblage
     * @return nombre d'employés ciblés
     */
    @PostMapping("/preview-audience")
    public ResponseEntity<Map<String, Object>> previewNewsAudience(
            @RequestHeader("Authorization") String authorization,
            @RequestBody Map<String, Object> requestBody) {
        
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
            
            @SuppressWarnings("unchecked")
            List<String> targetDepartments = (List<String>) requestBody.get("targetDepartments");
            @SuppressWarnings("unchecked")
            List<String> targetLocations = (List<String>) requestBody.get("targetLocations");
            
            // Pour les ADMIN, forcer leur département/location
            if ("ADMIN".equals(admin.getRole())) {
                if (admin.getDepartment() != null) {
                    targetDepartments = Arrays.asList(admin.getDepartment());
                }
                if (admin.getLocation() != null) {
                    targetLocations = Arrays.asList(admin.getLocation());
                }
            }
            
            // Compter les employés qui correspondent aux critères
            int targetedEmployeesCount = 0;
            
            if (targetDepartments != null && !targetDepartments.isEmpty()) {
                for (String department : targetDepartments) {
                    if (targetLocations != null && !targetLocations.isEmpty()) {
                        for (String location : targetLocations) {
                            List<Map<String, Object>> employees = flaskApiService.getFilteredEmployees(
                                token.startsWith("admin-token-") || token.startsWith("superadmin-token-") ? null : token,
                                department,
                                location,
                                "SUPERADMIN" // Pour compter tous les employés sans restriction
                            );
                            targetedEmployeesCount += employees.size();
                        }
                    } else {
                        List<Map<String, Object>> employees = flaskApiService.getFilteredEmployees(
                            token.startsWith("admin-token-") || token.startsWith("superadmin-token-") ? null : token,
                            department,
                            null,
                            "SUPERADMIN"
                        );
                        targetedEmployeesCount += employees.size();
                    }
                }
            } else if (targetLocations != null && !targetLocations.isEmpty()) {
                for (String location : targetLocations) {
                    List<Map<String, Object>> employees = flaskApiService.getFilteredEmployees(
                        token.startsWith("admin-token-") || token.startsWith("superadmin-token-") ? null : token,
                        null,
                        location,
                        "SUPERADMIN"
                    );
                    targetedEmployeesCount += employees.size();
                }
            } else {
                // Aucun filtre spécifique, compter selon les permissions admin
                Map<String, String> filterParams = authService.getFilteringParams(admin);
                List<Map<String, Object>> employees = flaskApiService.getFilteredEmployees(
                    token.startsWith("admin-token-") || token.startsWith("superadmin-token-") ? null : token,
                    filterParams.get("department"),
                    filterParams.get("location"),
                    filterParams.get("role")
                );
                targetedEmployeesCount = employees.size();
            }
            
            response.put("success", true);
            response.put("targetedEmployeesCount", targetedEmployeesCount);
            response.put("targetingCriteria", Map.of(
                "departments", targetDepartments != null ? targetDepartments : Arrays.asList(),
                "locations", targetLocations != null ? targetLocations : Arrays.asList()
            ));
            response.put("adminRole", admin.getRole());
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la prévisualisation: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    /**
     * Récupérer les templates d'actualités prédéfinis
     * @param authorization token d'authentification
     * @return liste des templates disponibles
     */
    @GetMapping("/templates")
    public ResponseEntity<Map<String, Object>> getNewsTemplates(
            @RequestHeader("Authorization") String authorization) {
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            String token = authorization.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                response.put("success", false);
                response.put("message", "Token invalide");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
            }
            
            // Templates prédéfinis pour différents types d'actualités
            List<Map<String, Object>> templates = Arrays.asList(
                Map.of(
                    "id", "welcome",
                    "name", "Message de bienvenue",
                    "title", "Bienvenue dans l'équipe !",
                    "content", "Nous sommes heureux de vous accueillir dans notre équipe. N'hésitez pas à nous contacter pour toute question.",
                    "category", "RH"
                ),
                Map.of(
                    "id", "announcement",
                    "name", "Annonce générale",
                    "title", "Annonce importante",
                    "content", "Nous tenons à vous informer de...",
                    "category", "Communication"
                ),
                Map.of(
                    "id", "meeting",
                    "name", "Convocation réunion",
                    "title", "Réunion d'équipe",
                    "content", "Une réunion d'équipe est prévue le [DATE] à [HEURE] en [LIEU]. Ordre du jour : [SUJET]",
                    "category", "Réunion"
                ),
                Map.of(
                    "id", "policy",
                    "name", "Nouvelle procédure",
                    "title", "Mise à jour des procédures",
                    "content", "Nous vous informons de la mise en place d'une nouvelle procédure concernant...",
                    "category", "Procédures"
                ),
                Map.of(
                    "id", "celebration",
                    "name", "Félicitations",
                    "title", "Félicitations !",
                    "content", "Nous tenons à féliciter [NOM] pour [RAISON]. Bravo !",
                    "category", "Célébration"
                )
            );
            
            response.put("success", true);
            response.put("templates", templates);
            response.put("count", templates.size());
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la récupération des templates: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
}
