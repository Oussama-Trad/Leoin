package com.leoni.repositories;

import com.leoni.models.ChatMessage;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Repository pour la gestion des messages de chat
 */
@Repository
public interface ChatMessageRepository extends MongoRepository<ChatMessage, String> {
    
    // Messages d'une conversation, triés par date
    List<ChatMessage> findByChatIdOrderByCreatedAtAsc(String chatId);
    
    // Messages d'une conversation avec pagination
    Page<ChatMessage> findByChatIdOrderByCreatedAtAsc(String chatId, Pageable pageable);
    
    // Messages non lus d'une conversation
    List<ChatMessage> findByChatIdAndIsReadFalseOrderByCreatedAtAsc(String chatId);
    
    // Dernier message d'une conversation
    ChatMessage findFirstByChatIdOrderByCreatedAtDesc(String chatId);
    
    // Messages envoyés par un utilisateur spécifique
    List<ChatMessage> findBySenderIdOrderByCreatedAtDesc(String senderId);
    
    // Messages d'un type spécifique (admin, user, etc.)
    List<ChatMessage> findByChatIdAndSenderTypeOrderByCreatedAtAsc(String chatId, String senderType);
    
    // Compter les messages non lus dans une conversation
    @Query(value = "{ 'chatId': ?0, 'isRead': false }", count = true)
    long countUnreadMessagesByChatId(String chatId);
    
    // Compter les messages non lus pour un utilisateur spécifique
    @Query(value = "{ 'chatId': ?0, 'isRead': false, 'senderId': { $ne: ?1 } }", count = true)
    long countUnreadMessagesForUser(String chatId, String userId);
    
    // Messages créés dans une période
    @Query("{ 'chatId': ?0, 'createdAt': { $gte: ?1, $lte: ?2 } }")
    List<ChatMessage> findByChatIdAndCreatedAtBetween(
        String chatId, LocalDateTime startDate, LocalDateTime endDate);
    
    // Messages modifiés
    List<ChatMessage> findByChatIdAndIsEditedTrueOrderByEditedAtDesc(String chatId);
    
    // Recherche textuelle dans les messages
    @Query("{ 'chatId': ?0, 'message': { $regex: ?1, $options: 'i' } }")
    List<ChatMessage> findByChatIdAndMessageContainingIgnoreCase(String chatId, String keyword);
    
    // Messages par type (texte, fichier, image)
    List<ChatMessage> findByChatIdAndMessageTypeOrderByCreatedAtAsc(String chatId, String messageType);
    
    // Statistiques - messages par période pour un chat
    @Query(value = "{ 'chatId': ?0, 'createdAt': { $gte: ?1, $lte: ?2 } }", count = true)
    long countMessagesByChatIdAndDateRange(String chatId, LocalDateTime startDate, LocalDateTime endDate);
    
    // Statistiques - messages par expéditeur dans un chat
    @Query(value = "{ 'chatId': ?0, 'senderId': ?1 }", count = true)
    long countMessagesByChatIdAndSenderId(String chatId, String senderId);
    
    // Messages récents (dernières heures)
    @Query("{ 'chatId': ?0, 'createdAt': { $gte: ?1 } }")
    List<ChatMessage> findRecentMessagesByChatId(String chatId, LocalDateTime since);
    
    // Supprimer tous les messages d'une conversation
    void deleteByChatId(String chatId);
    
    // Messages non lus par type d'expéditeur
    @Query("{ 'chatId': ?0, 'senderType': ?1, 'isRead': false }")
    List<ChatMessage> findUnreadMessagesByChatIdAndSenderType(String chatId, String senderType);
    
    // Marquer tous les messages comme lus
    @Query("{ 'chatId': ?0, 'isRead': false }")
    List<ChatMessage> findUnreadMessagesByChatId(String chatId);
}
