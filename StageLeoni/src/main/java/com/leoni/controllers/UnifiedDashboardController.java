package com.leoni.controllers;

import com.leoni.services.UnifiedAuthService;
import com.leoni.services.AdminService;
import com.leoni.services.NewsService;
import com.leoni.repositories.UserRepository;
import com.leoni.models.Admin;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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
public class UnifiedDashboardController {
    
    private static final Logger logger = LoggerFactory.getLogger(UnifiedDashboardController.class);
    
    @Autowired
    private UnifiedAuthService unifiedAuthService;
    
    @Autowired
    private AdminService adminService;
    
    @Autowired
    private NewsService newsService;
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private MongoTemplate mongoTemplate;
    
    /**
     * Main dashboard endpoint - unified for both Admin and SuperAdmin
     */
    @GetMapping
    public String dashboard(
            @RequestParam(required = false) String token,
            @RequestParam(required = false) String adminUsername,
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            Model model) {
        
        logger.info("Dashboard access attempt - token: {}, adminUsername: {}, authHeader: {}", 
            token != null ? "present" : "null", 
            adminUsername, 
            authHeader != null ? "present" : "null");
        
        try {
            // Extract token from various sources
            String authToken = extractToken(token, authHeader);
            
            if (authToken == null) {
                // Redirect to login if no token
                return "redirect:/login.html";
            }
            
            // Validate token
            if (!unifiedAuthService.validateToken(authToken)) {
                logger.warn("Invalid token provided");
                model.addAttribute("error", "Session expirée. Veuillez vous reconnecter.");
                return "redirect:/login.html";
            }
            
            // Extract user info from token
            String username = unifiedAuthService.getUsernameFromToken(authToken);
            String role = unifiedAuthService.getRoleFromToken(authToken);
            String userId = unifiedAuthService.getUserIdFromToken(authToken);
            String department = unifiedAuthService.getDepartmentFromToken(authToken);
            String location = unifiedAuthService.getLocationFromToken(authToken);
            
            boolean isSuperAdmin = "SUPERADMIN".equals(role);
            
            logger.info("Dashboard access for user: {} ({}), department: {}, location: {}", 
                username, role, department, location);
            
            // Set basic user info
            model.addAttribute("username", username);
            model.addAttribute("role", role);
            model.addAttribute("isSuperAdmin", isSuperAdmin);
            model.addAttribute("department", department);
            model.addAttribute("location", location);
            model.addAttribute("token", authToken);
            
            // Load dashboard statistics
            loadDashboardStats(model, isSuperAdmin, department, location);
            
            // Load recent activity
            loadRecentActivity(model, isSuperAdmin, department, location);
            
            return "unified-dashboard";
            
        } catch (Exception e) {
            logger.error("Error loading dashboard", e);
            model.addAttribute("error", "Erreur lors du chargement du tableau de bord");
            return "unified-dashboard";
        }
    }
    
    /**
     * API endpoint for dashboard stats
     */
    @GetMapping("/api/stats")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> getDashboardStats(
            @RequestHeader("Authorization") String authHeader) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!unifiedAuthService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            String role = unifiedAuthService.getRoleFromToken(token);
            String department = unifiedAuthService.getDepartmentFromToken(token);
            String location = unifiedAuthService.getLocationFromToken(token);
            boolean isSuperAdmin = "SUPERADMIN".equals(role);
            
            Map<String, Object> stats = new HashMap<>();
            
            // Load different stats based on role
            if (isSuperAdmin) {
                stats = loadSuperAdminStats();
            } else {
                stats = loadAdminStats(department, location);
            }
            
            stats.put("success", true);
            return ResponseEntity.ok(stats);
            
        } catch (Exception e) {
            logger.error("Error getting dashboard stats", e);
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", "Erreur lors du chargement des statistiques")
            );
        }
    }
    
    /**
     * Extract token from various sources
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
    
    /**
     * Load dashboard statistics
     */
    private void loadDashboardStats(Model model, boolean isSuperAdmin, String department, String location) {
        try {
            if (isSuperAdmin) {
                // SuperAdmin sees all statistics
                model.addAttribute("totalAdmins", adminService.getAllActiveAdmins().size());
                model.addAttribute("totalEmployees", userRepository.count());
                model.addAttribute("totalNews", newsService.getAllNews().size());
                model.addAttribute("totalDepartments", getDepartmentCount());
                model.addAttribute("totalLocations", getLocationCount());
            } else {
                // Admin sees filtered statistics
                model.addAttribute("totalAdmins", getFilteredAdminCount(department, location));
                model.addAttribute("totalEmployees", getFilteredEmployeeCount(department, location));
                model.addAttribute("totalNews", getFilteredNewsCount(department, location));
                model.addAttribute("department", department);
                model.addAttribute("location", location);
            }
            
            // Common stats
            model.addAttribute("activeChats", getActiveChatCount());
            model.addAttribute("pendingRequests", getPendingRequestCount());
            
        } catch (Exception e) {
            logger.error("Error loading dashboard stats", e);
            // Set default values
            model.addAttribute("totalAdmins", 0);
            model.addAttribute("totalEmployees", 0);
            model.addAttribute("totalNews", 0);
            model.addAttribute("activeChats", 0);
            model.addAttribute("pendingRequests", 0);
        }
    }
    
    /**
     * Load recent activity
     */
    private void loadRecentActivity(Model model, boolean isSuperAdmin, String department, String location) {
        try {
            List<Map<String, Object>> recentActivity = new ArrayList<>();
            
            // Recent news
            try {
                if (isSuperAdmin) {
                    newsService.getAllNews().stream()
                        .limit(5)
                        .forEach(news -> {
                            Map<String, Object> activity = new HashMap<>();
                            activity.put("type", "news");
                            activity.put("title", news.getTitle());
                            activity.put("date", news.getCreatedAt());
                            recentActivity.add(activity);
                        });
                }
            } catch (Exception e) {
                logger.debug("Error loading recent news", e);
            }
            
            // Recent user registrations
            try {
                userRepository.findAll().stream()
                    .sorted((a, b) -> {
                        if (a.getCreatedAt() == null && b.getCreatedAt() == null) return 0;
                        if (a.getCreatedAt() == null) return 1;
                        if (b.getCreatedAt() == null) return -1;
                        return b.getCreatedAt().compareTo(a.getCreatedAt());
                    })
                    .limit(3)
                    .forEach(user -> {
                        Map<String, Object> activity = new HashMap<>();
                        activity.put("type", "user");
                        activity.put("title", "Nouvel employé: " + user.getFirstName() + " " + user.getLastName());
                        activity.put("date", user.getCreatedAt());
                        recentActivity.add(activity);
                    });
            } catch (Exception e) {
                logger.debug("Error loading recent users", e);
            }
            
            model.addAttribute("recentActivity", recentActivity);
            
        } catch (Exception e) {
            logger.error("Error loading recent activity", e);
            model.addAttribute("recentActivity", new ArrayList<>());
        }
    }
    
    /**
     * Load SuperAdmin statistics
     */
    private Map<String, Object> loadSuperAdminStats() {
        Map<String, Object> stats = new HashMap<>();
        
        try {
            stats.put("totalAdmins", adminService.getAllActiveAdmins().size());
            stats.put("totalEmployees", userRepository.count());
            stats.put("totalNews", newsService.getAllNews().size());
            stats.put("totalDepartments", getDepartmentCount());
            stats.put("totalLocations", getLocationCount());
        } catch (Exception e) {
            logger.error("Error loading SuperAdmin stats", e);
        }
        
        return stats;
    }
    
    /**
     * Load Admin statistics (filtered by department/location)
     */
    private Map<String, Object> loadAdminStats(String department, String location) {
        Map<String, Object> stats = new HashMap<>();
        
        try {
            stats.put("totalEmployees", getFilteredEmployeeCount(department, location));
            stats.put("totalNews", getFilteredNewsCount(department, location));
            stats.put("department", department);
            stats.put("location", location);
        } catch (Exception e) {
            logger.error("Error loading Admin stats", e);
        }
        
        return stats;
    }
    
    // Helper methods for statistics
    
    private int getFilteredAdminCount(String department, String location) {
        try {
            Query query = new Query();
            if (department != null) {
                query.addCriteria(Criteria.where("department").is(department));
            }
            if (location != null) {
                query.addCriteria(Criteria.where("location").is(location));
            }
            query.addCriteria(Criteria.where("active").is(true));
            return (int) mongoTemplate.count(query, "admins");
        } catch (Exception e) {
            logger.debug("Error getting filtered admin count", e);
            return 0;
        }
    }
    
    private long getFilteredEmployeeCount(String department, String location) {
        try {
            if (department == null && location == null) {
                return userRepository.count();
            }
            
            Query query = new Query();
            if (department != null) {
                query.addCriteria(Criteria.where("department").is(department));
            }
            if (location != null) {
                query.addCriteria(Criteria.where("location").is(location));
            }
            return mongoTemplate.count(query, "users");
        } catch (Exception e) {
            logger.debug("Error getting filtered employee count", e);
            return 0;
        }
    }
    
    private int getFilteredNewsCount(String department, String location) {
        try {
            Query query = new Query();
            if (department != null) {
                query.addCriteria(Criteria.where("targetDepartment").is(department));
            }
            if (location != null) {
                query.addCriteria(Criteria.where("targetLocation").is(location));
            }
            return (int) mongoTemplate.count(query, "news");
        } catch (Exception e) {
            logger.debug("Error getting filtered news count", e);
            return 0;
        }
    }
    
    private int getDepartmentCount() {
        try {
            return (int) mongoTemplate.count(new Query(), "departments");
        } catch (Exception e) {
            return 0;
        }
    }
    
    private int getLocationCount() {
        try {
            // Count unique locations from admins or departments
            return adminService.getAllActiveAdmins().stream()
                .map(Admin::getLocation)
                .filter(Objects::nonNull)
                .map(String::valueOf)
                .collect(java.util.stream.Collectors.toSet())
                .size();
        } catch (Exception e) {
            return 0;
        }
    }
    
    private int getActiveChatCount() {
        try {
            Query query = new Query(Criteria.where("status").in("open", "in_progress"));
            return (int) mongoTemplate.count(query, "chats");
        } catch (Exception e) {
            return 0;
        }
    }
    
    private int getPendingRequestCount() {
        try {
            Query query = new Query(Criteria.where("status.current").is("pending"));
            return (int) mongoTemplate.count(query, "document_requests");
        } catch (Exception e) {
            return 0;
        }
    }
}
