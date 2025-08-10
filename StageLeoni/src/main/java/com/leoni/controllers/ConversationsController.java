package com.leoni.controllers;

import com.leoni.models.Admin;
import com.leoni.services.AdminService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@Controller
@RequestMapping("/conversations")
public class ConversationsController {

    @Autowired
    private AdminService adminService;
    
    @Autowired
    private MongoTemplate mongoTemplate;

    @GetMapping
    public String conversations(Model model, @RequestParam(required = false) String adminUsername) {
        System.out.println("ConversationsController: Called with adminUsername=" + adminUsername);
        
        try {
            // 1. Determine admin role and filtering
            boolean isSuperAdmin = false;
            String adminDepartment = null;
            String adminLocation = null;
            String displayName = adminUsername != null ? adminUsername : "Test Admin";
            
            // Check if admin exists in database and get role/location/department
            if (adminUsername != null) {
                try {
                    Optional<Admin> adminOpt = adminService.findByUsername(adminUsername);
                    if (adminOpt.isPresent()) {
                        Admin admin = adminOpt.get();
                        isSuperAdmin = "SUPERADMIN".equals(admin.getRole());
                        adminDepartment = admin.getDepartment();
                        adminLocation = admin.getLocation();
                        displayName = admin.getUsername() + " (" + admin.getRole() + ")";
                        System.out.println("Found admin: " + displayName + ", Department: " + adminDepartment + ", Location: " + adminLocation + ", IsSuperAdmin: " + isSuperAdmin);
                    } else {
                        System.out.println("Admin '" + adminUsername + "' not found in database, using demo mode");
                        adminDepartment = "Production";
                        adminLocation = "Mateur";
                        displayName = adminUsername + " (Demo Admin)";
                    }
                } catch (Exception e) {
                    System.err.println("Error fetching admin info: " + e.getMessage());
                    adminDepartment = "Production";
                    adminLocation = "Mateur";
                    displayName = adminUsername + " (Fallback)";
                }
            }
            
            // 2. Initialize data containers
            List<Map> filteredChats = new ArrayList<>();
            Map<String, Integer> statusStats = new HashMap<>();
            
            int activeChats = 0;
            int pendingChats = 0;
            int closedChats = 0;
            
            // 3. Fetch and filter conversations based on role
            try {
                List<Map> allChats = mongoTemplate.findAll(Map.class, "chats");
                System.out.println("Fetched " + allChats.size() + " total chats from database");
                
                for (Map chat : allChats) {
                    if (chat == null) continue;
                    
                    // Get chat department and location
                    String chatDept = getStringValue(chat, "targetDepartment");
                    if (chatDept == null || chatDept.isEmpty()) {
                        chatDept = getStringValue(chat, "department");
                    }
                    if (chatDept == null || chatDept.isEmpty()) {
                        chatDept = extractDepartmentFromService(getStringValue(chat, "service"));
                    }
                    
                    String chatLocation = getStringValue(chat, "targetLocation");
                    if (chatLocation == null || chatLocation.isEmpty()) {
                        chatLocation = getStringValue(chat, "location");
                    }
                    
                    // Apply role-based filtering
                    boolean includeChat = false;
                    if (isSuperAdmin) {
                        // SuperAdmin sees everything
                        includeChat = true;
                    } else {
                        // Regular admin sees only their department and location
                        boolean deptMatch = (adminDepartment == null || adminDepartment.equals(chatDept));
                        boolean locMatch = (adminLocation == null || adminLocation.equals(chatLocation));
                        includeChat = deptMatch && locMatch;
                    }
                    
                    if (includeChat) {
                        // Add message count to each conversation
                        Object chatId = chat.get("_id");
                        if (chatId != null) {
                            Query messageQuery = new Query(Criteria.where("chatRef").is(chatId));
                            long messageCount = mongoTemplate.count(messageQuery, "chat_messages");
                            chat.put("messageCount", messageCount);
                            
                            // Get last message
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
                        
                        filteredChats.add(chat);
                        
                        String status = getStringValue(chat, "status");
                        if (status == null || status.isEmpty()) {
                            status = "pending";
                        }
                        statusStats.put(status, statusStats.getOrDefault(status, 0) + 1);
                        
                        // Count by status
                        if ("open".equals(status) || "in_progress".equals(status)) {
                            activeChats++;
                        } else if ("pending".equals(status)) {
                            pendingChats++;
                        } else if ("closed".equals(status)) {
                            closedChats++;
                        }
                    }
                }
                
                System.out.println("Filtered to " + filteredChats.size() + " chats for role-based access");
                
            } catch (Exception mongoException) {
                System.err.println("MongoDB error: " + mongoException.getMessage());
                mongoException.printStackTrace();
            }
            
            // 4. Set model attributes
            model.addAttribute("adminUsername", adminUsername);
            model.addAttribute("adminDisplayName", displayName);
            model.addAttribute("isSuperAdmin", isSuperAdmin);
            model.addAttribute("adminDepartment", adminDepartment);
            model.addAttribute("adminLocation", adminLocation);
            
            model.addAttribute("conversations", filteredChats);
            model.addAttribute("totalConversations", filteredChats.size());
            model.addAttribute("activeChats", activeChats);
            model.addAttribute("pendingChats", pendingChats);
            model.addAttribute("closedChats", closedChats);
            model.addAttribute("statusStats", statusStats);
            
            model.addAttribute("title", "Gestion des Conversations");
            model.addAttribute("currentPage", "conversations");
            
            System.out.println("Conversations page loaded successfully for: " + displayName);
            return "conversations";
            
        } catch (Exception e) {
            System.err.println("Conversations error: " + e.getMessage());
            e.printStackTrace();
            
            // Error fallback
            model.addAttribute("error", "Erreur lors du chargement des conversations: " + e.getMessage());
            model.addAttribute("adminUsername", adminUsername);
            model.addAttribute("adminDisplayName", adminUsername != null ? adminUsername : "Utilisateur");
            model.addAttribute("isSuperAdmin", false);
            model.addAttribute("conversations", List.of());
            model.addAttribute("totalConversations", 0);
            model.addAttribute("activeChats", 0);
            model.addAttribute("pendingChats", 0);
            model.addAttribute("closedChats", 0);
            model.addAttribute("statusStats", Map.of());
            model.addAttribute("title", "Conversations - Erreur");
            model.addAttribute("currentPage", "conversations");
            
            return "conversations";
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
        
        // Extract department from service (format: "Department - Location")
        if (service.contains(" - ")) {
            return service.split(" - ")[0].trim();
        }
        
        return service;
    }
}
