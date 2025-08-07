package com.leoni.controllers;

import com.leoni.models.Admin;
import com.leoni.models.News;
import com.leoni.services.AdminService;
import com.leoni.services.NewsService;
import com.leoni.services.AuthService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/news")
@CrossOrigin(origins = "*")
public class NewsController {
    
    private static final Logger logger = LoggerFactory.getLogger(NewsController.class);
    
    @Autowired
    private NewsService newsService;
    
    @Autowired
    private AuthService authService;
    
    @Autowired
    private AdminService adminService;
    
    /**
     * Helper method to extract token from Authorization header
     */
    private String extractToken(String authHeader) {
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            return authHeader.replace("Bearer ", "");
        }
        return authHeader;
    }
    
    /**
     * Create a new news article
     */
    @PostMapping("/create")
    public ResponseEntity<Map<String, Object>> createNews(
            @RequestBody Map<String, Object> request,
            @RequestHeader(value = "Authorization", required = false) String authToken) {
        
        try {
            // Extract and validate token
            String token = extractToken(authToken);
            if (token == null || !authService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token d'authentification requis")
                );
            }
            
            String role = authService.getRoleFromToken(token);
            String userId = authService.getUserIdFromToken(token);
            
            if (role == null || userId == null) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token invalide")
                );
            }
            
            // Create news object
            News news = new News();
            String title = (String) request.get("title");
            logger.info("Title received from frontend: '{}'", title);
            
            news.setTitle(title);
            news.setContent((String) request.get("content"));
            news.setSummary((String) request.get("summary"));
            news.setCategory((String) request.get("category"));
            news.setPriority((String) request.get("priority"));
            
            // Handle image URL if provided
            if (request.containsKey("imageUrl")) {
                news.setImageUrl((String) request.get("imageUrl"));
            }
            if (request.containsKey("imageName")) {
                news.setImageName((String) request.get("imageName"));
            }
            
            // Handle targeting based on role
            if ("SUPERADMIN".equals(role)) {
                // SuperAdmins can set custom targeting
                news.setTargetLocation((String) request.get("targetLocation"));
                news.setTargetDepartment((String) request.get("targetDepartment"));
            } else if ("ADMIN".equals(role)) {
                // For regular admins, automatically set targeting based on their profile
                try {
                    Admin admin = adminService.getAdminById(userId);
                    if (admin != null) {
                        if (admin.getLocation() != null && !admin.getLocation().trim().isEmpty()) {
                            news.setTargetLocation(admin.getLocation());
                        }
                        if (admin.getDepartment() != null && !admin.getDepartment().trim().isEmpty()) {
                            news.setTargetDepartment(admin.getDepartment());
                        }
                    }
                } catch (Exception e) {
                    logger.error("Error getting admin profile for auto-targeting: " + e.getMessage());
                }
            }
            
            // Set visibility status
            String visibilityStatus = "draft"; // default value
            Object visibilityObj = request.get("visibility");
            if (visibilityObj instanceof Map) {
                Map<String, Object> visibilityMap = (Map<String, Object>) visibilityObj;
                visibilityStatus = (String) visibilityMap.getOrDefault("status", "draft");
            } else if (request.containsKey("status")) {
                // Fallback for direct status field
                visibilityStatus = (String) request.getOrDefault("status", "draft");
            }
            
            // Use legacy format (isActive) instead of visibility.status
            news.setIsActive("published".equals(visibilityStatus) || "draft".equals(visibilityStatus));
            
            // Create the news
            News createdNews = newsService.createNews(news, userId, role);
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "Actualité créée avec succès",
                "news", createdNews
            ));
            
        } catch (Exception e) {
            logger.error("Error creating news", e);
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", "Erreur lors de la création de l'actualité: " + e.getMessage())
            );
        }
    }
    
    /**
     * Alternative POST endpoint on /api/news (for compatibility with frontend)
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createNewsAlternative(
            @RequestBody Map<String, Object> request,
            @RequestHeader(value = "Authorization", required = false) String authToken) {
        // Redirect to the main create method
        return createNews(request, authToken);
    }
    
    /**
     * Get news based on user role and filters (ONLY location and department)
     */
    @GetMapping
    public ResponseEntity<List<News>> getNews(
            @RequestParam(value = "location", required = false) String location,
            @RequestParam(value = "department", required = false) String department,
            @RequestHeader(value = "Authorization", required = false) String authToken) {
        
        try {
            // Extract token from Authorization header
            String token = authToken;
            if (authToken != null && authToken.startsWith("Bearer ")) {
                token = authToken.replace("Bearer ", "");
            }
            
            // Validate token
            if (token == null || !authService.validateToken(token)) {
                logger.warn("Invalid or missing token: {}", token);
                return ResponseEntity.status(401).build();
            }
            
            String role = authService.getRoleFromToken(token);
            String userId = authService.getUserIdFromToken(token);
            
            List<News> news;
            
            if ("SUPERADMIN".equals(role)) {
                // SuperAdmin sees all news with optional filtering
                if (location != null || department != null) {
                    news = newsService.getFilteredNews(location, department);
                } else {
                    // For SuperAdmin, show ALL news regardless of status
                    news = newsService.getAllNews();
                }
            } else {
                // Admin sees only their targeted news
                news = newsService.getNewsForAdmin(userId);
            }
            
            return ResponseEntity.ok(news);
            
        } catch (Exception e) {
            logger.error("Error fetching news", e);
            return ResponseEntity.status(500).build();
        }
    }
    
    /**
     * DEBUG: Get ALL news regardless of status - for troubleshooting
     */
    @GetMapping("/debug/all")
    public ResponseEntity<List<News>> getAllNewsDebug() {
        try {
            List<News> news = newsService.getAllNews();
            logger.info("Found {} news items in database", news.size());
            return ResponseEntity.ok(news);
        } catch (Exception e) {
            logger.error("Error fetching all news for debug", e);
            return ResponseEntity.status(500).build();
        }
    }
    
    /**
     * Get news for employees (public endpoint with location/department filtering ONLY)
     */
    @GetMapping("/public")
    public ResponseEntity<List<News>> getPublicNews(
            @RequestParam("location") String location,
            @RequestParam("department") String department) {
        
        try {
            List<News> news = newsService.getFilteredNews(location, department);
            return ResponseEntity.ok(news);
            
        } catch (Exception e) {
            logger.error("Error fetching public news", e);
            return ResponseEntity.status(500).build();
        }
    }
    
    /**
     * Get news by ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<News> getNewsById(@PathVariable String id) {
        try {
            Optional<News> news = newsService.getNewsById(id);
            if (news.isPresent()) {
                return ResponseEntity.ok(news.get());
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (Exception e) {
            logger.error("Error fetching news by ID", e);
            return ResponseEntity.status(500).build();
        }
    }
    
    /**
     * Update news
     */
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateNews(
            @PathVariable String id,
            @RequestBody News updatedNews,
            @RequestHeader(value = "Authorization", required = false) String authToken) {
        
        try {
            // Extract and validate token
            String token = extractToken(authToken);
            if (token == null || !authService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token d'authentification requis")
                );
            }
            
            News news = newsService.updateNews(id, updatedNews);
            if (news != null) {
                return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", "Actualité mise à jour avec succès",
                    "news", news
                ));
            } else {
                return ResponseEntity.notFound().build();
            }
            
        } catch (Exception e) {
            logger.error("Error updating news", e);
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", "Erreur lors de la mise à jour: " + e.getMessage())
            );
        }
    }
    
    /**
     * Publish news
     */
    @PostMapping("/{id}/publish")
    public ResponseEntity<Map<String, Object>> publishNews(
            @PathVariable String id,
            @RequestHeader(value = "Authorization", required = false) String authToken) {
        
        try {
            // Extract and validate token
            String token = extractToken(authToken);
            if (token == null || !authService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token d'authentification requis")
                );
            }
            
            News news = newsService.publishNews(id);
            if (news != null) {
                return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", "Actualité publiée avec succès",
                    "news", news
                ));
            } else {
                return ResponseEntity.notFound().build();
            }
            
        } catch (Exception e) {
            logger.error("Error publishing news", e);
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", "Erreur lors de la publication: " + e.getMessage())
            );
        }
    }
    
    /**
     * Archive news
     */
    @PostMapping("/{id}/archive")
    public ResponseEntity<Map<String, Object>> archiveNews(
            @PathVariable String id,
            @RequestHeader(value = "Authorization", required = false) String authToken) {
        
        try {
            // Extract and validate token
            String token = extractToken(authToken);
            if (token == null || !authService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token d'authentification requis")
                );
            }
            
            News news = newsService.archiveNews(id);
            if (news != null) {
                return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", "Actualité archivée avec succès",
                    "news", news
                ));
            } else {
                return ResponseEntity.notFound().build();
            }
            
        } catch (Exception e) {
            logger.error("Error archiving news", e);
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", "Erreur lors de l'archivage: " + e.getMessage())
            );
        }
    }
    
    /**
     * Delete news
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteNews(
            @PathVariable String id,
            @RequestHeader(value = "Authorization", required = false) String authToken) {
        
        try {
            // Extract and validate token
            String token = extractToken(authToken);
            if (token == null || !authService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token d'authentification requis")
                );
            }
            
            boolean deleted = newsService.deleteNews(id);
            if (deleted) {
                return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", "Actualité supprimée avec succès"
                ));
            } else {
                return ResponseEntity.notFound().build();
            }
            
        } catch (Exception e) {
            logger.error("Error deleting news", e);
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", "Erreur lors de la suppression: " + e.getMessage())
            );
        }
    }
    
    /**
     * Upload image for news
     */
    @PostMapping("/upload-image")
    public ResponseEntity<Map<String, Object>> uploadImage(
            @RequestParam("file") org.springframework.web.multipart.MultipartFile file,
            @RequestHeader(value = "Authorization", required = false) String authToken) {
        
        try {
            // Extract and validate token
            String token = extractToken(authToken);
            if (token == null || !authService.validateToken(token)) {
                return ResponseEntity.status(401).body(
                    Map.of("success", false, "message", "Token d'authentification requis")
                );
            }
            
            if (file.isEmpty()) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Aucun fichier sélectionné")
                );
            }
            
            // Check file type
            String contentType = file.getContentType();
            if (contentType == null || !contentType.startsWith("image/")) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "Le fichier doit être une image")
                );
            }
            
            // Check file size (max 5MB)
            if (file.getSize() > 5 * 1024 * 1024) {
                return ResponseEntity.badRequest().body(
                    Map.of("success", false, "message", "La taille du fichier ne doit pas dépasser 5MB")
                );
            }
            
            // Create uploads directory if it doesn't exist
            String uploadDir = System.getProperty("user.dir") + "/uploads/news-images/";
            java.io.File dir = new java.io.File(uploadDir);
            if (!dir.exists()) {
                boolean created = dir.mkdirs();
                logger.info("Created upload directory: " + uploadDir + " - " + created);
            }
            
            // Generate unique filename
            String originalFilename = file.getOriginalFilename();
            String extension = "";
            if (originalFilename != null && originalFilename.contains(".")) {
                extension = originalFilename.substring(originalFilename.lastIndexOf("."));
            }
            String filename = System.currentTimeMillis() + "_" + java.util.UUID.randomUUID().toString() + extension;
            String filePath = uploadDir + filename;
            
            // Save file
            file.transferTo(new java.io.File(filePath));
            
            // Return file URL
            String fileUrl = "/uploads/news-images/" + filename;
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "Image uploadée avec succès",
                "imageUrl", fileUrl,
                "imageName", originalFilename
            ));
            
        } catch (Exception e) {
            logger.error("Error uploading image", e);
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", "Erreur lors de l'upload: " + e.getMessage())
            );
        }
    }
}
