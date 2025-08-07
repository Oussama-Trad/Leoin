package com.leoni.controllers;

import com.leoni.models.DocumentRequest;
import com.leoni.models.User;
import com.leoni.repositories.DocumentRequestRepository;
import com.leoni.repositories.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin/sync")
@CrossOrigin(origins = "*")
public class SyncController {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private DocumentRequestRepository documentRequestRepository;
    
    /**
     * General sync endpoint
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> syncData() {
        return syncUserDocuments();
    }
    
    /**
     * Synchronize user documentRequestIds with actual document requests
     */
    @PostMapping("/user-documents")
    public ResponseEntity<Map<String, Object>> syncUserDocuments() {
        try {
            List<User> users = userRepository.findAll();
            List<DocumentRequest> documentRequests = documentRequestRepository.findAll();
            
            // Clear all existing documentRequestIds
            for (User user : users) {
                if (user.getDocumentRequestIds() == null) {
                    user.setDocumentRequestIds(new ArrayList<>());
                } else {
                    user.getDocumentRequestIds().clear();
                }
            }
            
            // Rebuild documentRequestIds based on actual document requests
            for (DocumentRequest doc : documentRequests) {
                String userId = doc.getUserId();
                User user = users.stream()
                    .filter(u -> u.getId().equals(userId))
                    .findFirst()
                    .orElse(null);
                
                if (user != null) {
                    user.addDocumentRequest(doc.getId());
                }
            }
            
            // Save all users
            userRepository.saveAll(users);
            
            // Create response with sync statistics
            Map<String, Object> response = new HashMap<>();
            response.put("message", "User documents synchronized successfully");
            response.put("totalUsers", users.size());
            response.put("totalDocuments", documentRequests.size());
            
            Map<String, Integer> userDocumentCounts = new HashMap<>();
            for (User user : users) {
                userDocumentCounts.put(user.getAdresse1() != null ? user.getAdresse1() : user.getId(), user.getDocumentRequestIds().size());
            }
            response.put("userDocumentCounts", userDocumentCounts);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to sync user documents: " + e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        }
    }
}
