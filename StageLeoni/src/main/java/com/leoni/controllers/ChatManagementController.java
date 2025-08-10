package com.leoni.controllers;

import com.leoni.models.Chat;
import com.leoni.models.ChatMessage;
import com.leoni.repositories.ChatRepository;
import com.leoni.repositories.ChatMessageRepository;
import com.leoni.services.UnifiedAuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.util.*;

@RestController
@RequestMapping("/dashboard/api/chats")
public class ChatManagementController {
    
    private static final Logger logger = LoggerFactory.getLogger(ChatManagementController.class);
    
    @Autowired
    private ChatRepository chatRepository;
    
    @Autowired
    private ChatMessageRepository chatMessageRepository;
    
    @Autowired
    private UnifiedAuthService authService;
    
    @Autowired
    private MongoTemplate mongoTemplate;
    
    /**
     * Get chats with basic pagination
     */
    @GetMapping
    public ResponseEntity<Map<String, Object>> getChats(
            @RequestHeader("Authorization") String authHeader,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String search) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            // Build query criteria
            Criteria criteria = new Criteria();
            List<Criteria> conditions = new ArrayList<>();
            
            // Apply search filter
            if (search != null && !search.trim().isEmpty()) {
                conditions.add(new Criteria().orOperator(
                    Criteria.where("subject").regex(search, "i"),
                    Criteria.where("userName").regex(search, "i")
                ));
            }
            
            if (!conditions.isEmpty()) {
                criteria = criteria.andOperator(conditions.toArray(new Criteria[0]));
            }
            
            // Create pageable
            Sort sort = Sort.by(Sort.Direction.DESC, "lastActivityAt");
            Pageable pageable = PageRequest.of(page, size, sort);
            
            // Execute query
            Query query = Query.query(criteria).with(pageable);
            List<Chat> chats = mongoTemplate.find(query, Chat.class);
            long totalElements = mongoTemplate.count(Query.query(criteria), Chat.class);
            
            // Build response
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("chats", chats);
            response.put("totalElements", totalElements);
            response.put("totalPages", (int) Math.ceil((double) totalElements / size));
            response.put("currentPage", page);
            response.put("size", size);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Error fetching chats", e);
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la récupération des chats"));
        }
    }
    
    /**
     * Get chat by ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getChatById(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable String id) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            Optional<Chat> chatOpt = chatRepository.findById(id);
            
            if (!chatOpt.isPresent()) {
                return ResponseEntity.status(404)
                    .body(Map.of("success", false, "message", "Chat non trouvé"));
            }
            
            Chat chat = chatOpt.get();
            
            // Get recent messages
            Query messageQuery = Query.query(Criteria.where("chatRef").is(id))
                .with(Sort.by(Sort.Direction.DESC, "createdAt"))
                .limit(20);
            List<ChatMessage> messages = mongoTemplate.find(messageQuery, ChatMessage.class);
            
            // Reverse to show chronological order
            Collections.reverse(messages);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("chat", chat);
            response.put("messages", messages);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Error fetching chat by ID", e);
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la récupération du chat"));
        }
    }
    
    /**
     * Update chat status
     */
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateChat(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable String id,
            @RequestBody Map<String, Object> updateData) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            Optional<Chat> existingChat = chatRepository.findById(id);
            if (!existingChat.isPresent()) {
                return ResponseEntity.status(404)
                    .body(Map.of("success", false, "message", "Chat non trouvé"));
            }
            
            Chat chat = existingChat.get();
            
            // Update allowed fields
            if (updateData.containsKey("status")) {
                String status = (String) updateData.get("status");
                if (Arrays.asList("open", "in_progress", "closed").contains(status)) {
                    chat.setStatus(status);
                }
            }
            
            if (updateData.containsKey("subject")) {
                String subject = (String) updateData.get("subject");
                if (subject != null && !subject.trim().isEmpty()) {
                    chat.setSubject(subject);
                }
            }
            
            chat.setUpdatedAt(LocalDateTime.now());
            
            Chat savedChat = chatRepository.save(chat);
            
            return ResponseEntity.ok(Map.of("success", true, "chat", savedChat));
            
        } catch (Exception e) {
            logger.error("Error updating chat", e);
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la mise à jour du chat"));
        }
    }
    
    /**
     * Get chat statistics
     */
    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getStatistics(
            @RequestHeader("Authorization") String authHeader) {
        
        try {
            String token = authHeader.replace("Bearer ", "");
            
            if (!authService.validateToken(token)) {
                return ResponseEntity.status(401)
                    .body(Map.of("success", false, "message", "Token invalide"));
            }
            
            Map<String, Object> stats = new HashMap<>();
            
            // Total chats
            long totalChats = chatRepository.count();
            stats.put("totalChats", totalChats);
            
            // By status
            Arrays.asList("open", "in_progress", "closed").forEach(status -> {
                long count = mongoTemplate.count(Query.query(Criteria.where("status").is(status)), Chat.class);
                stats.put("status_" + status, count);
            });
            
            // Total messages
            long totalMessages = chatMessageRepository.count();
            stats.put("totalMessages", totalMessages);
            
            return ResponseEntity.ok(Map.of("success", true, "statistics", stats));
            
        } catch (Exception e) {
            logger.error("Error fetching chat statistics", e);
            return ResponseEntity.status(500)
                .body(Map.of("success", false, "message", "Erreur lors de la récupération des statistiques"));
        }
    }
}
