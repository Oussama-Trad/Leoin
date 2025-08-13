package com.leoni.controllers;

import com.leoni.models.Chat;
import com.leoni.models.ChatMessage;
import com.leoni.services.ChatSyncService;
import com.leoni.services.AuthService;
import com.leoni.services.UnifiedAuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Contrôleur pour la gestion des conversations de chat par les admins
 */
@Controller
@RequestMapping("/admin/chat")
public class AdminChatController {
    
    @Autowired
    private ChatSyncService chatSyncService;
    
    @Autowired
    private UnifiedAuthService authService;
    
    /**
     * Page principale de gestion des conversations unifiées
     */
    @GetMapping
    public String chatManagement(Model model, HttpServletRequest request,
                                @RequestParam(defaultValue = "0") int page,
                                @RequestParam(defaultValue = "10") int size,
                                @RequestParam(required = false) String status,
                                @RequestParam(required = false) String token) {
        
        try {
            // Extraire le token d'authentification
            String authToken = extractToken(token, request.getHeader("Authorization"));
            
            if (authToken == null || !authService.validateToken(authToken)) {
                return "redirect:/login";
            }
            
            // Récupérer les informations admin
            String role = authService.getRoleFromToken(authToken);
            String department = authService.getDepartmentFromToken(authToken);
            String location = authService.getLocationFromToken(authToken);
            String username = authService.getUsernameFromToken(authToken);
            
            // Récupérer les conversations filtrées
            Page<Chat> chats = chatSyncService.getFilteredChatsForAdmin(
                department, location, role, page, size, status
            );
            
            // Statistiques
            Map<String, Object> statistics = chatSyncService.getChatStatistics(department, location, role);
            
            // Ajouter au modèle
            model.addAttribute("chats", chats);
            model.addAttribute("statistics", statistics);
            model.addAttribute("username", username);
            model.addAttribute("role", role);
            model.addAttribute("department", department);
            model.addAttribute("location", location);
            model.addAttribute("isSuperAdmin", "SUPERADMIN".equals(role));
            model.addAttribute("currentPage", page);
            model.addAttribute("pageSize", size);
            model.addAttribute("selectedStatus", status);
            model.addAttribute("totalPages", chats.getTotalPages());
            model.addAttribute("totalElements", chats.getTotalElements());
            model.addAttribute("token", authToken);
            
            return "unified-chat-management";
            
        } catch (Exception e) {
            model.addAttribute("error", "Erreur lors du chargement des conversations: " + e.getMessage());
            return "unified-chat-management";
        }
    }
    
    /**
     * Page de détail d'une conversation
     */
    @GetMapping("/{chatId}")
    public String chatDetail(@PathVariable String chatId, Model model, 
                           @RequestParam(required = false) String token,
                           HttpServletRequest request) {
        
        try {
            // Extraire le token d'authentification
            String authToken = extractToken(token, request.getHeader("Authorization"));
            
            if (authToken == null || !authService.validateToken(authToken)) {
                return "redirect:/login";
            }
            
            // Récupérer les informations admin
            String role = authService.getRoleFromToken(authToken);
            String department = authService.getDepartmentFromToken(authToken);
            String location = authService.getLocationFromToken(authToken);
            
            // Récupérer la conversation avec messages
            Map<String, Object> chatData = chatSyncService.getChatWithMessages(chatId, department, location, role);
            
            model.addAttribute("chat", chatData.get("chat"));
            model.addAttribute("messages", chatData.get("messages"));
            model.addAttribute("messageCount", chatData.get("messageCount"));
            model.addAttribute("canReply", chatData.get("canReply"));
            model.addAttribute("token", authToken);
            
            return "admin/chat/chat-detail";
            
        } catch (Exception e) {
            model.addAttribute("error", "Erreur lors du chargement de la conversation: " + e.getMessage());
            return "redirect:/admin/login";
        }
    }
    
    /**
     * API REST: Récupérer les conversations avec synchronisation mobile
     */
    @GetMapping("/api/conversations")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> getConversations(
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            HttpServletRequest request,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String status) {
        
        try {
            // Extraire le token d'authentification
            String token = extractToken(request.getParameter("token"), authHeader);
            
            if (token == null || !authService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            // Récupérer les informations admin
            String role = authService.getRoleFromToken(token);
            String department = authService.getDepartmentFromToken(token);
            String location = authService.getLocationFromToken(token);
            
            // Récupérer les conversations avec synchronisation
            Page<Chat> chatsPage = chatSyncService.getFilteredChatsForAdmin(
                department, location, role, page, size, status
            );
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("conversations", chatsPage.getContent());
            response.put("total", chatsPage.getTotalElements());
            response.put("page", page);
            response.put("size", size);
            response.put("totalPages", chatsPage.getTotalPages());
            response.put("adminRole", role);
            
            System.out.println("AdminChatController: Trouvé " + chatsPage.getTotalElements() + " conversations synchronisées");
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            System.err.println("AdminChatController Conversations Exception: " + e.getMessage());
            e.printStackTrace();
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Erreur synchronisation: " + e.getMessage());
            errorResponse.put("conversations", new java.util.ArrayList<>());
            errorResponse.put("total", 0);
            errorResponse.put("page", page);
            errorResponse.put("size", size);
            return ResponseEntity.status(200).body(errorResponse); // Retourner 200 avec erreur pour éviter JS errors
        }
    }
    
    /**
     * API REST: Récupérer une conversation avec messages
     */
    @GetMapping("/api/{chatId}")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> getChatWithMessages(
            @PathVariable String chatId, 
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            HttpServletRequest request) {
        
        try {
            // Extraire le token d'authentification
            String token = extractToken(request.getParameter("token"), authHeader);
            
            if (token == null || !authService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            // Récupérer les informations admin
            String role = authService.getRoleFromToken(token);
            String department = authService.getDepartmentFromToken(token);
            String location = authService.getLocationFromToken(token);
            
            // Récupérer la conversation avec messages
            Map<String, Object> chatData = chatSyncService.getChatWithMessages(chatId, department, location, role);
            chatData.put("success", true);
            
            return ResponseEntity.ok(chatData);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", e.getMessage())
            );
        }
    }
    
    /**
     * API REST: Répondre à une conversation
     */
    @PostMapping("/api/{chatId}/reply")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> replyToChat(
            @PathVariable String chatId,
            @RequestBody Map<String, String> request,
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            HttpServletRequest httpRequest) {
        
        try {
            // Extraire le token d'authentification
            String token = extractToken(httpRequest.getParameter("token"), authHeader);
            
            if (token == null || !authService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            String message = request.get("message");
            if (message == null || message.trim().isEmpty()) {
                return ResponseEntity.status(400).body(
                    Map.of("success", false, "message", "Message requis")
                );
            }
            
            String adminId = authService.getUserIdFromToken(token);
            String adminName = authService.getUsernameFromToken(token);
            
            ChatMessage chatMessage = chatSyncService.replyToChat(chatId, adminId, adminName, message.trim());
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Réponse envoyée avec succès");
            response.put("messageId", chatMessage.getId());
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", e.getMessage())
            );
        }
    }
    
    /**
     * API REST: Changer le statut d'une conversation
     */
    @PutMapping("/api/{chatId}/status")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> updateChatStatus(
            @PathVariable String chatId,
            @RequestBody Map<String, String> request,
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            HttpServletRequest httpRequest) {
        
        try {
            // Extraire le token d'authentification
            String token = extractToken(httpRequest.getParameter("token"), authHeader);
            
            if (token == null || !authService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            String newStatus = request.get("status");
            if (newStatus == null || newStatus.trim().isEmpty()) {
                return ResponseEntity.status(400).body(
                    Map.of("success", false, "message", "Statut requis")
                );
            }
            
            String adminId = authService.getUserIdFromToken(token);
            String adminName = authService.getUsernameFromToken(token);
            
            Chat updatedChat = chatSyncService.updateChatStatus(chatId, newStatus, adminId, adminName);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("chat", updatedChat);
            response.put("message", "Statut mis à jour avec succès");
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", e.getMessage())
            );
        }
    }
    
    /**
     * API REST: Rechercher des conversations
     */
    @GetMapping("/api/search")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> searchChats(
            @RequestParam String keyword,
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            HttpServletRequest httpRequest) {
        
        try {
            // Extraire le token d'authentification
            String token = extractToken(httpRequest.getParameter("token"), authHeader);
            
            if (token == null || !authService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            String role = authService.getRoleFromToken(token);
            String department = authService.getDepartmentFromToken(token);
            String location = authService.getLocationFromToken(token);
            
            List<Chat> chats = chatSyncService.searchChats(keyword, department, location, role);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("chats", chats);
            response.put("count", chats.size());
            response.put("keyword", keyword);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", e.getMessage())
            );
        }
    }
    
    /**
     * API REST: Statistiques des conversations avec synchronisation
     */
    @GetMapping("/api/statistics")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> getChatStatistics(
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            HttpServletRequest request) {
        
        try {
            // Extraire le token d'authentification
            String token = extractToken(request.getParameter("token"), authHeader);
            
            if (token == null || !authService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            String role = authService.getRoleFromToken(token);
            String department = authService.getDepartmentFromToken(token);
            String location = authService.getLocationFromToken(token);
            
            Map<String, Object> stats = chatSyncService.getChatStatistics(department, location, role);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("statistics", stats);
            response.put("adminRole", role);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            System.err.println("AdminChatController Stats Exception: " + e.getMessage());
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Erreur synchronisation: " + e.getMessage());
            errorResponse.put("statistics", Map.of(
                "totalConversations", 0,
                "openConversations", 0,
                "inProgressConversations", 0,
                "closedConversations", 0
            ));
            return ResponseEntity.status(200).body(errorResponse);
        }
    }
    
    /**
     * Extraire le token de différentes sources
     */
    private String extractToken(String tokenParam, String authHeader) {
        if (tokenParam != null && !tokenParam.trim().isEmpty()) {
            return tokenParam.trim();
        }
        
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            return authHeader.replace("Bearer ", "").trim();
        }
        
        return null;
    }
}
