package com.leoni.services;

import com.leoni.models.Admin;
import com.leoni.models.Chat;
import com.leoni.models.ChatMessage;
import com.leoni.repositories.AdminRepository;
import com.leoni.repositories.ChatRepository;
import com.leoni.repositories.ChatMessageRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service pour la gestion des conversations et messages de chat
 */
@Service
public class ChatService {
    
    @Autowired
    private ChatRepository chatRepository;
    
    @Autowired
    private ChatMessageRepository chatMessageRepository;
    
    @Autowired
    private AdminRepository adminRepository;
    
    @Autowired
    private AccessControlService accessControlService;
    
    /**
     * Récupérer les conversations filtrées pour un admin
     */
    public Page<Chat> getFilteredChatsForAdmin(String adminId, int page, int size, String status) {
        Admin admin = adminRepository.findById(adminId).orElse(null);
        if (admin == null) {
            throw new RuntimeException("Admin non trouvé");
        }
        
        Pageable pageable = PageRequest.of(page, size);
        
        // Super admin voit tout
        if ("SUPERADMIN".equals(admin.getRole())) {
            if (status != null && !status.isEmpty()) {
                return chatRepository.findByStatusOrderByLastActivityAtDesc(status, pageable);
            } else {
                return chatRepository.findAllByOrderByLastActivityAtDesc(pageable);
            }
        }
        
        // Admin normal voit seulement son département/location
        String department = admin.getDepartment();
        String location = admin.getLocation();
        
        if (status != null && !status.isEmpty()) {
            return chatRepository.findByStatusAndTargetDepartmentAndTargetLocationOrderByLastActivityAtDesc(
                status, department, location, pageable);
        } else {
            return chatRepository.findByTargetDepartmentAndTargetLocationOrderByLastActivityAtDesc(
                department, location, pageable);
        }
    }
    
    /**
     * Récupérer une conversation avec ses messages
     */
    public Map<String, Object> getChatWithMessages(String chatId, String adminId) {
        Chat chat = chatRepository.findById(chatId).orElse(null);
        if (chat == null) {
            throw new RuntimeException("Conversation non trouvée");
        }
        
        // Vérifier les permissions d'accès
        if (!canAdminAccessChat(adminId, chat)) {
            throw new RuntimeException("Accès non autorisé à cette conversation");
        }
        
        // Récupérer les messages
        List<ChatMessage> messages = chatMessageRepository.findByChatIdOrderByCreatedAtAsc(chatId);
        
        // Marquer les messages comme lus pour l'admin
        markMessagesAsReadByAdmin(chatId, adminId);
        
        // Construire la réponse
        Map<String, Object> result = new HashMap<>();
        result.put("chat", chat);
        result.put("messages", messages);
        result.put("messageCount", messages.size());
        result.put("unreadCount", chatMessageRepository.countUnreadMessagesForUser(chatId, adminId));
        
        return result;
    }
    
    /**
     * Répondre à une conversation
     */
    public ChatMessage replyToChat(String chatId, String adminId, String message) {
        Chat chat = chatRepository.findById(chatId).orElse(null);
        if (chat == null) {
            throw new RuntimeException("Conversation non trouvée");
        }
        
        Admin admin = adminRepository.findById(adminId).orElse(null);
        if (admin == null) {
            throw new RuntimeException("Admin non trouvé");
        }
        
        // Vérifier les permissions
        if (!canAdminAccessChat(adminId, chat)) {
            throw new RuntimeException("Accès non autorisé à cette conversation");
        }
        
        // Créer le message de réponse
        ChatMessage chatMessage = new ChatMessage();
        chatMessage.setChatId(chatId);
        chatMessage.setSenderId(adminId);
        chatMessage.setSenderName(admin.getUsername());
        chatMessage.setSenderEmail(admin.getEmail());
        chatMessage.setSenderType("SUPERADMIN".equals(admin.getRole()) ? "superadmin" : "admin");
        chatMessage.setMessage(message);
        
        // Sauvegarder le message
        ChatMessage savedMessage = chatMessageRepository.save(chatMessage);
        
        // Mettre à jour la conversation
        chat.incrementMessageCount();
        chat.setHasUnreadMessages(true);
        chat.setStatus("in_progress");
        if (chat.getAssignedAdminId() == null) {
            chat.setAssignedAdminId(adminId);
            chat.setAssignedAdminName(admin.getUsername());
        }
        chatRepository.save(chat);
        
        return savedMessage;
    }
    
    /**
     * Changer le statut d'une conversation
     */
    public Chat updateChatStatus(String chatId, String adminId, String newStatus) {
        Chat chat = chatRepository.findById(chatId).orElse(null);
        if (chat == null) {
            throw new RuntimeException("Conversation non trouvée");
        }
        
        if (!canAdminAccessChat(adminId, chat)) {
            throw new RuntimeException("Accès non autorisé à cette conversation");
        }
        
        chat.setStatus(newStatus);
        chat.updateLastActivity();
        
        return chatRepository.save(chat);
    }
    
    /**
     * Assigner une conversation à un admin
     */
    public Chat assignChatToAdmin(String chatId, String adminId, String targetAdminId) {
        Chat chat = chatRepository.findById(chatId).orElse(null);
        if (chat == null) {
            throw new RuntimeException("Conversation non trouvée");
        }
        
        Admin currentAdmin = adminRepository.findById(adminId).orElse(null);
        Admin targetAdmin = adminRepository.findById(targetAdminId).orElse(null);
        
        if (currentAdmin == null || targetAdmin == null) {
            throw new RuntimeException("Admin non trouvé");
        }
        
        // Seuls les super admins peuvent réassigner ou les admins peuvent s'auto-assigner
        if (!"SUPERADMIN".equals(currentAdmin.getRole()) && !adminId.equals(targetAdminId)) {
            throw new RuntimeException("Permission insuffisante pour cette action");
        }
        
        chat.setAssignedAdminId(targetAdminId);
        chat.setAssignedAdminName(targetAdmin.getUsername());
        chat.updateLastActivity();
        
        return chatRepository.save(chat);
    }
    
    /**
     * Statistiques des conversations pour un admin
     */
    public Map<String, Object> getChatStatistics(String adminId) {
        Admin admin = adminRepository.findById(adminId).orElse(null);
        if (admin == null) {
            throw new RuntimeException("Admin non trouvé");
        }
        
        Map<String, Object> stats = new HashMap<>();
        
        if ("SUPERADMIN".equals(admin.getRole())) {
            // Statistiques globales pour super admin
            stats.put("totalChats", chatRepository.count());
            stats.put("activeChats", chatRepository.countActiveChats());
            stats.put("unreadChats", chatRepository.findByHasUnreadMessagesTrue().size());
            
            // Statistiques par statut
            stats.put("openChats", chatRepository.findByStatusOrderByLastActivityAtDesc("open", PageRequest.of(0, 1)).getTotalElements());
            stats.put("inProgressChats", chatRepository.findByStatusOrderByLastActivityAtDesc("in_progress", PageRequest.of(0, 1)).getTotalElements());
            stats.put("closedChats", chatRepository.findByStatusOrderByLastActivityAtDesc("closed", PageRequest.of(0, 1)).getTotalElements());
            
        } else {
            // Statistiques pour admin normal
            String department = admin.getDepartment();
            String location = admin.getLocation();
            
            Page<Chat> allChats = chatRepository.findByTargetDepartmentAndTargetLocationOrderByLastActivityAtDesc(
                department, location, PageRequest.of(0, 1));
            stats.put("totalChats", allChats.getTotalElements());
            stats.put("activeChats", chatRepository.countActiveChatsByDepartmentAndLocation(department, location));
            stats.put("unreadChats", chatRepository.findUnreadChatsByDepartmentAndLocation(department, location).size());
            
            // Chats assignés à cet admin
            stats.put("assignedChats", chatRepository.findByAssignedAdminIdOrderByLastActivityAtDesc(adminId).size());
        }
        
        // Statistiques temporelles (dernières 24h, 7 jours, 30 jours)
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime yesterday = now.minusDays(1);
        LocalDateTime lastWeek = now.minusDays(7);
        LocalDateTime lastMonth = now.minusDays(30);
        
        if ("SUPERADMIN".equals(admin.getRole())) {
            stats.put("chatsLast24h", chatRepository.findRecentChats(yesterday).size());
            stats.put("chatsLastWeek", chatRepository.findByCreatedAtBetween(lastWeek, now).size());
            stats.put("chatsLastMonth", chatRepository.findByCreatedAtBetween(lastMonth, now).size());
        } else {
            String department = admin.getDepartment();
            String location = admin.getLocation();
            stats.put("chatsLast24h", chatRepository.findRecentChatsByDepartmentAndLocation(yesterday, department, location).size());
            stats.put("chatsLastWeek", chatRepository.findByCreatedAtBetweenAndTargetDepartmentAndTargetLocation(lastWeek, now, department, location).size());
            stats.put("chatsLastMonth", chatRepository.findByCreatedAtBetweenAndTargetDepartmentAndTargetLocation(lastMonth, now, department, location).size());
        }
        
        return stats;
    }
    
    /**
     * Rechercher des conversations
     */
    public List<Chat> searchChats(String adminId, String keyword) {
        Admin admin = adminRepository.findById(adminId).orElse(null);
        if (admin == null) {
            throw new RuntimeException("Admin non trouvé");
        }
        
        if ("SUPERADMIN".equals(admin.getRole())) {
            return chatRepository.findBySubjectContainingIgnoreCase(keyword);
        } else {
            return chatRepository.findBySubjectContainingIgnoreCaseAndTargetDepartmentAndTargetLocation(
                keyword, admin.getDepartment(), admin.getLocation());
        }
    }
    
    /**
     * Vérifier si un admin peut accéder à une conversation
     */
    private boolean canAdminAccessChat(String adminId, Chat chat) {
        Admin admin = adminRepository.findById(adminId).orElse(null);
        if (admin == null) {
            return false;
        }
        
        // Super admin peut tout voir
        if ("SUPERADMIN".equals(admin.getRole())) {
            return true;
        }
        
        // Admin normal peut voir seulement son département/location
        return admin.getDepartment().equals(chat.getTargetDepartment()) &&
               admin.getLocation().equals(chat.getTargetLocation());
    }
    
    /**
     * Marquer les messages comme lus par un admin
     */
    private void markMessagesAsReadByAdmin(String chatId, String adminId) {
        List<ChatMessage> unreadMessages = chatMessageRepository.findUnreadMessagesByChatId(chatId);
        for (ChatMessage message : unreadMessages) {
            if (!message.getSenderId().equals(adminId)) {
                message.markAsRead(adminId);
                chatMessageRepository.save(message);
            }
        }
        
        // Mettre à jour le statut de lecture du chat
        Chat chat = chatRepository.findById(chatId).orElse(null);
        if (chat != null) {
            long remainingUnread = chatMessageRepository.countUnreadMessagesByChatId(chatId);
            chat.setHasUnreadMessages(remainingUnread > 0);
            chatRepository.save(chat);
        }
    }
}
