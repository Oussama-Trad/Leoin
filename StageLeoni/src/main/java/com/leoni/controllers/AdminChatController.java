package com.leoni.controllers;

import com.leoni.models.Chat;
import com.leoni.models.ChatMessage;
import com.leoni.services.ChatService;
import com.leoni.services.AuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

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
    private ChatService chatService;
    
    @Autowired
    private AuthService authService;
    
    @Autowired
    private RestTemplate restTemplate;
    
    private final String PYTHON_BACKEND_URL = "http://localhost:5000";
    
    /**
     * Page principale de gestion des conversations
     */
    @GetMapping
    public String chatManagement(Model model, HttpServletRequest request,
                                @RequestParam(defaultValue = "0") int page,
                                @RequestParam(defaultValue = "10") int size,
                                @RequestParam(required = false) String status) {
        
        // Vérifier l'authentification
        String adminId = authService.getAuthenticatedAdminId(request);
        if (adminId == null) {
            return "redirect:/admin/login";
        }
        
        try {
            // Récupérer les conversations filtrées
            Page<Chat> chats = chatService.getFilteredChatsForAdmin(adminId, page, size, status);
            
            // Statistiques
            Map<String, Object> statistics = chatService.getChatStatistics(adminId);
            
            // Ajouter au modèle
            model.addAttribute("chats", chats);
            model.addAttribute("statistics", statistics);
            model.addAttribute("currentPage", page);
            model.addAttribute("pageSize", size);
            model.addAttribute("selectedStatus", status);
            model.addAttribute("totalPages", chats.getTotalPages());
            model.addAttribute("totalElements", chats.getTotalElements());
            
            return "admin/chat/chat-management";
            
        } catch (Exception e) {
            model.addAttribute("error", "Erreur lors du chargement des conversations: " + e.getMessage());
            return "admin/chat/chat-management";
        }
    }
    
    /**
     * Page de détail d'une conversation
     */
    @GetMapping("/{chatId}")
    public String chatDetail(@PathVariable String chatId, Model model, HttpServletRequest request) {
        
        String adminId = authService.getAuthenticatedAdminId(request);
        if (adminId == null) {
            return "redirect:/admin/login";
        }
        
        try {
            Map<String, Object> chatData = chatService.getChatWithMessages(chatId, adminId);
            
            model.addAttribute("chat", chatData.get("chat"));
            model.addAttribute("messages", chatData.get("messages"));
            model.addAttribute("messageCount", chatData.get("messageCount"));
            model.addAttribute("unreadCount", chatData.get("unreadCount"));
            
            return "admin/chat/chat-detail";
            
        } catch (Exception e) {
            model.addAttribute("error", "Erreur lors du chargement de la conversation: " + e.getMessage());
            return "redirect:/admin/chat";
        }
    }
    
    /**
     * API REST: Récupérer les conversations (AJAX)
     */
    @GetMapping("/api/conversations")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> getConversations(
            HttpServletRequest request,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String admin_username,
            @RequestParam(required = false) String admin_role) {
        
        try {
            // Si les paramètres admin ne sont pas fournis, utiliser des valeurs par défaut valides
            if (admin_username == null) {
                admin_username = (String) request.getSession().getAttribute("currentAdmin");
                if (admin_username == null) {
                    admin_username = request.getParameter("adminUsername");
                    if (admin_username == null) {
                        admin_username = "trad"; // Valeur par défaut pour les tests
                    }
                }
            }
            
            if (admin_role == null) {
                admin_role = (String) request.getSession().getAttribute("userRole");
                if (admin_role == null) {
                    admin_role = "ADMIN"; // Valeur par défaut
                }
            }
            
            // Construire l'URL vers le backend Python
            String url = PYTHON_BACKEND_URL + "/api/admin/chat/conversations";
            url += "?page=" + page + "&size=" + size;
            url += "&admin_username=" + admin_username + "&admin_role=" + admin_role;
            
            if (status != null && !status.isEmpty()) {
                url += "&status=" + status;
            }
            
            System.out.println("AdminChatController: Calling Python conversations API: " + url);
            
            try {
                // Faire l'appel au backend Python
                @SuppressWarnings("unchecked")
                Map<String, Object> response = restTemplate.getForObject(url, Map.class);
                
                if (response == null) {
                    Map<String, Object> errorResponse = new HashMap<>();
                    errorResponse.put("success", false);
                    errorResponse.put("error", "Réponse vide du backend Python");
                    return ResponseEntity.status(500).body(errorResponse);
                }
                
                return ResponseEntity.ok(response);
                
            } catch (Exception httpError) {
                System.err.println("AdminChatController HTTP Error: " + httpError.getMessage());
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("success", false);
                errorResponse.put("error", "Erreur communication backend: " + httpError.getMessage());
                errorResponse.put("conversations", new java.util.ArrayList<>());
                errorResponse.put("total", 0);
                errorResponse.put("page", page);
                errorResponse.put("size", size);
                return ResponseEntity.status(200).body(errorResponse); // Retourner 200 avec erreur pour éviter JS errors
            }
            
        } catch (Exception e) {
            System.err.println("AdminChatController Conversations Exception: " + e.getMessage());
            e.printStackTrace();
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Erreur interne: " + e.getMessage());
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
            @PathVariable String chatId, HttpServletRequest request) {
        
        String adminId = authService.getAuthenticatedAdminId(request);
        if (adminId == null) {
            return ResponseEntity.status(401).body(Map.of("error", "Non authentifié"));
        }
        
        try {
            Map<String, Object> chatData = chatService.getChatWithMessages(chatId, adminId);
            chatData.put("success", true);
            return ResponseEntity.ok(chatData);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
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
            HttpServletRequest httpRequest) {
        
        String adminId = authService.getAuthenticatedAdminId(httpRequest);
        if (adminId == null) {
            return ResponseEntity.status(401).body(Map.of("error", "Non authentifié"));
        }
        
        try {
            String message = request.get("message");
            if (message == null || message.trim().isEmpty()) {
                return ResponseEntity.status(400).body(Map.of("error", "Message requis"));
            }
            
            ChatMessage chatMessage = chatService.replyToChat(chatId, adminId, message.trim());
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", chatMessage);
            response.put("info", "Réponse envoyée avec succès");
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
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
            HttpServletRequest httpRequest) {
        
        String adminId = authService.getAuthenticatedAdminId(httpRequest);
        if (adminId == null) {
            return ResponseEntity.status(401).body(Map.of("error", "Non authentifié"));
        }
        
        try {
            String newStatus = request.get("status");
            if (newStatus == null || newStatus.trim().isEmpty()) {
                return ResponseEntity.status(400).body(Map.of("error", "Statut requis"));
            }
            
            Chat updatedChat = chatService.updateChatStatus(chatId, adminId, newStatus);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("chat", updatedChat);
            response.put("info", "Statut mis à jour avec succès");
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    /**
     * API REST: Assigner une conversation à un admin
     */
    @PutMapping("/api/{chatId}/assign")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> assignChat(
            @PathVariable String chatId,
            @RequestBody Map<String, String> request,
            HttpServletRequest httpRequest) {
        
        String adminId = authService.getAuthenticatedAdminId(httpRequest);
        if (adminId == null) {
            return ResponseEntity.status(401).body(Map.of("error", "Non authentifié"));
        }
        
        try {
            String targetAdminId = request.get("adminId");
            if (targetAdminId == null || targetAdminId.trim().isEmpty()) {
                return ResponseEntity.status(400).body(Map.of("error", "ID admin requis"));
            }
            
            Chat updatedChat = chatService.assignChatToAdmin(chatId, adminId, targetAdminId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("chat", updatedChat);
            response.put("info", "Conversation assignée avec succès");
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    /**
     * API REST: Rechercher des conversations
     */
    @GetMapping("/api/search")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> searchChats(
            @RequestParam String keyword,
            HttpServletRequest request) {
        
        String adminId = authService.getAuthenticatedAdminId(request);
        if (adminId == null) {
            return ResponseEntity.status(401).body(Map.of("error", "Non authentifié"));
        }
        
        try {
            List<Chat> chats = chatService.searchChats(adminId, keyword);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("chats", chats);
            response.put("count", chats.size());
            response.put("keyword", keyword);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    /**
     * API REST: Statistiques des conversations
     */
    @GetMapping("/api/statistics")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> getChatStatistics(
            @RequestParam(required = false) String admin_username,
            @RequestParam(required = false) String admin_role,
            HttpServletRequest request) {
        
        try {
            // Si les paramètres admin ne sont pas fournis, utiliser des valeurs par défaut valides
            if (admin_username == null) {
                admin_username = (String) request.getSession().getAttribute("currentAdmin");
                if (admin_username == null) {
                    admin_username = request.getParameter("adminUsername");
                    if (admin_username == null) {
                        admin_username = "trad"; // Valeur par défaut pour les tests
                    }
                }
            }
            
            if (admin_role == null) {
                admin_role = (String) request.getSession().getAttribute("userRole");
                if (admin_role == null) {
                    admin_role = "ADMIN"; // Valeur par défaut
                }
            }
            
            // Construire l'URL vers le backend Python
            String url = PYTHON_BACKEND_URL + "/api/admin/chat/statistics";
            url += "?admin_username=" + admin_username + "&admin_role=" + admin_role;
            
            System.out.println("AdminChatController: Calling Python stats API: " + url);
            
            try {
                // Faire l'appel au backend Python
                @SuppressWarnings("unchecked")
                Map<String, Object> response = restTemplate.getForObject(url, Map.class);
                
                if (response == null) {
                    Map<String, Object> errorResponse = new HashMap<>();
                    errorResponse.put("success", false);
                    errorResponse.put("error", "Réponse vide du backend Python");
                    errorResponse.put("statistics", new HashMap<>());
                    return ResponseEntity.status(200).body(errorResponse);
                }
                
                return ResponseEntity.ok(response);
                
            } catch (Exception httpError) {
                System.err.println("AdminChatController HTTP Error: " + httpError.getMessage());
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("success", false);
                errorResponse.put("error", "Erreur communication backend: " + httpError.getMessage());
                errorResponse.put("statistics", Map.of(
                    "totalConversations", 0,
                    "pendingConversations", 0,
                    "resolvedConversations", 0,
                    "todayMessages", 0
                ));
                return ResponseEntity.status(200).body(errorResponse); // Retourner 200 avec erreur pour éviter JS errors
            }
            
        } catch (Exception e) {
            System.err.println("AdminChatController Stats Exception: " + e.getMessage());
            e.printStackTrace();
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Erreur interne: " + e.getMessage());
            errorResponse.put("statistics", Map.of(
                "totalConversations", 0,
                "pendingConversations", 0,
                "resolvedConversations", 0,
                "todayMessages", 0
            ));
            return ResponseEntity.status(200).body(errorResponse); // Retourner 200 avec erreur pour éviter JS errors
        }
    }
}
