package com.leoni.controllers;

import com.leoni.models.Chat;
import com.leoni.models.ChatMessage;
import com.leoni.models.DocumentRequest;
import com.leoni.services.ChatSyncService;
import com.leoni.services.DocumentSyncService;
import com.leoni.services.UnifiedAuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Contrôleur unifié pour la synchronisation avec l'application mobile
 */
@RestController
@RequestMapping("/api/sync")
@CrossOrigin(origins = "*")
public class UnifiedSyncController {
    
    @Autowired
    private ChatSyncService chatSyncService;
    
    @Autowired
    private DocumentSyncService documentSyncService;
    
    @Autowired
    private UnifiedAuthService authService;
    
    /**
     * Récupérer les conversations pour l'interface admin avec synchronisation mobile
     */
    @GetMapping("/chats")
    public ResponseEntity<Map<String, Object>> getAdminChats(
            @RequestHeader("Authorization") String authHeader,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String status) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String role = authService.getRoleFromToken(token);
            String department = authService.getDepartmentFromToken(token);
            String location = authService.getLocationFromToken(token);
            
            Page<Chat> chats = chatSyncService.getFilteredChatsForAdmin(
                department, location, role, page, size, status
            );
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("conversations", chats.getContent());
            response.put("totalElements", chats.getTotalElements());
            response.put("totalPages", chats.getTotalPages());
            response.put("currentPage", page);
            response.put("size", size);
            response.put("adminRole", role);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la récupération des conversations"));
        }
    }
    
    /**
     * Récupérer une conversation avec ses messages
     */
    @GetMapping("/chats/{chatId}")
    public ResponseEntity<Map<String, Object>> getChatWithMessages(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable String chatId) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String role = authService.getRoleFromToken(token);
            String department = authService.getDepartmentFromToken(token);
            String location = authService.getLocationFromToken(token);
            
            Map<String, Object> chatData = chatSyncService.getChatWithMessages(
                chatId, department, location, role
            );
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.putAll(chatData);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", e.getMessage()));
        }
    }
    
    /**
     * Répondre à une conversation
     */
    @PostMapping("/chats/{chatId}/reply")
    public ResponseEntity<Map<String, Object>> replyToChat(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable String chatId,
            @RequestBody Map<String, String> request) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String message = request.get("message");
            if (message == null || message.trim().isEmpty()) {
                return ResponseEntity.badRequest()
                    .body(Map.of("success", false, "message", "Message requis"));
            }
            
            String adminId = authService.getUserIdFromToken(token);
            String adminName = authService.getUsernameFromToken(token);
            
            ChatMessage chatMessage = chatSyncService.replyToChat(chatId, adminId, adminName, message.trim());
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "Réponse envoyée avec succès",
                "messageId", chatMessage.getId()
            ));
            
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", e.getMessage()));
        }
    }
    
    /**
     * Mettre à jour le statut d'une conversation
     */
    @PutMapping("/chats/{chatId}/status")
    public ResponseEntity<Map<String, Object>> updateChatStatus(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable String chatId,
            @RequestBody Map<String, String> request) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String newStatus = request.get("status");
            if (newStatus == null || newStatus.trim().isEmpty()) {
                return ResponseEntity.badRequest()
                    .body(Map.of("success", false, "message", "Statut requis"));
            }
            
            String adminId = authService.getUserIdFromToken(token);
            String adminName = authService.getUsernameFromToken(token);
            
            Chat updatedChat = chatSyncService.updateChatStatus(chatId, newStatus, adminId, adminName);
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "Statut mis à jour avec succès",
                "chat", updatedChat
            ));
            
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", e.getMessage()));
        }
    }
    
    /**
     * Récupérer les demandes de documents pour l'interface admin
     */
    @GetMapping("/documents")
    public ResponseEntity<Map<String, Object>> getAdminDocuments(
            @RequestHeader("Authorization") String authHeader,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String status) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String role = authService.getRoleFromToken(token);
            String department = authService.getDepartmentFromToken(token);
            String location = authService.getLocationFromToken(token);
            
            Page<DocumentRequest> requests = documentSyncService.getFilteredDocumentRequestsForAdmin(
                department, location, role, page, size, status
            );
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("requests", requests.getContent());
            response.put("totalElements", requests.getTotalElements());
            response.put("totalPages", requests.getTotalPages());
            response.put("currentPage", page);
            response.put("size", size);
            response.put("adminRole", role);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la récupération des demandes"));
        }
    }
    
    /**
     * Traiter une demande de document
     */
    @PutMapping("/documents/{requestId}/process")
    public ResponseEntity<Map<String, Object>> processDocumentRequest(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable String requestId,
            @RequestBody Map<String, String> request) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String newStatus = request.get("newStatus");
            String comment = request.get("comment");
            
            if (newStatus == null || newStatus.trim().isEmpty()) {
                return ResponseEntity.badRequest()
                    .body(Map.of("success", false, "message", "Nouveau statut requis"));
            }
            
            String adminId = authService.getUserIdFromToken(token);
            String adminName = authService.getUsernameFromToken(token);
            
            DocumentRequest updatedRequest = documentSyncService.updateDocumentRequestStatus(
                requestId, newStatus, adminId, adminName, comment
            );
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "Demande traitée avec succès",
                "request", updatedRequest
            ));
            
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", e.getMessage()));
        }
    }
    
    /**
     * Récupérer les statistiques pour le dashboard admin
     */
    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getSyncStatistics(
            @RequestHeader("Authorization") String authHeader) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String role = authService.getRoleFromToken(token);
            String department = authService.getDepartmentFromToken(token);
            String location = authService.getLocationFromToken(token);
            
            // Récupérer les statistiques des chats
            Map<String, Object> chatStats = chatSyncService.getChatStatistics(department, location, role);
            
            // Récupérer les statistiques des documents
            Map<String, Object> docStats = documentSyncService.getDocumentStatistics(department, location, role);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("chatStatistics", chatStats);
            response.put("documentStatistics", docStats);
            response.put("adminRole", role);
            response.put("adminDepartment", department);
            response.put("adminLocation", location);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la récupération des statistiques"));
        }
    }
    
    /**
     * Rechercher dans les conversations
     */
    @GetMapping("/chats/search")
    public ResponseEntity<Map<String, Object>> searchChats(
            @RequestHeader("Authorization") String authHeader,
            @RequestParam String keyword) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String role = authService.getRoleFromToken(token);
            String department = authService.getDepartmentFromToken(token);
            String location = authService.getLocationFromToken(token);
            
            List<Chat> chats = chatSyncService.searchChats(keyword, department, location, role);
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "chats", chats,
                "count", chats.size(),
                "keyword", keyword
            ));
            
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la recherche"));
        }
    }
}