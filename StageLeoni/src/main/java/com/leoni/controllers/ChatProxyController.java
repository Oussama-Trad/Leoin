package com.leoni.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;

import jakarta.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.Map;

/**
 * Contrôleur proxy pour rediriger les appels chat vers le backend Python
 */
@RestController
@RequestMapping("/admin/chat/api")
public class ChatProxyController {
    
    @Autowired
    private RestTemplate restTemplate;
    
    private final String PYTHON_BACKEND_URL = "http://localhost:5000";
    
    /**
     * Proxy pour récupérer les conversations
     */
    @GetMapping("/conversations")
    public ResponseEntity<Map<String, Object>> getConversations(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String admin_username,
            @RequestParam(required = false) String admin_role,
            HttpServletRequest request) {
        
        try {
            // Construire l'URL vers le backend Python
            String url = PYTHON_BACKEND_URL + "/api/admin/chat/conversations";
            url += "?page=" + page + "&size=" + size;
            
            if (status != null && !status.isEmpty()) {
                url += "&status=" + status;
            }
            
            // Si les paramètres admin ne sont pas fournis, essayer de les récupérer de la session
            if (admin_username == null) {
                admin_username = (String) request.getSession().getAttribute("currentAdmin");
                if (admin_username == null) {
                    admin_username = request.getParameter("adminUsername");
                }
            }
            
            if (admin_role == null) {
                admin_role = (String) request.getSession().getAttribute("userRole");
                if (admin_role == null) {
                    admin_role = "ADMIN"; // Valeur par défaut
                }
            }
            
            if (admin_username != null) {
                url += "&admin_username=" + admin_username;
            }
            if (admin_role != null) {
                url += "&admin_role=" + admin_role;
            }
            
            System.out.println("ChatProxy: Calling Python API: " + url);
            
            // Faire l'appel au backend Python
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            
            return ResponseEntity.ok(response);
            
        } catch (HttpClientErrorException | HttpServerErrorException e) {
            System.err.println("ChatProxy Error: " + e.getStatusCode() + " - " + e.getResponseBodyAsString());
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Erreur backend: " + e.getMessage());
            return ResponseEntity.status(e.getStatusCode()).body(errorResponse);
            
        } catch (Exception e) {
            System.err.println("ChatProxy Exception: " + e.getMessage());
            e.printStackTrace();
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Erreur interne: " + e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        }
    }
    
    /**
     * Proxy pour récupérer les statistiques chat
     */
    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getChatStatistics(
            @RequestParam(required = false) String admin_username,
            @RequestParam(required = false) String admin_role,
            HttpServletRequest request) {
        
        try {
            // Construire l'URL vers le backend Python
            String url = PYTHON_BACKEND_URL + "/api/admin/chat/statistics";
            
            // Si les paramètres admin ne sont pas fournis, essayer de les récupérer de la session
            if (admin_username == null) {
                admin_username = (String) request.getSession().getAttribute("currentAdmin");
                if (admin_username == null) {
                    admin_username = request.getParameter("adminUsername");
                }
            }
            
            if (admin_role == null) {
                admin_role = (String) request.getSession().getAttribute("userRole");
                if (admin_role == null) {
                    admin_role = "ADMIN"; // Valeur par défaut
                }
            }
            
            boolean hasParams = false;
            if (admin_username != null) {
                url += (hasParams ? "&" : "?") + "admin_username=" + admin_username;
                hasParams = true;
            }
            if (admin_role != null) {
                url += (hasParams ? "&" : "?") + "admin_role=" + admin_role;
                hasParams = true;
            }
            
            System.out.println("ChatProxy: Calling Python stats API: " + url);
            
            // Faire l'appel au backend Python
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            
            return ResponseEntity.ok(response);
            
        } catch (HttpClientErrorException | HttpServerErrorException e) {
            System.err.println("ChatProxy Stats Error: " + e.getStatusCode() + " - " + e.getResponseBodyAsString());
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Erreur backend: " + e.getMessage());
            return ResponseEntity.status(e.getStatusCode()).body(errorResponse);
            
        } catch (Exception e) {
            System.err.println("ChatProxy Stats Exception: " + e.getMessage());
            e.printStackTrace();
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Erreur interne: " + e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        }
    }
    
    /**
     * Proxy pour récupérer une conversation avec ses messages
     */
    @GetMapping("/{chatId}")
    public ResponseEntity<Map<String, Object>> getChatWithMessages(
            @PathVariable String chatId,
            @RequestParam(required = false) String admin_username,
            @RequestParam(required = false) String admin_role,
            HttpServletRequest request) {
        
        try {
            // Construire l'URL vers le backend Python
            String url = PYTHON_BACKEND_URL + "/api/admin/chat/" + chatId;
            
            // Si les paramètres admin ne sont pas fournis, essayer de les récupérer de la session
            if (admin_username == null) {
                admin_username = (String) request.getSession().getAttribute("currentAdmin");
                if (admin_username == null) {
                    admin_username = request.getParameter("adminUsername");
                }
            }
            
            if (admin_role == null) {
                admin_role = (String) request.getSession().getAttribute("userRole");
                if (admin_role == null) {
                    admin_role = "ADMIN"; // Valeur par défaut
                }
            }
            
            boolean hasParams = false;
            if (admin_username != null) {
                url += (hasParams ? "&" : "?") + "admin_username=" + admin_username;
                hasParams = true;
            }
            if (admin_role != null) {
                url += (hasParams ? "&" : "?") + "admin_role=" + admin_role;
                hasParams = true;
            }
            
            System.out.println("ChatProxy: Calling Python chat detail API: " + url);
            
            // Faire l'appel au backend Python
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            
            return ResponseEntity.ok(response);
            
        } catch (HttpClientErrorException | HttpServerErrorException e) {
            System.err.println("ChatProxy Chat Detail Error: " + e.getStatusCode() + " - " + e.getResponseBodyAsString());
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Erreur backend: " + e.getMessage());
            return ResponseEntity.status(e.getStatusCode()).body(errorResponse);
            
        } catch (Exception e) {
            System.err.println("ChatProxy Chat Detail Exception: " + e.getMessage());
            e.printStackTrace();
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Erreur interne: " + e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        }
    }
    
    /**
     * Proxy pour répondre à une conversation
     */
    @PostMapping("/{chatId}/reply")
    public ResponseEntity<Map<String, Object>> replyToChat(
            @PathVariable String chatId,
            @RequestBody Map<String, String> requestBody,
            @RequestParam(required = false) String admin_username,
            @RequestParam(required = false) String admin_role,
            HttpServletRequest request) {
        
        try {
            // Construire l'URL vers le backend Python
            String url = PYTHON_BACKEND_URL + "/api/admin/chat/" + chatId + "/reply";
            
            // Si les paramètres admin ne sont pas fournis, essayer de les récupérer de la session
            if (admin_username == null) {
                admin_username = (String) request.getSession().getAttribute("currentAdmin");
                if (admin_username == null) {
                    admin_username = request.getParameter("adminUsername");
                }
            }
            
            if (admin_role == null) {
                admin_role = (String) request.getSession().getAttribute("userRole");
                if (admin_role == null) {
                    admin_role = "ADMIN"; // Valeur par défaut
                }
            }
            
            // Ajouter les infos admin au body de la requête
            Map<String, String> body = new HashMap<>(requestBody);
            if (admin_username != null) {
                body.put("admin_username", admin_username);
            }
            if (admin_role != null) {
                body.put("admin_role", admin_role);
            }
            
            System.out.println("ChatProxy: Posting to Python reply API: " + url);
            System.out.println("ChatProxy: Request body: " + body);
            
            // Faire l'appel au backend Python
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, body, Map.class);
            
            return ResponseEntity.ok(response);
            
        } catch (HttpClientErrorException | HttpServerErrorException e) {
            System.err.println("ChatProxy Reply Error: " + e.getStatusCode() + " - " + e.getResponseBodyAsString());
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Erreur backend: " + e.getMessage());
            return ResponseEntity.status(e.getStatusCode()).body(errorResponse);
            
        } catch (Exception e) {
            System.err.println("ChatProxy Reply Exception: " + e.getMessage());
            e.printStackTrace();
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Erreur interne: " + e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        }
    }
}
