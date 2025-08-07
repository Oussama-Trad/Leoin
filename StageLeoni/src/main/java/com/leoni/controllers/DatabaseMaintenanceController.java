package com.leoni.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/admin/database")
@CrossOrigin(origins = "*")
public class DatabaseMaintenanceController {

    @Autowired
    private MongoTemplate mongoTemplate;

    /**
     * Drop the unique index on parentalEmail field
     */
    @PostMapping("/drop-parental-email-index")
    public ResponseEntity<Map<String, Object>> dropParentalEmailIndex() {
        try {
            // Drop the unique index on parentalEmail
            mongoTemplate.getCollection("users").dropIndex("parentalEmail_1");
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Successfully dropped unique index on parentalEmail field");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "Error dropping index: " + e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }

    /**
     * List all indexes on users collection
     */
    @GetMapping("/list-user-indexes")
    public ResponseEntity<Map<String, Object>> listUserIndexes() {
        try {
            var indexes = mongoTemplate.getCollection("users").listIndexes();
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("indexes", indexes.into(new java.util.ArrayList<>()));
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "Error listing indexes: " + e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }
}
