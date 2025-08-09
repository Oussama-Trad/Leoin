package com.leoni.controllers;

import com.leoni.dto.UserDTO;
import com.leoni.models.DocumentRequest;
import com.leoni.services.AccessControlService;
import com.leoni.services.AuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.HashMap;

/**
 * Contrôleur pour la gestion des droits d'accès et du filtrage
 */
@RestController
@RequestMapping("/api/admin/access")
@CrossOrigin(origins = "*")
public class AccessControlController {
    
    @Autowired
    private AccessControlService accessControlService;
    
    @Autowired
    private AuthService authService;
    
    /**
     * Récupérer les employés filtrés selon les droits de l'admin
     */
    @GetMapping("/employees")
    public ResponseEntity<Map<String, Object>> getFilteredEmployees(
            @RequestHeader("Authorization") String authHeader,
            @RequestParam(required = false) String location,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) String status) {
        
        try {
            // Extraire et valider le token
            if (!authHeader.startsWith("Bearer ")) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Token d'autorisation requis")
                );
            }
            
            String token = authHeader.substring(7);
            String adminRole = authService.getRoleFromToken(token);
            String adminId = authService.getUserIdFromToken(token);
            
            if (adminRole == null || adminId == null) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            // Récupérer les employés filtrés
            List<UserDTO> employees = accessControlService.getFilteredEmployees(
                adminId, adminRole, location, department, status
            );
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("employees", employees);
            response.put("count", employees.size());
            response.put("adminRole", adminRole);
            response.put("filters", Map.of(
                "location", location != null ? location : "",
                "department", department != null ? department : "",
                "status", status != null ? status : ""
            ));
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            System.out.println("Error in getFilteredEmployees: " + e.getMessage());
            return ResponseEntity.internalServerError().body(
                Map.of("success", false, "message", "Erreur serveur: " + e.getMessage())
            );
        }
    }
    
    /**
     * Récupérer les demandes de documents filtrées selon les droits de l'admin
     */
    @GetMapping("/document-requests")
    public ResponseEntity<Map<String, Object>> getFilteredDocumentRequests(
            @RequestHeader("Authorization") String authHeader,
            @RequestParam(required = false) String status) {
        
        try {
            // Extraire et valider le token
            if (!authHeader.startsWith("Bearer ")) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Token d'autorisation requis")
                );
            }
            
            String token = authHeader.substring(7);
            String adminRole = authService.getRoleFromToken(token);
            String adminId = authService.getUserIdFromToken(token);
            
            if (adminRole == null || adminId == null) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            // Récupérer les demandes filtrées
            List<DocumentRequest> requests = accessControlService.getFilteredDocumentRequests(
                adminId, adminRole, status
            );
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("documentRequests", requests);
            response.put("count", requests.size());
            response.put("adminRole", adminRole);
            response.put("statusFilter", status != null ? status : "");
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            System.out.println("Error in getFilteredDocumentRequests: " + e.getMessage());
            return ResponseEntity.internalServerError().body(
                Map.of("success", false, "message", "Erreur serveur: " + e.getMessage())
            );
        }
    }
    
    /**
     * Vérifier l'accès à un employé spécifique
     */
    @GetMapping("/check-employee/{employeeId}")
    public ResponseEntity<Map<String, Object>> checkEmployeeAccess(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable String employeeId) {
        
        try {
            // Extraire et valider le token
            if (!authHeader.startsWith("Bearer ")) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Token d'autorisation requis")
                );
            }
            
            String token = authHeader.substring(7);
            String adminRole = authService.getRoleFromToken(token);
            String adminId = authService.getUserIdFromToken(token);
            
            if (adminRole == null || adminId == null) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            // Vérifier l'accès
            boolean hasAccess = accessControlService.canAccessEmployee(adminId, adminRole, employeeId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("hasAccess", hasAccess);
            response.put("employeeId", employeeId);
            response.put("adminRole", adminRole);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            System.out.println("Error in checkEmployeeAccess: " + e.getMessage());
            return ResponseEntity.internalServerError().body(
                Map.of("success", false, "message", "Erreur serveur: " + e.getMessage())
            );
        }
    }
    
    /**
     * Vérifier l'accès à une demande de document
     */
    @GetMapping("/check-document-request/{requestId}")
    public ResponseEntity<Map<String, Object>> checkDocumentRequestAccess(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable String requestId) {
        
        try {
            // Extraire et valider le token
            if (!authHeader.startsWith("Bearer ")) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Token d'autorisation requis")
                );
            }
            
            String token = authHeader.substring(7);
            String adminRole = authService.getRoleFromToken(token);
            String adminId = authService.getUserIdFromToken(token);
            
            if (adminRole == null || adminId == null) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            // Vérifier l'accès
            boolean canModify = accessControlService.canModifyDocumentRequest(adminId, adminRole, requestId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("canModify", canModify);
            response.put("requestId", requestId);
            response.put("adminRole", adminRole);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            System.out.println("Error in checkDocumentRequestAccess: " + e.getMessage());
            return ResponseEntity.internalServerError().body(
                Map.of("success", false, "message", "Erreur serveur: " + e.getMessage())
            );
        }
    }
    
    /**
     * Récupérer les options de filtrage disponibles pour l'admin
     */
    @GetMapping("/filtering-options")
    public ResponseEntity<Map<String, Object>> getFilteringOptions(
            @RequestHeader("Authorization") String authHeader) {
        
        try {
            // Extraire et valider le token
            if (!authHeader.startsWith("Bearer ")) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Token d'autorisation requis")
                );
            }
            
            String token = authHeader.substring(7);
            String adminRole = authService.getRoleFromToken(token);
            String adminId = authService.getUserIdFromToken(token);
            
            if (adminRole == null || adminId == null) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            // Récupérer les options
            AccessControlService.FilteringOptions options = accessControlService.getFilteringOptions(adminId, adminRole);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("locations", options.getLocations());
            response.put("departments", options.getDepartments());
            response.put("canFilterAll", options.isCanFilterAll());
            response.put("adminRole", adminRole);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            System.out.println("Error in getFilteringOptions: " + e.getMessage());
            return ResponseEntity.internalServerError().body(
                Map.of("success", false, "message", "Erreur serveur: " + e.getMessage())
            );
        }
    }
    
    /**
     * Récupérer les statistiques selon les droits de l'admin
     */
    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getAccessControlStatistics(
            @RequestHeader("Authorization") String authHeader) {
        
        try {
            // Extraire et valider le token
            if (!authHeader.startsWith("Bearer ")) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Token d'autorisation requis")
                );
            }
            
            String token = authHeader.substring(7);
            String adminRole = authService.getRoleFromToken(token);
            String adminId = authService.getUserIdFromToken(token);
            
            if (adminRole == null || adminId == null) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            // Récupérer les statistiques
            List<UserDTO> employees = accessControlService.getFilteredEmployees(adminId, adminRole, null, null, null);
            List<DocumentRequest> requests = accessControlService.getFilteredDocumentRequests(adminId, adminRole, null);
            
            // Calculer les statistiques
            long activeEmployees = employees.stream().filter(emp -> "active".equalsIgnoreCase(emp.getStatus())).count();
            long pendingRequests = requests.stream().filter(req -> 
                req.getStatus() != null && "en attente".equalsIgnoreCase(req.getStatus().getCurrent())
            ).count();
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("totalEmployees", employees.size());
            response.put("activeEmployees", activeEmployees);
            response.put("totalDocumentRequests", requests.size());
            response.put("pendingDocumentRequests", pendingRequests);
            response.put("adminRole", adminRole);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            System.out.println("Error in getAccessControlStatistics: " + e.getMessage());
            return ResponseEntity.internalServerError().body(
                Map.of("success", false, "message", "Erreur serveur: " + e.getMessage())
            );
        }
    }
}
