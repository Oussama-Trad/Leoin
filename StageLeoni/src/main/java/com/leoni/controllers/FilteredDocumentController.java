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

/**
 * Contrôleur pour la gestion des documents avec filtrage par département/location
 * Utilise l'API Flask pour récupérer et gérer les documents filtrés
 */
@RestController
@RequestMapping("/api/admin/flask-documents")
@CrossOrigin(origins = "*")
public class FilteredDocumentController {

    @Autowired
    private AuthService authService;

    @Autowired
    private FlaskApiService flaskApiService;

    /**
     * Récupérer les demandes de documents filtrées selon les permissions admin
     * @param authorization token d'authentification
     * @param status statut des documents à filtrer (optionnel)
     * @param type type de document à filtrer (optionnel)
     * @return liste des demandes de documents filtrées
     */
    @GetMapping("/requests")
    public ResponseEntity<Map<String, Object>> getFilteredDocumentRequests(
            @RequestHeader("Authorization") String authorization,
            @RequestParam(value = "status", required = false) String status,
            @RequestParam(value = "type", required = false) String type) {
        
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
            
            // Récupérer les documents via Flask API
            List<Map<String, Object>> documents = flaskApiService.getFilteredDocumentRequests(
                token.startsWith("admin-token-") || token.startsWith("superadmin-token-") ? null : token,
                filterParams.get("department"),
                filterParams.get("location"),
                filterParams.get("role")
            );
            
            // Filtrer par statut si spécifié
            if (status != null && !status.isEmpty()) {
                documents = documents.stream()
                    .filter(doc -> status.equals(doc.get("status")))
                    .toList();
            }
            
            // Filtrer par type si spécifié
            if (type != null && !type.isEmpty()) {
                documents = documents.stream()
                    .filter(doc -> type.equals(doc.get("documentType")))
                    .toList();
            }
            
            response.put("success", true);
            response.put("documents", documents);
            response.put("count", documents.size());
            response.put("filters", Map.of(
                "status", status != null ? status : "all",
                "type", type != null ? type : "all"
            ));
            response.put("adminScope", Map.of(
                "role", admin.getRole(),
                "department", admin.getDepartment() != null ? admin.getDepartment() : "ALL",
                "location", admin.getLocation() != null ? admin.getLocation() : "ALL"
            ));
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la récupération des documents: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    /**
     * Mettre à jour le statut d'une demande de document
     * @param authorization token d'authentification
     * @param documentId ID du document
     * @param requestBody nouveau statut
     * @return résultat de la mise à jour
     */
    @PutMapping("/{documentId}/status")
    public ResponseEntity<Map<String, Object>> updateDocumentStatus(
            @RequestHeader("Authorization") String authorization,
            @PathVariable String documentId,
            @RequestBody Map<String, String> requestBody) {
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            String token = authorization.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                response.put("success", false);
                response.put("message", "Token invalide");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
            }
            
            String newStatus = requestBody.get("newStatus");
            if (newStatus == null || newStatus.isEmpty()) {
                response.put("success", false);
                response.put("message", "Nouveau statut requis");
                return ResponseEntity.badRequest().body(response);
            }
            
            // Valider les statuts autorisés
            if (!List.of("pending", "approved", "rejected", "processing").contains(newStatus.toLowerCase())) {
                response.put("success", false);
                response.put("message", "Statut invalide. Statuts autorisés: pending, approved, rejected, processing");
                return ResponseEntity.badRequest().body(response);
            }
            
            // Mettre à jour via Flask API
            boolean updated = flaskApiService.updateDocumentStatus(
                token.startsWith("admin-token-") || token.startsWith("superadmin-token-") ? null : token,
                documentId,
                newStatus
            );
            
            if (updated) {
                response.put("success", true);
                response.put("message", "Statut du document mis à jour avec succès");
                response.put("documentId", documentId);
                response.put("newStatus", newStatus);
            } else {
                response.put("success", false);
                response.put("message", "Échec de la mise à jour du statut");
            }
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la mise à jour: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    /**
     * Récupérer les statistiques des documents par statut
     * @param authorization token d'authentification
     * @return statistiques des documents
     */
    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getDocumentStatistics(
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
            
            // Récupérer tous les documents selon les permissions
            List<Map<String, Object>> documents = flaskApiService.getFilteredDocumentRequests(
                token.startsWith("admin-token-") || token.startsWith("superadmin-token-") ? null : token,
                filterParams.get("department"),
                filterParams.get("location"),
                filterParams.get("role")
            );
            
            // Calculer les statistiques
            Map<String, Integer> statusStats = new HashMap<>();
            Map<String, Integer> typeStats = new HashMap<>();
            int totalDocuments = documents.size();
            
            for (Map<String, Object> document : documents) {
                String status = (String) document.get("status");
                String type = (String) document.get("documentType");
                
                if (status != null) {
                    statusStats.put(status, statusStats.getOrDefault(status, 0) + 1);
                }
                if (type != null) {
                    typeStats.put(type, typeStats.getOrDefault(type, 0) + 1);
                }
            }
            
            response.put("success", true);
            response.put("totalDocuments", totalDocuments);
            response.put("statusStatistics", statusStats);
            response.put("typeStatistics", typeStats);
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
     * Approuver plusieurs documents en lot
     * @param authorization token d'authentification
     * @param requestBody liste des IDs de documents et nouveau statut
     * @return résultat des mises à jour en lot
     */
    @PutMapping("/batch-update")
    public ResponseEntity<Map<String, Object>> batchUpdateDocuments(
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
            
            @SuppressWarnings("unchecked")
            List<String> documentIds = (List<String>) requestBody.get("documentIds");
            String newStatus = (String) requestBody.get("newStatus");
            
            if (documentIds == null || documentIds.isEmpty()) {
                response.put("success", false);
                response.put("message", "Liste des IDs de documents requise");
                return ResponseEntity.badRequest().body(response);
            }
            
            if (newStatus == null || newStatus.isEmpty()) {
                response.put("success", false);
                response.put("message", "Nouveau statut requis");
                return ResponseEntity.badRequest().body(response);
            }
            
            // Valider le statut
            if (!List.of("pending", "approved", "rejected", "processing").contains(newStatus.toLowerCase())) {
                response.put("success", false);
                response.put("message", "Statut invalide");
                return ResponseEntity.badRequest().body(response);
            }
            
            // Mettre à jour chaque document
            int successCount = 0;
            int failCount = 0;
            
            for (String documentId : documentIds) {
                boolean updated = flaskApiService.updateDocumentStatus(
                    token.startsWith("admin-token-") || token.startsWith("superadmin-token-") ? null : token,
                    documentId,
                    newStatus
                );
                
                if (updated) {
                    successCount++;
                } else {
                    failCount++;
                }
            }
            
            response.put("success", true);
            response.put("message", String.format("Mise à jour terminée: %d succès, %d échecs", successCount, failCount));
            response.put("successCount", successCount);
            response.put("failCount", failCount);
            response.put("totalProcessed", documentIds.size());
            response.put("newStatus", newStatus);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la mise à jour en lot: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
}
