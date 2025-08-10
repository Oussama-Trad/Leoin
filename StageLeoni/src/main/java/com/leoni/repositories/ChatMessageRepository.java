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
 * IMPORTANT: Les messages dans MongoDB utilisent 'chatRef' au lieu de 'chatId'
 */
@Repository
public interface ChatMessageRepository extends MongoRepository<ChatMessage, String> {
    
    // Messages d'une conversation, triés par date (utilise chatRef)
    @Query("{ 'chatRef': ?0 }")
    List<ChatMessage> findByChatRefOrderByCreatedAtAsc(String chatRef);
    
    // Messages d'une conversation avec pagination (utilise chatRef)
    @Query("{ 'chatRef': ?0 }")
    Page<ChatMessage> findByChatRefOrderByCreatedAtAsc(String chatRef, Pageable pageable);
    
    // Messages non lus d'une conversation (utilise chatRef)
    @Query("{ 'chatRef': ?0, 'isRead': false }")
    List<ChatMessage> findByChatRefAndIsReadFalseOrderByCreatedAtAsc(String chatRef);
    
    // Dernier message d'une conversation (utilise chatRef)
    @Query(value = "{ 'chatRef': ?0 }", sort = "{ 'createdAt': -1 }")
    ChatMessage findFirstByChatRefOrderByCreatedAtDesc(String chatRef);
    
    // Messages envoyés par un utilisateur spécifique
    List<ChatMessage> findBySenderIdOrderByCreatedAtDesc(String senderId);
    
    // Messages d'un type spécifique (admin, user, etc.) (utilise chatRef)
    @Query("{ 'chatRef': ?0, 'senderType': ?1 }")
    List<ChatMessage> findByChatRefAndSenderTypeOrderByCreatedAtAsc(String chatRef, String senderType);
    
    // Compter les messages non lus dans une conversation (utilise chatRef)
    @Query(value = "{ 'chatRef': ?0, 'isRead': false }", count = true)
    long countUnreadMessagesByChatRef(String chatRef);
    
    // Compter les messages non lus pour un utilisateur spécifique (utilise chatRef)
    @Query(value = "{ 'chatRef': ?0, 'isRead': false, 'senderId': { $ne: ?1 } }", count = true)
    long countUnreadMessagesForUser(String chatRef, String userId);
    
    // Messages créés dans une période (utilise chatRef)
    @Query("{ 'chatRef': ?0, 'createdAt': { $gte: ?1, $lte: ?2 } }")
    List<ChatMessage> findByChatRefAndCreatedAtBetween(
        String chatRef, LocalDateTime startDate, LocalDateTime endDate);
    
    // Messages modifiés (utilise chatRef)
    @Query("{ 'chatRef': ?0, 'isEdited': true }")
    List<ChatMessage> findByChatRefAndIsEditedTrueOrderByEditedAtDesc(String chatRef);
    
    // Recherche textuelle dans les messages (utilise chatRef)
    @Query("{ 'chatRef': ?0, 'message': { $regex: ?1, $options: 'i' } }")
    List<ChatMessage> findByChatRefAndMessageContainingIgnoreCase(String chatRef, String keyword);
    
    // Messages par type (texte, fichier, image) (utilise chatRef)
    @Query("{ 'chatRef': ?0, 'messageType': ?1 }")
    List<ChatMessage> findByChatRefAndMessageTypeOrderByCreatedAtAsc(String chatRef, String messageType);
    
    // Statistiques - messages par période pour un chat (utilise chatRef)
    @Query(value = "{ 'chatRef': ?0, 'createdAt': { $gte: ?1, $lte: ?2 } }", count = true)
    long countMessagesByChatRefAndDateRange(String chatRef, LocalDateTime startDate, LocalDateTime endDate);
    
    // Statistiques - messages par expéditeur dans un chat (utilise chatRef)
    @Query(value = "{ 'chatRef': ?0, 'senderId': ?1 }", count = true)
    long countMessagesByChatRefAndSenderId(String chatRef, String senderId);
    
    // Messages récents (dernières heures) (utilise chatRef)
    @Query("{ 'chatRef': ?0, 'createdAt': { $gte: ?1 } }")
    List<ChatMessage> findRecentMessagesByChatRef(String chatRef, LocalDateTime since);
    
    // Supprimer tous les messages d'une conversation (utilise chatRef)
    @Query(value = "{ 'chatRef': ?0 }", delete = true)
    void deleteByChatRef(String chatRef);
    
    // Messages non lus par type d'expéditeur (utilise chatRef)
    @Query("{ 'chatRef': ?0, 'senderType': ?1, 'isRead': false }")
    List<ChatMessage> findUnreadMessagesByChatRefAndSenderType(String chatRef, String senderType);
    
    // Marquer tous les messages comme lus (utilise chatRef)
    @Query("{ 'chatRef': ?0, 'isRead': false }")
    List<ChatMessage> findUnreadMessagesByChatRef(String chatRef);
}
