/**
 * News Model - Data structure simplifiée pour le nouveau système de news
 */
class NewsModel {
  constructor(data = {}) {
    this.id = data.id || data._id || null;
    this.title = data.title || '';
    this.description = data.description || '';
    this.content = data.content || '';
    this.photos = data.photos || [];
    this.authorName = data.authorName || '';
    this.publishedAt = data.publishedAt || null;
    this.priority = data.priority || 'normal';
    this.category = data.category || 'general';
    this.targetLocation = data.targetLocation || null;
    this.targetDepartment = data.targetDepartment || null;
    this.isActive = data.isActive !== undefined ? data.isActive : true;
  }

  /**
   * Priority levels for news
   */
  static PRIORITY_LEVELS = {
    low: 'Faible',
    normal: 'Normal',
    high: 'Élevé', 
    urgent: 'Urgent'
  };

  /**
   * News categories
   */
  static CATEGORIES = {
    general: 'Général',
    announcement: 'Annonce',
    training: 'Formation',
    safety: 'Sécurité'
  };

  /**
   * Get formatted published date
   */
  getFormattedDate() {
    if (!this.publishedAt) return '';
    
    const date = new Date(this.publishedAt);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
      return 'À l\'instant';
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `Il y a ${minutes} minute${minutes > 1 ? 's' : ''}`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `Il y a ${hours} heure${hours > 1 ? 's' : ''}`;
    } else if (diffInSeconds < 604800) {
      const days = Math.floor(diffInSeconds / 86400);
      return `Il y a ${days} jour${days > 1 ? 's' : ''}`;
    } else {
      return date.toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
    }
  }

  /**
   * Get priority display name
   */
  getPriorityDisplay() {
    return NewsModel.PRIORITY_LEVELS[this.priority] || 'Normal';
  }

  /**
   * Get category display name
   */
  getCategoryDisplay() {
    return NewsModel.CATEGORIES[this.category] || 'Général';
  }

  /**
   * Get priority color for UI
   */
  getPriorityColor() {
    const colors = {
      low: '#10B981',     // Green
      normal: '#3B82F6',  // Blue
      high: '#F59E0B',    // Amber
      urgent: '#EF4444'   // Red
    };
    return colors[this.priority] || colors.normal;
  }

  /**
   * Check if news has photos
   */
  hasPhotos() {
    return this.photos && this.photos.length > 0;
  }

  /**
   * Get targeting info for display
   */
  getTargetingInfo() {
    if (!this.targetLocation && !this.targetDepartment) {
      return 'Tous les employés';
    } else if (this.targetLocation && !this.targetDepartment) {
      return `Tous les employés de ${this.targetLocation}`;
    } else if (!this.targetLocation && this.targetDepartment) {
      return `Tous les employés ${this.targetDepartment}`;
    } else {
      return `Employés ${this.targetDepartment} de ${this.targetLocation}`;
    }
  }

  /**
   * Validate news data
   */
  static validate(data) {
    const errors = [];

    if (!data.title || data.title.trim().length === 0) {
      errors.push('Le titre est obligatoire');
    }

    if (data.title && data.title.length > 200) {
      errors.push('Le titre ne peut pas dépasser 200 caractères');
    }

    if (!data.description || data.description.trim().length === 0) {
      errors.push('La description est obligatoire');
    }

    if (data.description && data.description.length > 500) {
      errors.push('La description ne peut pas dépasser 500 caractères');
    }

    if (data.priority && !Object.keys(NewsModel.PRIORITY_LEVELS).includes(data.priority)) {
      errors.push('Priorité invalide');
    }

    if (data.category && !Object.keys(NewsModel.CATEGORIES).includes(data.category)) {
      errors.push('Catégorie invalide');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Convert to API object
   */
  toApiObject() {
    return {
      title: this.title,
      description: this.description,
      content: this.content,
      photos: this.photos,
      priority: this.priority,
      category: this.category,
      targetLocation: this.targetLocation,
      targetDepartment: this.targetDepartment,
      isActive: this.isActive
    };
  }

  /**
   * Create from API response
   */
  static fromApiResponse(apiData) {
    return new NewsModel({
      id: apiData._id || apiData.id,
      title: apiData.title,
      description: apiData.description,
      content: apiData.content,
      photos: apiData.photos,
      authorName: apiData.authorName,
      publishedAt: apiData.publishedAt,
      priority: apiData.priority,
      category: apiData.category,
      targetLocation: apiData.targetLocation,
      targetDepartment: apiData.targetDepartment,
      isActive: apiData.isActive
    });
  }

  /**
   * Create array from API response
   */
  static fromApiArray(apiArray) {
    return apiArray.map(item => NewsModel.fromApiResponse(item));
  }
}

export default NewsModel;
