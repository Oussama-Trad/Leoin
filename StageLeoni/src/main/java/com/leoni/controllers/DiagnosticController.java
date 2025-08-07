package com.leoni.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/diagnostic")
public class DiagnosticController {

    @Autowired
    private MongoTemplate mongoTemplate;

    @GetMapping("/mongodb-connectivity")
    public ResponseEntity<Map<String, Object>> testMongoDBConnectivity() {
        Map<String, Object> result = new HashMap<>();
        
        try {
            // Test 1: Network connectivity to MongoDB server
            result.put("network_test", testNetworkConnectivity("192.168.1.16", 27017));
            
            // Test 2: MongoDB template connection
            result.put("mongodb_template_test", testMongoTemplate());
            
            // Test 3: Database operations
            result.put("database_operations_test", testDatabaseOperations());
            
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            result.put("error", e.getMessage());
            result.put("error_type", e.getClass().getSimpleName());
            return ResponseEntity.status(500).body(result);
        }
    }
    
    private Map<String, Object> testNetworkConnectivity(String host, int port) {
        Map<String, Object> networkResult = new HashMap<>();
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(host, port), 5000);
            networkResult.put("status", "SUCCESS");
            networkResult.put("message", "Network connection to " + host + ":" + port + " successful");
        } catch (Exception e) {
            networkResult.put("status", "FAILED");
            networkResult.put("message", "Network connection failed: " + e.getMessage());
            networkResult.put("error_type", e.getClass().getSimpleName());
        }
        return networkResult;
    }
    
    private Map<String, Object> testMongoTemplate() {
        Map<String, Object> templateResult = new HashMap<>();
        try {
            // Try to get database name
            String dbName = mongoTemplate.getDb().getName();
            templateResult.put("status", "SUCCESS");
            templateResult.put("database_name", dbName);
            templateResult.put("message", "MongoTemplate connection successful");
        } catch (Exception e) {
            templateResult.put("status", "FAILED");
            templateResult.put("message", "MongoTemplate connection failed: " + e.getMessage());
            templateResult.put("error_type", e.getClass().getSimpleName());
        }
        return templateResult;
    }
    
    private Map<String, Object> testDatabaseOperations() {
        Map<String, Object> dbResult = new HashMap<>();
        try {
            // Try to list collections
            var collections = mongoTemplate.getCollectionNames();
            dbResult.put("status", "SUCCESS");
            dbResult.put("collections", collections);
            dbResult.put("collection_count", collections.size());
            dbResult.put("message", "Database operations successful");
        } catch (Exception e) {
            dbResult.put("status", "FAILED");
            dbResult.put("message", "Database operations failed: " + e.getMessage());
            dbResult.put("error_type", e.getClass().getSimpleName());
        }
        return dbResult;
    }
}