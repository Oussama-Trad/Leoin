package com.leoni.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/health")
@CrossOrigin(origins = "*")
public class HealthController {

    @Autowired
    private MongoTemplate mongoTemplate;

    /**
     * Simple health check that doesn't require database
     */
    @GetMapping("/simple")
    public ResponseEntity<Map<String, Object>> simpleHealthCheck() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("message", "Application is running");
        response.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(response);
    }

    /**
     * Database connectivity check
     */
    @GetMapping("/database")
    public ResponseEntity<Map<String, Object>> databaseHealthCheck() {
        Map<String, Object> response = new HashMap<>();
        
        try {
            // Try to ping MongoDB
            mongoTemplate.getCollection("test").countDocuments();
            response.put("status", "UP");
            response.put("database", "Connected");
            response.put("message", "MongoDB connection successful");
        } catch (Exception e) {
            response.put("status", "DOWN");
            response.put("database", "Disconnected");
            response.put("message", "MongoDB connection failed: " + e.getMessage());
            response.put("error", e.getClass().getSimpleName());
        }
        
        response.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(response);
    }
}