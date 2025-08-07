/**
 * Chat Model - Data structure and validation for chat functionality
 */
class ChatModel {
  constructor(data = {}) {
    this.id = data.id || null;
    this.subject = data.subject || '';
    this.serviceName = data.serviceName || '';
    this.status = data.status || 'pending';
    this.priority = data.priority || 'normal';
    this.messageCount = data.messageCount || 0;
    this.lastMessage = data.lastMessage || null;
    this.createdAt = data.createdAt || null;
    this.lastActivityAt = data.lastActivityAt || null;
    this.rating = data.rating || { score: null, feedback: null, ratedAt: null };
  }

  /**
   * Chat status types
   */
  static STATUS_TYPES = {
    pending: 'En attente',
    active: 'Actif',
    resolved: 'Résolu',
    closed: 'Fermé'
  };

  /**
   * Priority levels
   */
  static PRIORITY_LEVELS = {
    low: 'Faible',
    normal: 'Normal',
    high: 'Élevé',
    urgent: 'Urgent'
  };

  /**
   * Get status color for UI
   */
  getStatusColor() {
    const colors = {
      pending: '#F59E0B',    // Orange
      active: '#10B981',     // Green
      resolved: '#3B82F6',   // Blue
      closed: '#6B7280'      // Gray
    };
    return colors[this.status] || colors.pending;
  }

  /**
   * Get priority color for UI
   */
  getPriorityColor() {
    const colors = {
      low: '#10B981',      // Green
      normal: '#3B82F6',   // Blue
      high: '#F59E0B',     // Orange
      urgent: '#EF4444'    // Red
    };
    return colors[this.priority] || colors.normal;
  }

  /**
   * Get formatted date
   */
  getFormattedDate(dateField = 'lastActivityAt') {
    const dateValue = this[dateField];
    if (!dateValue) return '';
    
    const date = new Date(dateValue);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffMinutes = Math.floor(diffTime / (1000 * 60));
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffMinutes < 1) return 'À l\'instant';
    if (diffMinutes < 60) return `Il y a ${diffMinutes} min`;
    if (diffHours < 24) return `Il y a ${diffHours}h`;
    if (diffDays < 7) return `Il y a ${diffDays} jours`;
    
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short'
    });
  }

  /**
   * Check if chat is active
   */
  isActive() {
    return this.status === 'active';
  }

  /**
   * Check if chat can receive messages
   */
  canSendMessages() {
    return this.status === 'active' || this.status === 'pending';
  }

  /**
   * Check if chat can be rated
   */
  canBeRated() {
    return this.status === 'resolved' && !this.rating.score;
  }

  /**
   * Get last message preview
   */
  getLastMessagePreview(maxLength = 50) {
    if (!this.lastMessage || !this.lastMessage.text) {
      return 'Aucun message';
    }
    
    const text = this.lastMessage.text;
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }

  /**
   * Validate chat creation data
   */
  static validateChatCreation(data) {
    const errors = [];

    if (!data.serviceId || data.serviceId.trim() === '') {
      errors.push('Le service est requis');
    }

    if (!data.subject || data.subject.trim().length < 5) {
      errors.push('Le sujet doit contenir au moins 5 caractères');
    }

    if (data.subject && data.subject.length > 200) {
      errors.push('Le sujet ne peut pas dépasser 200 caractères');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Create from API response
   */
  static fromApiResponse(apiData) {
    return new ChatModel({
      id: apiData.id,
      subject: apiData.subject,
      serviceName: apiData.serviceName,
      status: apiData.status,
      priority: apiData.priority,
      messageCount: apiData.messageCount,
      lastMessage: apiData.lastMessage,
      createdAt: apiData.createdAt,
      lastActivityAt: apiData.lastActivityAt,
      rating: apiData.rating
    });
  }

  /**
   * Convert to display object
   */
  toDisplayObject() {
    return {
      id: this.id,
      subject: this.subject,
      serviceName: this.serviceName,
      status: this.status,
      statusLabel: ChatModel.STATUS_TYPES[this.status],
      statusColor: this.getStatusColor(),
      priority: this.priority,
      priorityLabel: ChatModel.PRIORITY_LEVELS[this.priority],
      priorityColor: this.getPriorityColor(),
      messageCount: this.messageCount,
      lastMessage: this.lastMessage,
      lastMessagePreview: this.getLastMessagePreview(),
      createdAt: this.createdAt,
      lastActivityAt: this.lastActivityAt,
      formattedDate: this.getFormattedDate(),
      rating: this.rating,
      isActive: this.isActive(),
      canSendMessages: this.canSendMessages(),
      canBeRated: this.canBeRated()
    };
  }
}

/**
 * Chat Message Model
 */
class ChatMessageModel {
  constructor(data = {}) {
    this.id = data.id || null;
    this.senderId = data.senderId || null;
    this.senderName = data.senderName || '';
    this.senderRole = data.senderRole || 'employee';
    this.message = data.message || { text: '', type: 'text' };
    this.status = data.status || 'sent';
    this.isSystemMessage = data.isSystemMessage || false;
    this.createdAt = data.createdAt || null;
  }

  /**
   * Message status types
   */
  static STATUS_TYPES = {
    sent: 'Envoyé',
    delivered: 'Livré',
    read: 'Lu'
  };

  /**
   * Sender role types
   */
  static SENDER_ROLES = {
    employee: 'Employé',
    service_rep: 'Service',
    system: 'Système'
  };

  /**
   * Check if message is from current user
   */
  isFromCurrentUser(currentUserId) {
    return this.senderId === currentUserId;
  }

  /**
   * Get formatted time
   */
  getFormattedTime() {
    if (!this.createdAt) return '';
    
    const date = new Date(this.createdAt);
    return date.toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  /**
   * Get sender role color
   */
  getSenderRoleColor() {
    const colors = {
      employee: '#3B82F6',     // Blue
      service_rep: '#10B981',  // Green
      system: '#6B7280'        // Gray
    };
    return colors[this.senderRole] || colors.employee;
  }

  /**
   * Validate message data
   */
  static validate(data) {
    const errors = [];

    if (!data.message || data.message.trim() === '') {
      errors.push('Le message ne peut pas être vide');
    }

    if (data.message && data.message.length > 1000) {
      errors.push('Le message ne peut pas dépasser 1000 caractères');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Create from API response
   */
  static fromApiResponse(apiData) {
    return new ChatMessageModel({
      id: apiData.id,
      senderId: apiData.senderId,
      senderName: apiData.senderName,
      senderRole: apiData.senderRole,
      message: apiData.message,
      status: apiData.status,
      isSystemMessage: apiData.isSystemMessage,
      createdAt: apiData.createdAt
    });
  }

  /**
   * Convert to display object
   */
  toDisplayObject() {
    return {
      id: this.id,
      senderId: this.senderId,
      senderName: this.senderName,
      senderRole: this.senderRole,
      senderRoleLabel: ChatMessageModel.SENDER_ROLES[this.senderRole],
      senderRoleColor: this.getSenderRoleColor(),
      message: this.message,
      status: this.status,
      statusLabel: ChatMessageModel.STATUS_TYPES[this.status],
      isSystemMessage: this.isSystemMessage,
      createdAt: this.createdAt,
      formattedTime: this.getFormattedTime()
    };
  }
}

/**
 * Service Model
 */
class ServiceModel {
  constructor(data = {}) {
    this.id = data.id || null;
    this.name = data.name || '';
    this.code = data.code || '';
    this.description = data.description || '';
    this.stats = data.stats || {};
    this.settings = data.settings || {};
  }

  /**
   * Get response time in human format
   */
  getFormattedResponseTime() {
    const minutes = this.settings.averageResponseTime || 0;
    
    if (minutes < 60) {
      return `${minutes} min`;
    }
    
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    
    if (remainingMinutes === 0) {
      return `${hours}h`;
    }
    
    return `${hours}h ${remainingMinutes}min`;
  }

  /**
   * Get service icon based on code
   */
  getServiceIcon() {
    const icons = {
      HR_SUPPORT: 'people-outline',
      IT_HELPDESK: 'desktop-outline',
      MAINTENANCE: 'construct-outline',
      SECURITY: 'shield-checkmark-outline'
    };
    return icons[this.code] || 'help-circle-outline';
  }

  /**
   * Create from API response
   */
  static fromApiResponse(apiData) {
    return new ServiceModel({
      id: apiData.id,
      name: apiData.name,
      code: apiData.code,
      description: apiData.description,
      stats: apiData.stats,
      settings: apiData.settings
    });
  }

  /**
   * Convert to display object
   */
  toDisplayObject() {
    return {
      id: this.id,
      name: this.name,
      code: this.code,
      description: this.description,
      stats: this.stats,
      settings: this.settings,
      formattedResponseTime: this.getFormattedResponseTime(),
      serviceIcon: this.getServiceIcon()
    };
  }
}

export { ChatModel, ChatMessageModel, ServiceModel };
export default ChatModel;
