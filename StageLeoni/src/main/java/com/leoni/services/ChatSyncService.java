package com.leoni.services;

import com.leoni.models.Chat;
import com.leoni.models.ChatMessage;
import com.leoni.repositories.ChatRepository;
import com.leoni.repositories.ChatMessageRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;

/**
 * Service unifié pour la synchronisation des chats avec l'application mobile
 */
@Service
public class ChatSyncService {
    
    @Autowired
    private ChatRepository chatRepository;
    
    @Autowired
    private ChatMessageRepository chatMessageRepository;
    
    @Autowired
    private MongoTemplate mongoTemplate;
    
    /**
     * Récupérer les conversations filtrées pour un admin avec synchronisation mobile
     */
    public Page<Chat> getFilteredChatsForAdmin(String adminDepartment, String adminLocation, 
                                              String adminRole, int page, int size, String status) {
        
        System.out.println("ChatSyncService: Filtrage conversations pour admin");
        System.out.println("Département: " + adminDepartment + ", Location: " + adminLocation + ", Rôle: " + adminRole);
        
        Criteria criteria = new Criteria();
        List<Criteria> conditions = new ArrayList<>();
        
        // Filtrage selon le rôle
        if (!"SUPERADMIN".equals(adminRole)) {
            // Admin normal : seulement son département et location
            if (adminDepartment != null && !adminDepartment.trim().isEmpty()) {
                conditions.add(Criteria.where("targetDepartment").is(adminDepartment));
            }
            if (adminLocation != null && !adminLocation.trim().isEmpty()) {
                conditions.add(Criteria.where("targetLocation").is(adminLocation));
            }
        }
        // SuperAdmin voit toutes les conversations (pas de filtre)
        
        // Filtre par statut si fourni
        if (status != null && !status.trim().isEmpty() && !"all".equals(status)) {
            conditions.add(Criteria.where("status").is(status));
        }
        
        // Appliquer les conditions
        if (!conditions.isEmpty()) {
            criteria = criteria.andOperator(conditions.toArray(new Criteria[0]));
        }
        
        // Créer la requête avec pagination
        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "lastActivityAt"));
        Query query = Query.query(criteria).with(pageable);
        
        // Exécuter la requête
        List<Chat> chats = mongoTemplate.find(query, Chat.class);
        long totalElements = mongoTemplate.count(Query.query(criteria), Chat.class);
        
        System.out.println("ChatSyncService: Trouvé " + chats.size() + " conversations sur " + totalElements + " total");
        
        // Enrichir avec les informations de messages
        for (Chat chat : chats) {
            enrichChatWithMessageInfo(chat);
        }
        
        return new org.springframework.data.domain.PageImpl<>(chats, pageable, totalElements);
    }
    
    /**
     * Enrichir un chat avec les informations de messages
     */
    private void enrichChatWithMessageInfo(Chat chat) {
        try {
            String chatId = chat.getId();
            
            // Compter les messages
            Query messageQuery = Query.query(Criteria.where("chatRef").is(chatId));
            long messageCount = mongoTemplate.count(messageQuery, ChatMessage.class);
            chat.setMessageCount((int) messageCount);
            
            // Récupérer le dernier message
            Query lastMessageQuery = Query.query(Criteria.where("chatRef").is(chatId))
                .with(Sort.by(Sort.Direction.DESC, "createdAt"))
                .limit(1);
            List<ChatMessage> lastMessages = mongoTemplate.find(lastMessageQuery, ChatMessage.class);
            
            if (!lastMessages.isEmpty()) {
                ChatMessage lastMessage = lastMessages.get(0);
                // Mettre à jour lastActivityAt si nécessaire
                if (chat.getLastActivityAt() == null || 
                    lastMessage.getCreatedAt().isAfter(chat.getLastActivityAt())) {
                    chat.setLastActivityAt(lastMessage.getCreatedAt());
                }
            }
            
            // Compter les messages non lus
            Query unreadQuery = Query.query(Criteria.where("chatRef").is(chatId)
                .and("isRead").is(false)
                .and("senderType").is("user"));
            long unreadCount = mongoTemplate.count(unreadQuery, ChatMessage.class);
            chat.setHasUnreadMessages(unreadCount > 0);
            
        } catch (Exception e) {
            System.err.println("Erreur enrichissement chat " + chat.getId() + ": " + e.getMessage());
        }
    }
    
    /**
     * Récupérer une conversation avec ses messages
     */
    public Map<String, Object> getChatWithMessages(String chatId, String adminDepartment, String adminLocation, String adminRole) {
        try {
            // Récupérer la conversation
            Optional<Chat> chatOpt = chatRepository.findById(chatId);
            if (!chatOpt.isPresent()) {
                throw new RuntimeException("Conversation non trouvée");
            }
            
            Chat chat = chatOpt.get();
            
            // Vérifier les permissions
            if (!canAdminAccessChat(chat, adminDepartment, adminLocation, adminRole)) {
                throw new RuntimeException("Accès non autorisé à cette conversation");
            }
            
            // Récupérer les messages
            Query messageQuery = Query.query(Criteria.where("chatRef").is(chatId))
                .with(Sort.by(Sort.Direction.ASC, "createdAt"));
            List<ChatMessage> messages = mongoTemplate.find(messageQuery, ChatMessage.class);
            
            // Enrichir le chat
            enrichChatWithMessageInfo(chat);
            
            Map<String, Object> result = new HashMap<>();
            result.put("chat", chat);
            result.put("messages", messages);
            result.put("messageCount", messages.size());
            result.put("canReply", chat.isActive());
            
            return result;
            
        } catch (Exception e) {
            throw new RuntimeException("Erreur lors de la récupération de la conversation: " + e.getMessage());
        }
    }
    
    /**
     * Répondre à une conversation (admin)
     */
    public ChatMessage replyToChat(String chatId, String adminId, String adminName, String message) {
        try {
            // Vérifier que la conversation existe
            Optional<Chat> chatOpt = chatRepository.findById(chatId);
            if (!chatOpt.isPresent()) {
                throw new RuntimeException("Conversation non trouvée");
            }
            
            Chat chat = chatOpt.get();
            
            // Créer le message de réponse
            ChatMessage chatMessage = new ChatMessage();
            chatMessage.setChatRef(chatId);
            chatMessage.setSenderId(adminId);
            chatMessage.setSenderName(adminName);
            chatMessage.setSenderType("admin");
            chatMessage.setMessage(message);
            chatMessage.setCreatedAt(LocalDateTime.now());
            chatMessage.setRead(false);
            
            // Sauvegarder le message
            ChatMessage savedMessage = chatMessageRepository.save(chatMessage);
            
            // Mettre à jour la conversation
            chat.setLastActivityAt(LocalDateTime.now());
            chat.setStatus("in_progress");
            chat.setHasUnreadMessages(true);
            chat.setAssignedAdminId(adminId);
            chat.setAssignedAdminName(adminName);
            chat.setMessageCount(chat.getMessageCount() + 1);
            
            chatRepository.save(chat);
            
            return savedMessage;
            
        } catch (Exception e) {
            throw new RuntimeException("Erreur lors de l'envoi de la réponse: " + e.getMessage());
        }
    }
    
    /**
     * Mettre à jour le statut d'une conversation
     */
    public Chat updateChatStatus(String chatId, String newStatus, String adminId, String adminName) {
        try {
            Optional<Chat> chatOpt = chatRepository.findById(chatId);
            if (!chatOpt.isPresent()) {
                throw new RuntimeException("Conversation non trouvée");
            }
            
            Chat chat = chatOpt.get();
            chat.setStatus(newStatus);
            chat.setLastActivityAt(LocalDateTime.now());
            chat.setUpdatedAt(LocalDateTime.now());
            
            if (adminId != null && adminName != null) {
                chat.setAssignedAdminId(adminId);
                chat.setAssignedAdminName(adminName);
            }
            
            return chatRepository.save(chat);
            
        } catch (Exception e) {
            throw new RuntimeException("Erreur lors de la mise à jour du statut: " + e.getMessage());
        }
    }
    
    /**
     * Récupérer les statistiques des conversations
     */
    public Map<String, Object> getChatStatistics(String adminDepartment, String adminLocation, String adminRole) {
        try {
            Map<String, Object> stats = new HashMap<>();
            
            // Construire le filtre de base
            Criteria baseCriteria = new Criteria();
            if (!"SUPERADMIN".equals(adminRole)) {
                List<Criteria> conditions = new ArrayList<>();
                if (adminDepartment != null) {
                    conditions.add(Criteria.where("targetDepartment").is(adminDepartment));
                }
                if (adminLocation != null) {
                    conditions.add(Criteria.where("targetLocation").is(adminLocation));
                }
                if (!conditions.isEmpty()) {
                    baseCriteria = baseCriteria.andOperator(conditions.toArray(new Criteria[0]));
                }
            }
            
            // Statistiques générales
            long totalChats = mongoTemplate.count(Query.query(baseCriteria), Chat.class);
            stats.put("totalConversations", totalChats);
            
            // Par statut
            Arrays.asList("open", "in_progress", "closed").forEach(status -> {
                Criteria statusCriteria = baseCriteria.and("status").is(status);
                long count = mongoTemplate.count(Query.query(statusCriteria), Chat.class);
                stats.put(status + "Conversations", count);
            });
            
            // Conversations avec messages non lus
            Criteria unreadCriteria = baseCriteria.and("hasUnreadMessages").is(true);
            long unreadCount = mongoTemplate.count(Query.query(unreadCriteria), Chat.class);
            stats.put("unreadConversations", unreadCount);
            
            // Conversations récentes (dernières 24h)
            LocalDateTime yesterday = LocalDateTime.now().minusDays(1);
            Criteria recentCriteria = baseCriteria.and("createdAt").gte(yesterday);
            long recentCount = mongoTemplate.count(Query.query(recentCriteria), Chat.class);
            stats.put("recentConversations", recentCount);
            
            return stats;
            
        } catch (Exception e) {
            System.err.println("Erreur calcul statistiques chat: " + e.getMessage());
            return new HashMap<>();
        }
    }
    
    /**
     * Vérifier si un admin peut accéder à une conversation
     */
    private boolean canAdminAccessChat(Chat chat, String adminDepartment, String adminLocation, String adminRole) {
        // SuperAdmin peut tout voir
        if ("SUPERADMIN".equals(adminRole)) {
            return true;
        }
        
        // Admin normal : vérifier département et location
        return Objects.equals(chat.getTargetDepartment(), adminDepartment) &&
               Objects.equals(chat.getTargetLocation(), adminLocation);
    }
    
    /**
     * Rechercher des conversations
     */
    public List<Chat> searchChats(String keyword, String adminDepartment, String adminLocation, String adminRole) {
        try {
            Criteria criteria = new Criteria();
            List<Criteria> conditions = new ArrayList<>();
            
            // Filtre de recherche textuelle
            conditions.add(new Criteria().orOperator(
                Criteria.where("subject").regex(keyword, "i"),
                Criteria.where("userName").regex(keyword, "i")
            ));
            
            // Filtrage selon le rôle
            if (!"SUPERADMIN".equals(adminRole)) {
                if (adminDepartment != null) {
                    conditions.add(Criteria.where("targetDepartment").is(adminDepartment));
                }
                if (adminLocation != null) {
                    conditions.add(Criteria.where("targetLocation").is(adminLocation));
                }
            }
            
            if (!conditions.isEmpty()) {
                criteria = criteria.andOperator(conditions.toArray(new Criteria[0]));
            }
            
            Query query = Query.query(criteria)
                .with(Sort.by(Sort.Direction.DESC, "lastActivityAt"))
                .limit(20);
            
            return mongoTemplate.find(query, Chat.class);
            
        } catch (Exception e) {
            System.err.println("Erreur recherche chats: " + e.getMessage());
            return new ArrayList<>();
        }
    }
}