package com.leoni.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.*;

@Controller
@RequestMapping("/admin/chats-mongo")
public class AdminChatMongoController {

    @Autowired
    private MongoTemplate mongoTemplate;

    @GetMapping
    public String chatManagementPage(Model model) {
        try {
            // Récupérer toutes les conversations depuis MongoDB
            List<Map> allChats = mongoTemplate.findAll(Map.class, "chats");
            
            model.addAttribute("totalChats", allChats.size());
            model.addAttribute("chats", allChats);
            
            // Statistiques par département
            Map<String, Integer> departmentStats = new HashMap<>();
            Map<String, Integer> locationStats = new HashMap<>();
            Map<String, Integer> statusStats = new HashMap<>();
            
            for (Map chat : allChats) {
                // Département (essayer les deux structures)
                String dept = getStringValue(chat, "targetDepartment");
                if (dept == null || dept.isEmpty()) {
                    dept = getStringValue(chat, "department");
                }
                if (dept == null || dept.isEmpty()) {
                    dept = extractDepartmentFromService(getStringValue(chat, "service"));
                }
                if (dept != null && !dept.isEmpty()) {
                    departmentStats.put(dept, departmentStats.getOrDefault(dept, 0) + 1);
                }
                
                // Location
                String location = getStringValue(chat, "targetLocation");
                if (location == null || location.isEmpty()) {
                    location = getStringValue(chat, "location");
                }
                if (location != null && !location.isEmpty()) {
                    locationStats.put(location, locationStats.getOrDefault(location, 0) + 1);
                }
                
                // Status
                String status = getStringValue(chat, "status");
                if (status == null || status.isEmpty()) {
                    status = "pending";
                }
                statusStats.put(status, statusStats.getOrDefault(status, 0) + 1);
            }
            
            model.addAttribute("departmentStats", departmentStats);
            model.addAttribute("locationStats", locationStats);
            model.addAttribute("statusStats", statusStats);
            
            return "admin/chat-management-mongo";
            
        } catch (Exception e) {
            e.printStackTrace();
            model.addAttribute("error", "Erreur lors du chargement des conversations: " + e.getMessage());
            model.addAttribute("totalChats", 0);
            model.addAttribute("chats", new ArrayList<>());
            return "admin/chat-management-mongo";
        }
    }

    @GetMapping("/api/conversations")
    @ResponseBody
    public Map<String, Object> getConversationsApi() {
        try {
            // Récupérer toutes les conversations
            List<Map> chats = mongoTemplate.findAll(Map.class, "chats");
            
            // Pour chaque conversation, récupérer le nombre de messages
            for (Map chat : chats) {
                Object chatId = chat.get("_id");
                if (chatId != null) {
                    Query messageQuery = new Query(Criteria.where("chatRef").is(chatId));
                    long messageCount = mongoTemplate.count(messageQuery, "chat_messages");
                    chat.put("messageCount", messageCount);
                    
                    // Récupérer le dernier message
                    Query lastMessageQuery = new Query(Criteria.where("chatRef").is(chatId))
                            .with(org.springframework.data.domain.Sort.by(
                                org.springframework.data.domain.Sort.Direction.DESC, "createdAt"))
                            .limit(1);
                    List<Map> lastMessages = mongoTemplate.find(lastMessageQuery, Map.class, "chat_messages");
                    if (!lastMessages.isEmpty()) {
                        Map lastMessage = lastMessages.get(0);
                        chat.put("lastMessage", getStringValue(lastMessage, "message"));
                        chat.put("lastMessageDate", lastMessage.get("createdAt"));
                    }
                }
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("conversations", chats);
            response.put("total", chats.size());
            
            return response;
            
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", e.getMessage());
            response.put("conversations", new ArrayList<>());
            response.put("total", 0);
            return response;
        }
    }

    @GetMapping("/api/messages")
    @ResponseBody
    public Map<String, Object> getMessagesApi() {
        try {
            // Récupérer tous les messages
            List<Map> messages = mongoTemplate.findAll(Map.class, "chat_messages");
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("messages", messages);
            response.put("total", messages.size());
            
            return response;
            
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", e.getMessage());
            response.put("messages", new ArrayList<>());
            response.put("total", 0);
            return response;
        }
    }

    @GetMapping("/api/stats")
    @ResponseBody
    public Map<String, Object> getStatsApi() {
        try {
            List<Map> chats = mongoTemplate.findAll(Map.class, "chats");
            List<Map> messages = mongoTemplate.findAll(Map.class, "chat_messages");
            
            Map<String, Integer> departmentStats = new HashMap<>();
            Map<String, Integer> locationStats = new HashMap<>();
            Map<String, Integer> statusStats = new HashMap<>();
            
            for (Map chat : chats) {
                // Département
                String dept = getStringValue(chat, "targetDepartment");
                if (dept == null || dept.isEmpty()) {
                    dept = getStringValue(chat, "department");
                }
                if (dept == null || dept.isEmpty()) {
                    dept = extractDepartmentFromService(getStringValue(chat, "service"));
                }
                if (dept != null && !dept.isEmpty()) {
                    departmentStats.put(dept, departmentStats.getOrDefault(dept, 0) + 1);
                }
                
                // Location
                String location = getStringValue(chat, "targetLocation");
                if (location == null || location.isEmpty()) {
                    location = getStringValue(chat, "location");
                }
                if (location != null && !location.isEmpty()) {
                    locationStats.put(location, locationStats.getOrDefault(location, 0) + 1);
                }
                
                // Status
                String status = getStringValue(chat, "status");
                if (status == null || status.isEmpty()) {
                    status = "pending";
                }
                statusStats.put(status, statusStats.getOrDefault(status, 0) + 1);
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("totalChats", chats.size());
            response.put("totalMessages", messages.size());
            response.put("departmentStats", departmentStats);
            response.put("locationStats", locationStats);
            response.put("statusStats", statusStats);
            
            return response;
            
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", e.getMessage());
            return response;
        }
    }

    private String getStringValue(Map map, String key) {
        Object value = map.get(key);
        return value != null ? value.toString() : null;
    }

    private String extractDepartmentFromService(String service) {
        if (service == null || service.isEmpty()) {
            return null;
        }
        
        // Extraire le département du service (format: "Department - Location")
        if (service.contains(" - ")) {
            return service.split(" - ")[0].trim();
        }
        
        return service;
    }
}
