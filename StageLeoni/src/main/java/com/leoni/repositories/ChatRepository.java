package com.leoni.repositories;

import com.leoni.models.Chat;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Repository pour la gestion des conversations de chat
 */
@Repository
public interface ChatRepository extends MongoRepository<Chat, String> {
    
    // Recherche par utilisateur
    List<Chat> findByUserIdOrderByLastActivityAtDesc(String userId);
    
    // Recherche par département et location (pour les admins)
    @Query("{ 'targetDepartment': ?0, 'targetLocation': ?1 }")
    Page<Chat> findByTargetDepartmentAndTargetLocationOrderByLastActivityAtDesc(
        String department, String location, Pageable pageable);
    
    // Recherche pour les super admins (tous les chats)
    Page<Chat> findAllByOrderByLastActivityAtDesc(Pageable pageable);
    
    // Recherche par statut
    @Query("{ 'status': ?0, 'targetDepartment': ?1, 'targetLocation': ?2 }")
    Page<Chat> findByStatusAndTargetDepartmentAndTargetLocationOrderByLastActivityAtDesc(
        String status, String department, String location, Pageable pageable);
    
    // Recherche par statut pour super admin
    Page<Chat> findByStatusOrderByLastActivityAtDesc(String status, Pageable pageable);
    
    // Recherche par admin assigné
    List<Chat> findByAssignedAdminIdOrderByLastActivityAtDesc(String adminId);
    
    // Chats avec messages non lus
    @Query("{ 'hasUnreadMessages': true, 'targetDepartment': ?0, 'targetLocation': ?1 }")
    List<Chat> findUnreadChatsByDepartmentAndLocation(String department, String location);
    
    // Chats avec messages non lus pour super admin
    List<Chat> findByHasUnreadMessagesTrue();
    
    // Statistiques par période
    @Query("{ 'createdAt': { $gte: ?0, $lte: ?1 }, 'targetDepartment': ?2, 'targetLocation': ?3 }")
    List<Chat> findByCreatedAtBetweenAndTargetDepartmentAndTargetLocation(
        LocalDateTime startDate, LocalDateTime endDate, String department, String location);
    
    // Statistiques globales pour super admin
    @Query("{ 'createdAt': { $gte: ?0, $lte: ?1 } }")
    List<Chat> findByCreatedAtBetween(LocalDateTime startDate, LocalDateTime endDate);
    
    // Compter les chats actifs par département/location
    @Query(value = "{ 'status': { $in: ['open', 'in_progress'] }, 'targetDepartment': ?0, 'targetLocation': ?1 }", count = true)
    long countActiveChatsByDepartmentAndLocation(String department, String location);
    
    // Compter tous les chats actifs
    @Query(value = "{ 'status': { $in: ['open', 'in_progress'] } }", count = true)
    long countActiveChats();
    
    // Recherche par priorité
    @Query("{ 'priority': ?0, 'targetDepartment': ?1, 'targetLocation': ?2 }")
    List<Chat> findByPriorityAndTargetDepartmentAndTargetLocation(
        String priority, String department, String location);
    
    // Recherche textuelle dans le sujet
    @Query("{ 'subject': { $regex: ?0, $options: 'i' }, 'targetDepartment': ?1, 'targetLocation': ?2 }")
    List<Chat> findBySubjectContainingIgnoreCaseAndTargetDepartmentAndTargetLocation(
        String keyword, String department, String location);
    
    // Recherche textuelle pour super admin
    @Query("{ 'subject': { $regex: ?0, $options: 'i' } }")
    List<Chat> findBySubjectContainingIgnoreCase(String keyword);
    
    // Chats récents (dernières 24h) par département/location
    @Query("{ 'createdAt': { $gte: ?0 }, 'targetDepartment': ?1, 'targetLocation': ?2 }")
    List<Chat> findRecentChatsByDepartmentAndLocation(
        LocalDateTime since, String department, String location);
    
    // Tous les chats récents pour super admin
    @Query("{ 'createdAt': { $gte: ?0 } }")
    List<Chat> findRecentChats(LocalDateTime since);
}
