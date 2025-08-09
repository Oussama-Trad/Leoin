package com.leoni.models;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Modèle pour les conversations de chat
 * Correspond à la collection 'chats' dans MongoDB
 */
@Document(collection = "chats")
public class Chat {
    
    @Id
    private String id;
    
    private String userId;
    private String userName;
    private String userEmail;
    private String userDepartment;
    private String userLocation;
    
    private String subject;
    private String status; // "open", "in_progress", "closed"
    
    private String targetDepartment;
    private String targetLocation;
    
    private String assignedAdminId;
    private String assignedAdminName;
    
    private LocalDateTime createdAt;
    private LocalDateTime lastActivityAt;
    private LocalDateTime updatedAt;
    
    private int messageCount;
    private boolean hasUnreadMessages;
    private String priority; // "low", "medium", "high", "urgent"
    
    // Constructeurs
    public Chat() {
        this.createdAt = LocalDateTime.now();
        this.lastActivityAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.status = "open";
        this.messageCount = 0;
        this.hasUnreadMessages = false;
        this.priority = "medium";
    }
    
    // Getters et Setters
    public String getId() {
        return id;
    }
    
    public void setId(String id) {
        this.id = id;
    }
    
    public String getUserId() {
        return userId;
    }
    
    public void setUserId(String userId) {
        this.userId = userId;
    }
    
    public String getUserName() {
        return userName;
    }
    
    public void setUserName(String userName) {
        this.userName = userName;
    }
    
    public String getUserEmail() {
        return userEmail;
    }
    
    public void setUserEmail(String userEmail) {
        this.userEmail = userEmail;
    }
    
    public String getUserDepartment() {
        return userDepartment;
    }
    
    public void setUserDepartment(String userDepartment) {
        this.userDepartment = userDepartment;
    }
    
    public String getUserLocation() {
        return userLocation;
    }
    
    public void setUserLocation(String userLocation) {
        this.userLocation = userLocation;
    }
    
    public String getSubject() {
        return subject;
    }
    
    public void setSubject(String subject) {
        this.subject = subject;
    }
    
    public String getStatus() {
        return status;
    }
    
    public void setStatus(String status) {
        this.status = status;
    }
    
    public String getTargetDepartment() {
        return targetDepartment;
    }
    
    public void setTargetDepartment(String targetDepartment) {
        this.targetDepartment = targetDepartment;
    }
    
    public String getTargetLocation() {
        return targetLocation;
    }
    
    public void setTargetLocation(String targetLocation) {
        this.targetLocation = targetLocation;
    }
    
    public String getAssignedAdminId() {
        return assignedAdminId;
    }
    
    public void setAssignedAdminId(String assignedAdminId) {
        this.assignedAdminId = assignedAdminId;
    }
    
    public String getAssignedAdminName() {
        return assignedAdminName;
    }
    
    public void setAssignedAdminName(String assignedAdminName) {
        this.assignedAdminName = assignedAdminName;
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    public LocalDateTime getLastActivityAt() {
        return lastActivityAt;
    }
    
    public void setLastActivityAt(LocalDateTime lastActivityAt) {
        this.lastActivityAt = lastActivityAt;
    }
    
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    
    public int getMessageCount() {
        return messageCount;
    }
    
    public void setMessageCount(int messageCount) {
        this.messageCount = messageCount;
    }
    
    public boolean isHasUnreadMessages() {
        return hasUnreadMessages;
    }
    
    public void setHasUnreadMessages(boolean hasUnreadMessages) {
        this.hasUnreadMessages = hasUnreadMessages;
    }
    
    public String getPriority() {
        return priority;
    }
    
    public void setPriority(String priority) {
        this.priority = priority;
    }
    
    // Méthodes utilitaires
    public void updateLastActivity() {
        this.lastActivityAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
    
    public void incrementMessageCount() {
        this.messageCount++;
        updateLastActivity();
    }
    
    public boolean isActive() {
        return "open".equals(status) || "in_progress".equals(status);
    }
    
    @Override
    public String toString() {
        return "Chat{" +
                "id='" + id + '\'' +
                ", userId='" + userId + '\'' +
                ", subject='" + subject + '\'' +
                ", status='" + status + '\'' +
                ", targetDepartment='" + targetDepartment + '\'' +
                ", targetLocation='" + targetLocation + '\'' +
                ", messageCount=" + messageCount +
                ", createdAt=" + createdAt +
                '}';
    }
}
