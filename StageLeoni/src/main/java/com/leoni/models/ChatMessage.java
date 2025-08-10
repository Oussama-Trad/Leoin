package com.leoni.models;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;

/**
 * Modèle pour les messages de chat
 * Correspond à la collection 'chat_messages' dans MongoDB
 */
@Document(collection = "chat_messages")
public class ChatMessage {
    
    @Id
    private String id;
    
    private String chatRef; // IMPORTANT: Correspond au 'chatRef' dans MongoDB
    private String senderId;
    private String senderName;
    private String senderEmail;
    private String senderType; // "user", "admin", "superadmin"
    
    private String message;
    private String messageType; // "text", "file", "image"
    
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    private boolean isRead;
    private LocalDateTime readAt;
    private String readBy;
    
    private boolean isEdited;
    private LocalDateTime editedAt;
    private String originalMessage;
    
    // Constructeurs
    public ChatMessage() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.messageType = "text";
        this.isRead = false;
        this.isEdited = false;
    }
    
    public ChatMessage(String chatRef, String senderId, String senderName, String message) {
        this();
        this.chatRef = chatRef;
        this.senderId = senderId;
        this.senderName = senderName;
        this.message = message;
    }
    
    // Getters et Setters
    public String getId() {
        return id;
    }
    
    public void setId(String id) {
        this.id = id;
    }
    
    public String getChatRef() {
        return chatRef;
    }
    
    public void setChatRef(String chatRef) {
        this.chatRef = chatRef;
    }
    
    public String getSenderId() {
        return senderId;
    }
    
    public void setSenderId(String senderId) {
        this.senderId = senderId;
    }
    
    public String getSenderName() {
        return senderName;
    }
    
    public void setSenderName(String senderName) {
        this.senderName = senderName;
    }
    
    public String getSenderEmail() {
        return senderEmail;
    }
    
    public void setSenderEmail(String senderEmail) {
        this.senderEmail = senderEmail;
    }
    
    public String getSenderType() {
        return senderType;
    }
    
    public void setSenderType(String senderType) {
        this.senderType = senderType;
    }
    
    public String getMessage() {
        return message;
    }
    
    public void setMessage(String message) {
        this.message = message;
    }
    
    public String getMessageType() {
        return messageType;
    }
    
    public void setMessageType(String messageType) {
        this.messageType = messageType;
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    
    public boolean isRead() {
        return isRead;
    }
    
    public void setRead(boolean read) {
        isRead = read;
    }
    
    public LocalDateTime getReadAt() {
        return readAt;
    }
    
    public void setReadAt(LocalDateTime readAt) {
        this.readAt = readAt;
    }
    
    public String getReadBy() {
        return readBy;
    }
    
    public void setReadBy(String readBy) {
        this.readBy = readBy;
    }
    
    public boolean isEdited() {
        return isEdited;
    }
    
    public void setEdited(boolean edited) {
        isEdited = edited;
    }
    
    public LocalDateTime getEditedAt() {
        return editedAt;
    }
    
    public void setEditedAt(LocalDateTime editedAt) {
        this.editedAt = editedAt;
    }
    
    public String getOriginalMessage() {
        return originalMessage;
    }
    
    public void setOriginalMessage(String originalMessage) {
        this.originalMessage = originalMessage;
    }
    
    // Méthodes utilitaires
    public void markAsRead(String readerId) {
        this.isRead = true;
        this.readAt = LocalDateTime.now();
        this.readBy = readerId;
        this.updatedAt = LocalDateTime.now();
    }
    
    public void editMessage(String newMessage) {
        if (this.message != null && !this.message.equals(newMessage)) {
            this.originalMessage = this.message;
            this.message = newMessage;
            this.isEdited = true;
            this.editedAt = LocalDateTime.now();
            this.updatedAt = LocalDateTime.now();
        }
    }
    
    public boolean isFromAdmin() {
        return "admin".equals(senderType) || "superadmin".equals(senderType);
    }
    
    public boolean isFromUser() {
        return "user".equals(senderType);
    }
    
    @Override
    public String toString() {
        return "ChatMessage{" +
                "id='" + id + '\'' +
                ", chatRef='" + chatRef + '\'' +
                ", senderId='" + senderId + '\'' +
                ", senderName='" + senderName + '\'' +
                ", senderType='" + senderType + '\'' +
                ", message='" + message + '\'' +
                ", createdAt=" + createdAt +
                ", isRead=" + isRead +
                '}';
    }
}
