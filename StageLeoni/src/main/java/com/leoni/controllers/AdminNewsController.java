package com.leoni.controllers;

import com.leoni.services.AuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;

import java.util.Map;

@RestController
@RequestMapping("/api/admin")
@CrossOrigin(origins = "*")
public class AdminNewsController {
    
    @Autowired
    private AuthService authService;
    
    @Autowired
    private RestTemplate restTemplate;
    
    // Base URL for Python backend
    private static final String PYTHON_BACKEND_URL = "http://localhost:5000";
    
    /**
     * Create a new news article with department and location targeting
     * @param authHeader Authorization header with bearer token
     * @param newsData News article data including title, content, targeting info
     * @return Creation result
     */
    @PostMapping("/news/create")
    public ResponseEntity<?> createFilteredNews(
            @RequestHeader("Authorization") String authHeader,
            @RequestBody Map<String, Object> newsData) {
        
        System.out.println("=== CREATE FILTERED NEWS ===");
        System.out.println("Auth Header: " + authHeader);
        System.out.println("News Data: " + newsData);
        
        try {
            // Validate token
            String token = authHeader.replace("Bearer ", "");
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of("success", false, "message", "Token invalide"));
            }
            
            // Get admin role and info from token
            String role = authService.getRoleFromToken(token);
            String userId = authService.getUserIdFromToken(token);
            
            // Add author information to news data
            newsData.put("authorRole", role);
            newsData.put("authorId", userId);
            
            String url = PYTHON_BACKEND_URL + "/api/admin/news/create";
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", authHeader);
            headers.set("Content-Type", "application/json");
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(newsData, headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                Map.class
            );
            
            System.out.println("News creation response: " + response.getStatusCode());
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            System.out.println("Error in createFilteredNews: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Erreur lors de la création de l'actualité: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Get news filtered by admin role and department/location
     * @param authHeader Authorization header
     * @param department Optional department filter
     * @param location Optional location filter
     * @return List of filtered news articles
     */
    @GetMapping("/news/filtered")
    public ResponseEntity<?> getFilteredNews(
            @RequestHeader("Authorization") String authHeader,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) String location) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of("success", false, "message", "Token invalide"));
            }
            
            String role = authService.getRoleFromToken(token);
            
            // Build URL with filters based on role
            StringBuilder urlBuilder = new StringBuilder(PYTHON_BACKEND_URL + "/api/admin/news");
            urlBuilder.append("?role=").append(role);
            
            if (department != null && !department.isEmpty()) {
                urlBuilder.append("&department=").append(department);
            }
            if (location != null && !location.isEmpty()) {
                urlBuilder.append("&location=").append(location);
            }
            
            String url = urlBuilder.toString();
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", authHeader);
            HttpEntity<String> entity = new HttpEntity<>(headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            return ResponseEntity.ok(response.getBody());
            
        } catch (Exception e) {
            System.out.println("Error in getFilteredNews: " + e.getMessage());
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "message", "Erreur lors de la récupération des actualités: " + e.getMessage()
            ));
        }
    }
}
