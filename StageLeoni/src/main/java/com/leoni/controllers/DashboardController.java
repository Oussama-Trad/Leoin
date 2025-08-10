package com.leoni.controllers;

import com.leoni.models.Admin;
import com.leoni.models.SuperAdmin;
import com.leoni.models.User;
import com.leoni.services.AdminService;
import com.leoni.services.SuperAdminService;
import com.leoni.repositories.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@Controller
@RequestMapping("/dashboard")
public class DashboardController {

    @Autowired
    private AdminService adminService;
    
    @Autowired
    private SuperAdminService superAdminService;
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private MongoTemplate mongoTemplate;

    @GetMapping
    public String dashboard(Model model, @RequestParam(required = false) String adminUsername) {
        System.out.println("DashboardController: Called with adminUsername=" + adminUsername);
        
        try {
            // 1. Determine admin role and filtering
            boolean isSuperAdmin = false;
            String adminDepartment = null;
            String adminLocation = null;
            String displayName = adminUsername != null ? adminUsername : "Test Admin";
            
            // Check if admin exists in database and get role/location/department
            if (adminUsername != null) {
                try {
                    // First check in regular admins
                    Optional<Admin> adminOpt = adminService.findByUsername(adminUsername);
                    if (adminOpt.isPresent()) {
                        Admin admin = adminOpt.get();
                        isSuperAdmin = "SUPERADMIN".equals(admin.getRole());
                        adminDepartment = admin.getDepartment();
                        adminLocation = admin.getLocation();
                        displayName = admin.getUsername() + " (" + admin.getRole() + ")";
                        System.out.println("Found admin: " + displayName + ", Department: " + adminDepartment + ", Location: " + adminLocation + ", IsSuperAdmin: " + isSuperAdmin);
                    } else {
                        // Check in superadmins collection
                        Optional<SuperAdmin> superAdminOpt = superAdminService.findByUsername(adminUsername);
                        if (superAdminOpt.isPresent()) {
                            SuperAdmin superAdmin = superAdminOpt.get();
                            isSuperAdmin = true;
                            displayName = superAdmin.getUsername() + " (SUPERADMIN)";
                            System.out.println("Found superadmin: " + displayName);
                        } else {
                            System.out.println("Admin/SuperAdmin '" + adminUsername + "' not found in database, using demo mode");
                            // Demo mode - assume regular admin
                            adminDepartment = "Production";
                            adminLocation = "Mateur";
                            displayName = adminUsername + " (Demo Admin)";
                        }
                    }
                } catch (Exception e) {
                    System.err.println("Error fetching admin info: " + e.getMessage());
                    // Fallback to demo mode
                    adminDepartment = "Production";
                    adminLocation = "Mateur";
                    displayName = adminUsername + " (Fallback)";
                }
            }
            
            // 2. Initialize data containers
            List<Map> filteredChats = new ArrayList<>();
            Map<String, Integer> departmentStats = new HashMap<>();
            Map<String, Integer> locationStats = new HashMap<>();
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
                        filteredChats.add(chat);
                        
                        // Update statistics
                        if (chatDept != null && !chatDept.isEmpty()) {
                            departmentStats.put(chatDept, departmentStats.getOrDefault(chatDept, 0) + 1);
                        }
                        
                        if (chatLocation != null && !chatLocation.isEmpty()) {
                            locationStats.put(chatLocation, locationStats.getOrDefault(chatLocation, 0) + 1);
                        }
                        
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
            
            // 3.2. Fetch and filter employees based on role
            int totalEmployees = 0;
            int activeEmployees = 0;
            int pendingEmployees = 0;
            Map<String, Integer> employeeDepartmentStats = new HashMap<>();
            Map<String, Integer> employeeLocationStats = new HashMap<>();
            
            try {
                List<User> allEmployees = userRepository.findAll();
                
                final String finalAdminDepartment = adminDepartment;
                final String finalAdminLocation = adminLocation;
                
                List<User> filteredEmployees;
                if (isSuperAdmin) {
                    // SuperAdmin sees all employees
                    filteredEmployees = allEmployees;
                    System.out.println("SuperAdmin - showing all " + allEmployees.size() + " employees");
                } else {
                    // Regular admin sees only their department and location
                    filteredEmployees = allEmployees.stream()
                        .filter(emp -> {
                            boolean deptMatch = (finalAdminDepartment == null || finalAdminDepartment.equals(emp.getDepartment()));
                            boolean locMatch = (finalAdminLocation == null || finalAdminLocation.equals(emp.getLocation()));
                            return deptMatch && locMatch;
                        })
                        .collect(java.util.stream.Collectors.toList());
                    System.out.println("Regular admin - filtered to " + filteredEmployees.size() + " employees from " + allEmployees.size() + " total");
                }
                
                totalEmployees = filteredEmployees.size();
                activeEmployees = (int) filteredEmployees.stream()
                    .filter(emp -> "approved".equals(emp.getStatus()))
                    .count();
                pendingEmployees = (int) filteredEmployees.stream()
                    .filter(emp -> "pending".equals(emp.getStatus()))
                    .count();
                
                // Calculate department and location stats for employees
                for (User employee : filteredEmployees) {
                    String empDept = employee.getDepartment();
                    if (empDept != null && !empDept.isEmpty()) {
                        employeeDepartmentStats.put(empDept, employeeDepartmentStats.getOrDefault(empDept, 0) + 1);
                    }
                    
                    String empLoc = employee.getLocation();
                    if (empLoc != null && !empLoc.isEmpty()) {
                        employeeLocationStats.put(empLoc, employeeLocationStats.getOrDefault(empLoc, 0) + 1);
                    }
                }
                
            } catch (Exception employeeException) {
                System.err.println("Employee stats error: " + employeeException.getMessage());
                employeeException.printStackTrace();
            }
            
            // 4. Set model attributes with proper error handling
            model.addAttribute("adminUsername", adminUsername);
            model.addAttribute("adminDisplayName", displayName);
            model.addAttribute("isSuperAdmin", isSuperAdmin);
            model.addAttribute("adminDepartment", adminDepartment);
            model.addAttribute("adminLocation", adminLocation);
            
            model.addAttribute("totalConversations", filteredChats.size());
            model.addAttribute("activeChats", activeChats);
            model.addAttribute("pendingChats", pendingChats);
            model.addAttribute("closedChats", closedChats);
            
            model.addAttribute("conversations", filteredChats);
            model.addAttribute("departmentStats", departmentStats);
            model.addAttribute("locationStats", locationStats);
            model.addAttribute("statusStats", statusStats);
            
            // Employee statistics
            model.addAttribute("totalEmployees", totalEmployees);
            model.addAttribute("activeEmployees", activeEmployees);
            model.addAttribute("pendingEmployees", pendingEmployees);
            model.addAttribute("employeeDepartmentStats", employeeDepartmentStats);
            model.addAttribute("employeeLocationStats", employeeLocationStats);
            
            model.addAttribute("title", "Leoni Admin Dashboard");
            model.addAttribute("message", "Welcome to the Admin Dashboard");
            
            System.out.println("Dashboard loaded successfully for: " + displayName);
            return "dashboard";
            
        } catch (Exception e) {
            System.err.println("Dashboard error: " + e.getMessage());
            e.printStackTrace();
            
            // Error fallback
            model.addAttribute("error", "Erreur: " + e.getMessage());
            model.addAttribute("adminUsername", adminUsername);
            model.addAttribute("adminDisplayName", adminUsername != null ? adminUsername : "Utilisateur");
            model.addAttribute("isSuperAdmin", false);
            model.addAttribute("totalConversations", 0);
            model.addAttribute("activeChats", 0);
            model.addAttribute("pendingChats", 0);
            model.addAttribute("closedChats", 0);
            model.addAttribute("conversations", new ArrayList<>());
            model.addAttribute("departmentStats", new HashMap<>());
            model.addAttribute("locationStats", new HashMap<>());
            model.addAttribute("statusStats", new HashMap<>());
            model.addAttribute("title", "Leoni Admin Dashboard - Erreur");
            model.addAttribute("message", "Erreur lors du chargement");
            
            return "dashboard";
        }
    }
    
    /**
     * Handle favicon.ico requests to prevent 500 errors
     */
    @GetMapping("/favicon.ico")
    @ResponseBody
    public ResponseEntity<Void> favicon() {
        return ResponseEntity.notFound().build();
    }
    
    /**
     * Get admin information by admin ID (used as session token)
     * @param adminId the admin ID from session
     * @return Admin information
     */
    @GetMapping("/api/admin-info/{adminId}")
    @ResponseBody
    public ResponseEntity<?> getAdminInfo(@PathVariable String adminId) {
        try {
            Optional<Admin> admin = adminService.findById(adminId);
            if (admin.isPresent()) {
                Admin adminInfo = admin.get();
                return ResponseEntity.ok(Map.of(
                    "success", true,
                    "admin", Map.of(
                        "id", adminInfo.getId(),
                        "username", adminInfo.getUsername(),
                        "departmentId", adminInfo.getDepartmentId(),
                        "role", adminInfo.getRole()
                    )
                ));
            } else {
                return ResponseEntity.status(404).body(
                    Map.of("success", false, "message", "Admin not found")
                );
            }
        } catch (Exception e) {
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", "Error retrieving admin info: " + e.getMessage())
            );
        }
    }
    
    /**
     * API pour récupérer les conversations pour le dashboard
     */
    @GetMapping("/api/conversations")
    @ResponseBody
    public ResponseEntity<?> getConversationsApi() {
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
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", e.getMessage());
            response.put("conversations", new ArrayList<>());
            response.put("total", 0);
            return ResponseEntity.ok(response);
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
    
    /**
     * Test route for troubleshooting ERR_INCOMPLETE_CHUNKED_ENCODING
     */
    @GetMapping("/test")
    public String dashboardTest(Model model, @RequestParam(required = false) String adminUsername) {
        System.out.println("DashboardController TEST: Called with adminUsername=" + adminUsername);
        
        try {
            // Simple test data
            model.addAttribute("title", "Dashboard Test");
            model.addAttribute("message", "Test réussi - page de diagnostic");
            model.addAttribute("totalConversations", 5);
            model.addAttribute("activeChats", 2);
            model.addAttribute("pendingChats", 1);
            model.addAttribute("closedChats", 2);
            
            Map<String, Integer> testDeptStats = new HashMap<>();
            testDeptStats.put("Production", 3);
            testDeptStats.put("Quality", 2);
            model.addAttribute("departmentStats", testDeptStats);
            
            List<Map<String, Object>> testConversations = new ArrayList<>();
            Map<String, Object> conv1 = new HashMap<>();
            conv1.put("subject", "Test conversation 1");
            conv1.put("status", "pending");
            conv1.put("targetDepartment", "Production");
            conv1.put("targetLocation", "Mateur");
            testConversations.add(conv1);
            
            Map<String, Object> conv2 = new HashMap<>();
            conv2.put("subject", "Test conversation 2");
            conv2.put("status", "closed");
            conv2.put("department", "Quality");
            conv2.put("location", "Sousse");
            testConversations.add(conv2);
            
            model.addAttribute("conversations", testConversations);
            
            System.out.println("DashboardController TEST: Model attributes set successfully");
            return "dashboard-test";
            
        } catch (Exception e) {
            System.err.println("DashboardController TEST: Error: " + e.getMessage());
            e.printStackTrace();
            
            model.addAttribute("error", "Erreur dans le test: " + e.getMessage());
            model.addAttribute("title", "Dashboard Test - Erreur");
            model.addAttribute("message", "Erreur lors du test");
            model.addAttribute("totalConversations", 0);
            model.addAttribute("activeChats", 0);
            model.addAttribute("pendingChats", 0);
            model.addAttribute("closedChats", 0);
            model.addAttribute("departmentStats", new HashMap<>());
            model.addAttribute("conversations", new ArrayList<>());
            
            return "dashboard-test";
        }
    }
}
