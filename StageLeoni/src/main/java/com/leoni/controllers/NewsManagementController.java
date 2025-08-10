package com.leoni.controllers;

import com.leoni.models.News;
import com.leoni.models.Admin;
import com.leoni.services.NewsService;
import com.leoni.services.UnifiedAuthService;
import com.leoni.services.AdminService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.Optional;

@RestController
@RequestMapping("/api/news-management")
@CrossOrigin(origins = "*")
public class NewsManagementController {
    
    @Autowired
    private NewsService newsService;
    
    @Autowired
    private UnifiedAuthService authService;
    
    @Autowired
    private AdminService adminService;
    
    /**
     * Create a new news article
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createNews(
            @RequestBody News news,
            HttpServletRequest request
    ) {
        try {
            String authHeader = request.getHeader("Authorization");
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                return ResponseEntity.status(401).body(Map.of(
                    "success", false,
                    "message", "Authorization header required"
                ));
            }
            
            String token = authHeader.replace("Bearer ", "");
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of(
                    "success", false,
                    "message", "Invalid token"
                ));
            }
            
            // Get admin info from token
            String role = authService.getRoleFromToken(token);
            String adminId = authService.getUserIdFromToken(token);
            String username = authService.getUsernameFromToken(token);
            
            System.out.println("Creating news - Role: " + role + ", AdminId: " + adminId + ", Username: " + username);
            
            // Set author information
            news.setAuthorRef(adminId);
            news.setAuthorName(username);
            
            if (!"SUPERADMIN".equals(role)) {
                // For regular admins, get their location and department from token
                String location = authService.getLocationFromToken(token);
                String department = authService.getDepartmentFromToken(token);
                if (location != null) {
                    news.setTargetLocation(location);
                }
                if (department != null) {
                    news.setTargetDepartment(department);
                }
                System.out.println("Admin news - Location: " + location + ", Department: " + department);
            }
            // For SuperAdmins, use the values provided in the request
            
            News savedNews = newsService.createNews(news);
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "News created successfully",
                "news", savedNews
            ));
            
        } catch (Exception e) {
            System.err.println("Error creating news: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Error creating news: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Update an existing news article
     */
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateNews(
            @PathVariable String id,
            @RequestBody News news,
            HttpServletRequest request
    ) {
        try {
            String authHeader = request.getHeader("Authorization");
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of(
                    "success", false,
                    "message", "Invalid token"
                ));
            }
            
            news.setId(id);
            News updatedNews = newsService.updateNews(news);
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "News updated successfully",
                "news", updatedNews
            ));
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Error updating news: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Delete a news article
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteNews(
            @PathVariable String id,
            HttpServletRequest request
    ) {
        try {
            String authHeader = request.getHeader("Authorization");
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of(
                    "success", false,
                    "message", "Invalid token"
                ));
            }
            
            newsService.deleteNews(id);
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "News deleted successfully"
            ));
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Error deleting news: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Get all news (SuperAdmin only) or filtered news (regular admin)
     */
    @GetMapping
    public ResponseEntity<Map<String, Object>> getAllNews(HttpServletRequest request) {
        try {
            String authHeader = request.getHeader("Authorization");
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of(
                    "success", false,
                    "message", "Invalid token"
                ));
            }
            
            String role = authService.getRoleFromToken(token);
            List<News> newsList;
            
            if ("SUPERADMIN".equals(role)) {
                newsList = newsService.getAllNews();
            } else {
                // Get admin's location and department from token for filtering
                String location = authService.getLocationFromToken(token);
                String department = authService.getDepartmentFromToken(token);
                if (location != null || department != null) {
                    newsList = newsService.getFilteredNews(location, department);
                } else {
                    newsList = newsService.getAllNews(); // Fallback
                }
            }
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "news", newsList,
                "total", newsList.size()
            ));
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Error retrieving news: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Get news by ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getNewsById(
            @PathVariable String id,
            HttpServletRequest request
    ) {
        try {
            String authHeader = request.getHeader("Authorization");
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of(
                    "success", false,
                    "message", "Invalid token"
                ));
            }
            
            Optional<News> news = newsService.getNewsById(id);
            if (news.isPresent()) {
                return ResponseEntity.ok(Map.of(
                    "success", true,
                    "news", news.get()
                ));
            } else {
                return ResponseEntity.status(404).body(Map.of(
                    "success", false,
                    "message", "News not found"
                ));
            }
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Error retrieving news: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Update news status (publish/archive/draft)
     */
    @PatchMapping("/{id}/status")
    public ResponseEntity<Map<String, Object>> updateNewsStatus(
            @PathVariable String id,
            @RequestBody Map<String, String> statusUpdate,
            HttpServletRequest request
    ) {
        try {
            String authHeader = request.getHeader("Authorization");
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of(
                    "success", false,
                    "message", "Invalid token"
                ));
            }
            
            String newStatus = statusUpdate.get("status");
            News updatedNews = newsService.updateNewsStatus(id, newStatus);
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "News status updated successfully",
                "news", updatedNews
            ));
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Error updating news status: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Get news statistics
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getNewsStats(HttpServletRequest request) {
        try {
            String authHeader = request.getHeader("Authorization");
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of(
                    "success", false,
                    "message", "Invalid token"
                ));
            }
            
            Map<String, Object> stats = newsService.getNewsStatistics();
            return ResponseEntity.ok(stats);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Error retrieving statistics: " + e.getMessage()
            ));
        }
    }
}
